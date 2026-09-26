"""CMS FY 2026 hospital-condition analysis. Python 3.11+; standard library only.

The source contains published, risk-standardized ratios, not patient-level data.
No national patient readmission rate or penalty is estimated by this project.
"""
from collections import Counter
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sqlite3
import statistics

ROOT = Path(__file__).resolve().parent
MEASURES = {
    'READM-30-HF-HRRP': 'Heart failure',
    'READM-30-COPD-HRRP': 'COPD',
    'READM-30-PN-HRRP': 'Pneumonia',
    'READM-30-AMI-HRRP': 'Heart attack',
    'READM-30-CABG-HRRP': 'Coronary bypass',
    'READM-30-HIP-KNEE-HRRP': 'Hip / knee replacement',
}
THRESHOLDS = [0, 25, 100, 250]


def number(value, integer=False):
    """N/A is missing; zero is numeric. Reject unrecognized source tokens."""
    if value == 'N/A':
        return None
    n = float(value)
    if not math.isfinite(n) or n < 0 or (integer and not n.is_integer()):
        raise ValueError(f'Invalid numeric value: {value!r}')
    return int(n) if integer else n


def parse_csv(data):
    reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
    required = {'Facility Name', 'Facility ID', 'State', 'Measure Name', 'Number of Discharges',
                'Excess Readmission Ratio', 'Predicted Readmission Rate', 'Expected Readmission Rate',
                'Number of Readmissions', 'Footnote', 'Start Date', 'End Date'}
    if set(reader.fieldnames or []) != required:
        raise ValueError('Unexpected CMS source schema')
    rows, keys, facilities = [], set(), {}
    for raw in reader:
        fid, measure = raw['Facility ID'], raw['Measure Name']
        if not re.fullmatch(r'\d{6}', fid) or not re.fullmatch(r'[A-Z]{2}', raw['State']):
            raise ValueError('Malformed facility identifier or state')
        if measure not in MEASURES or (fid, measure) in keys:
            raise ValueError('Unknown measure or duplicate facility-condition key')
        keys.add((fid, measure))
        identity = (raw['Facility Name'], raw['State'])
        if fid in facilities and facilities[fid] != identity:
            raise ValueError('Conflicting facility identity')
        facilities[fid] = identity
        start = datetime.strptime(raw['Start Date'], '%m/%d/%Y').date().isoformat()
        end = datetime.strptime(raw['End Date'], '%m/%d/%Y').date().isoformat()
        if start > end:
            raise ValueError('Inverted source period')
        row = dict(facility_id=fid, facility_name=identity[0], state=identity[1], measure_id=measure,
                   discharges=number(raw['Number of Discharges'], True),
                   err=number(raw['Excess Readmission Ratio']),
                   predicted_rate=number(raw['Predicted Readmission Rate']),
                   expected_rate=number(raw['Expected Readmission Rate']),
                   discharges_raw=raw['Number of Discharges'], err_raw=raw['Excess Readmission Ratio'],
                   readmissions_raw=raw['Number of Readmissions'], footnote=raw['Footnote'],
                   start_date=start, end_date=end)
        if row['err'] is not None and (row['err'] <= 0 or row['expected_rate'] is None or row['expected_rate'] <= 0 or row['predicted_rate'] is None):
            raise ValueError('Published ratio lacks valid component rates')
        rows.append(row)
    if len({(r['start_date'], r['end_date']) for r in rows}) != 1:
        raise ValueError('Expected one common measurement period')
    return rows


def load_source(path=None):
    path = Path(path or ROOT / 'data/hrrp.csv')
    data = path.read_bytes()
    manifest = json.loads((ROOT / 'source.json').read_text(encoding='utf-8'))
    if hashlib.sha256(data).hexdigest() != manifest['sha256']:
        raise ValueError('Source checksum does not match source.json')
    return parse_csv(data)


def database(rows):
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.executescript((ROOT / 'sql/schema.sql').read_text(encoding='utf-8'))
    facilities = {r['facility_id']: (r['facility_id'], r['facility_name'], r['state']) for r in rows}
    db.executemany('INSERT INTO facility VALUES (?,?,?)', facilities.values())
    db.executemany('INSERT INTO measure VALUES (?,?)', MEASURES.items())
    fields = ['facility_id', 'measure_id', 'discharges', 'err', 'predicted_rate', 'expected_rate',
              'discharges_raw', 'err_raw', 'readmissions_raw', 'footnote', 'start_date', 'end_date']
    db.executemany('INSERT INTO result VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', ([r[k] for k in fields] for r in rows))
    return db


def disposition(row, minimum=0):
    if row['err'] is None:
        return 'missing_ratio'
    if minimum > 0 and row['discharges'] is None:
        return 'missing_volume'
    if minimum > 0 and row['discharges'] < minimum:
        return 'below_volume'
    return 'eligible'


def summarize(db, measure, region, minimum=0):
    if minimum not in THRESHOLDS:
        raise ValueError('Unsupported volume sensitivity setting')
    query = (ROOT / 'sql/cohort_summary.sql').read_text(encoding='utf-8')
    return dict(db.execute(query, dict(measure=measure, region=region, minimum=minimum)).fetchone())


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def build():
    rows = load_source()
    db = database(rows)
    manifest = json.loads((ROOT / 'source.json').read_text(encoding='utf-8'))
    summaries, export = {}, []
    reconciliation_count = 0
    for threshold in THRESHOLDS:
        summaries[str(threshold)] = {}
        for measure in MEASURES:
            summaries[str(threshold)][measure] = {}
            for region in ['IN', 'US']:
                result = summarize(db, measure, region, threshold)
                summaries[str(threshold)][measure][region] = result
                # An independent Python calculation checks SQL windows and denominators.
                population = [r for r in rows if r['measure_id'] == measure and (region == 'US' or r['state'] == region)]
                eligible = [r['err'] for r in population if disposition(r, threshold) == 'eligible']
                if result['source_hospitals'] != sum(result[k] for k in ['eligible', 'missing_ratio', 'missing_volume', 'below_volume']):
                    raise AssertionError('Population disposition reconciliation failed')
                if result['eligible'] != len(eligible) or result['above_one'] != sum(v > 1 for v in eligible):
                    raise AssertionError('SQL/Python count disagreement')
                expected_median = statistics.median(eligible) if eligible else None
                if result['median_err'] != expected_median:
                    raise AssertionError('SQL/Python median disagreement')
                expected_share = sum(v > 1 for v in eligible) / len(eligible) if eligible else None
                if result['above_share'] != expected_share:
                    raise AssertionError('SQL/Python share disagreement')
                reconciliation_count += 1
                summaries[str(threshold)][measure][region] = result
                export.append(dict(region=region, measure=measure, minimum_discharges=threshold, **result))
    if db.execute('PRAGMA foreign_key_check').fetchall():
        raise AssertionError('Relational integrity failed')
    if len(rows) != manifest['expected_rows'] or len({r['facility_id'] for r in rows}) != manifest['expected_facilities']:
        raise AssertionError('Pinned source totals changed')
    if any(n != len(MEASURES) for n in Counter(r['facility_id'] for r in rows).values()):
        raise AssertionError('Facility does not have all six source measure rows')
    ratio_differences = [abs(r['err'] - r['predicted_rate'] / r['expected_rate']) for r in rows if r['err'] is not None]
    if max(ratio_differences) > 0.0001:
        raise AssertionError('Published ratio/component mismatch beyond rounding tolerance')
    indiana = sorted([r for r in rows if r['state'] == 'IN'], key=lambda r: (r['facility_name'], r['facility_id'], r['measure_id']))
    result = dict(project='Hospital Readmissions & Quality Benchmarking', built='2026-09-26',
                  source=manifest, measures=MEASURES, thresholds=THRESHOLDS, summaries=summaries,
                  indiana_rows=indiana,
                  checks=dict(cohort_reconciliations=reconciliation_count, source_rows=len(rows),
                              source_facilities=len({r['facility_id'] for r in rows}),
                              source_missing_ratios=sum(r['err'] is None for r in rows),
                              published_ratio_missing_volume=sum(r['err'] is not None and r['discharges'] is None for r in rows),
                              foreign_key_violations=0, max_ratio_rounding_difference=max(ratio_differences)))
    out = ROOT / 'outputs'
    out.mkdir(exist_ok=True)
    (out / 'summary.json').write_text(json.dumps(result, separators=(',', ':'), allow_nan=False) + '\n', encoding='utf-8')
    write_csv(out / 'indiana_hospital_measures.csv', indiana)
    write_csv(out / 'condition_benchmarks.csv', export)
    c = summaries['0']['READM-30-COPD-HRRP']
    p = summaries['0']['READM-30-CABG-HRRP']
    findings = f'''# Findings: Indiana hospital readmissions

Independent portfolio analysis created September 2026. CMS FY 2026 release;
measurement period July 1, 2021 through June 30, 2024. Results describe this
historical reporting period, not present-day hospital performance.

## Decision question

Which condition-specific patterns should an Indiana quality team investigate,
and how does missing published information affect that shortlist?

## Findings and next steps

1. **COPD is a starting point for review.** {c['IN']['above_one']} of {c['IN']['eligible']} Indiana hospitals
   with published COPD ratios ({100*c['IN']['above_share']:.1f}%) have a ratio above 1,
   compared with {100*c['US']['above_share']:.1f}% in the national source population.
   This {100*(c['IN']['above_share']-c['US']['above_share']):.1f} percentage-point descriptive difference is
   not a significance test, payment penalty or estimate of avoidable readmissions.
   Next: review measure volumes and facility context before choosing hospitals
   for a care-transition review. No intervention or savings is claimed here.
2. **Coverage varies by condition.** Heart failure has 72 published ratios among
   82 Indiana source hospitals; coronary bypass has {p['IN']['eligible']}. Missing ratios are
   excluded from that measure's denominator, not treated as good performance.
   Next: examine source footnotes and whether the service is offered before
   comparing programs with different reporting coverage.
3. **A volume filter changes the cohort.** Nationally, {result['checks']['published_ratio_missing_volume']:,} rows have
   a published ratio but unavailable discharge counts. Default results retain
   them. Any positive volume filter excludes them visibly and applies the same
   rule to Indiana and national benchmarks. These are analyst-selected
   sensitivity settings, not CMS reporting eligibility cutoffs.

## Baseline condition comparisons (no volume filter)

| Condition | Indiana published / source | Indiana above 1 | National above 1 |
|---|---:|---:|---:|
'''
    for m, label in MEASURES.items():
        s = summaries['0'][m]
        findings += f"| {label} | {s['IN']['eligible']} / {s['IN']['source_hospitals']} | {s['IN']['above_share']:.1%} | {s['US']['above_share']:.1%} |\n"
    findings += '''
## Interpretation

- Grain: one hospital × condition/procedure × common measurement period.
- Excess readmission ratio = CMS-published predicted / expected readmission rate.
  The project uses the published ratio; it does not estimate a new risk model.
- Above-one share = hospital-condition rows with ERR > 1 / rows eligible for
  the selected condition and volume filter. Every eligible hospital gets equal
  weight. This is a share of hospitals, not a patient readmission rate.
- National means all hospitals in this source file, including Indiana. It is
  descriptive context, not CMS's dual-eligibility peer-group payment benchmark.
- The median summarizes hospital ratios. No pooled patient rate, inferred
  suppressed count, financial penalty or all-condition composite is calculated.
- This snapshot cannot establish a time trend, causes, avoidability, or the
  effect of a quality intervention. No confidence intervals are provided by
  this extract, and no significance claim is made.

## Verification

48 independently reconciled region × condition × volume summaries; source
checksum and totals; unique keys; six source measure rows per facility;
foreign keys; published-ratio rounding check. Raw missing/suppression tokens
and source footnotes remain visible in the Indiana export.
'''
    (out / 'findings.md').write_text(findings, encoding='utf-8')
    print(f'{len(rows):,} rows; {len(indiana)} Indiana rows; {reconciliation_count} cohort reconciliations passed')
    return result


if __name__ == '__main__':
    build()
