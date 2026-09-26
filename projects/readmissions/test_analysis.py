import csv
import io
from pathlib import Path
import tempfile
import unittest

from analysis import MEASURES, database, disposition, load_source, number, parse_csv, summarize

MEASURE = next(iter(MEASURES))


def record(fid, err=1.1, volume=100):
    return dict(facility_id=fid, facility_name=f'Hospital {fid}', state='IN', measure_id=MEASURE,
                discharges=volume, err=err, predicted_rate=11.0, expected_rate=10.0,
                discharges_raw='N/A' if volume is None else str(volume),
                err_raw='N/A' if err is None else str(err), readmissions_raw='Too Few to Report',
                footnote='', start_date='2021-07-01', end_date='2024-06-30')


def source_csv(identifiers):
    buffer = io.StringIO()
    headers = ['Facility Name', 'Facility ID', 'State', 'Measure Name', 'Number of Discharges',
               'Excess Readmission Ratio', 'Predicted Readmission Rate', 'Expected Readmission Rate',
               'Number of Readmissions', 'Footnote', 'Start Date', 'End Date']
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for fid in identifiers:
        writer.writerow(['Hospital', fid, 'IN', MEASURE, 'N/A', '1.1000', '11.0', '10.0',
                         'Too Few to Report', '', '07/01/2021', '06/30/2024'])
    return buffer.getvalue().encode()


class AnalysisTests(unittest.TestCase):
    def test_missing_volume_does_not_remove_published_ratio_by_default(self):
        rows = [record('000001', 1.2, None), record('000002', .8, 100), record('000003', None, None)]
        db = database(rows)
        all_rows = summarize(db, MEASURE, 'IN')
        filtered = summarize(db, MEASURE, 'IN', 25)
        self.assertEqual((all_rows['eligible'], all_rows['above_share']), (2, .5))
        self.assertEqual((filtered['eligible'], filtered['missing_volume'], filtered['missing_ratio']), (1, 1, 1))
        self.assertEqual(filtered['above_share'], 0)

    def test_ratio_one_is_neutral_and_zero_volume_is_numeric(self):
        self.assertEqual(number('0', True), 0)
        self.assertIsNone(number('N/A'))
        db = database([record('000001', 1.0, 0)])
        result = summarize(db, MEASURE, 'IN')
        self.assertEqual((result['exactly_one'], result['above_one']), (1, 0))
        self.assertEqual(summarize(db, MEASURE, 'IN', 25)['below_volume'], 1)

    def test_median_odd_even_and_empty(self):
        db = database([record('000001', .7, 20), record('000002', 1.0, 25), record('000003', 1.5, 100)])
        self.assertEqual(summarize(db, MEASURE, 'IN')['median_err'], 1.0)
        self.assertEqual(summarize(db, MEASURE, 'IN', 25)['median_err'], 1.25)
        empty = summarize(db, MEASURE, 'IN', 250)
        self.assertEqual(empty['eligible'], 0)
        self.assertIsNone(empty['median_err'])
        self.assertIsNone(empty['above_share'])

    def test_region_and_national_denominators(self):
        other = record('000002', .8)
        other['state'] = 'OH'
        db = database([record('000001', 1.2), other])
        self.assertEqual(summarize(db, MEASURE, 'IN')['above_share'], 1)
        self.assertEqual(summarize(db, MEASURE, 'US')['above_share'], .5)
        self.assertEqual(summarize(db, MEASURE, 'XX')['source_hospitals'], 0)

    def test_parse_preserves_ids_missing_tokens_and_dates(self):
        row = parse_csv(source_csv(['000001']))[0]
        self.assertEqual(row['facility_id'], '000001')
        self.assertIsNone(row['discharges'])
        self.assertEqual(row['readmissions_raw'], 'Too Few to Report')
        self.assertEqual(row['start_date'], '2021-07-01')

    def test_duplicate_grain_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            parse_csv(source_csv(['000001', '000001']))

    def test_nonfinite_and_invalid_integer_rejected(self):
        for token in ['NaN', 'inf', '-1', 'unavailable']:
            with self.subTest(token=token), self.assertRaises(ValueError):
                number(token)
        with self.assertRaises(ValueError):
            number('1.5', True)

    def test_checksum_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'changed.csv'
            path.write_bytes(source_csv(['000001']))
            with self.assertRaisesRegex(ValueError, 'checksum'):
                load_source(path)

    def test_boundary_and_disposition_priority(self):
        self.assertEqual(disposition(record('000001', None, None), 25), 'missing_ratio')
        self.assertEqual(disposition(record('000001', 1.1, 25), 25), 'eligible')
        self.assertEqual(disposition(record('000001', 1.1, 24), 25), 'below_volume')


if __name__ == '__main__':
    unittest.main()
