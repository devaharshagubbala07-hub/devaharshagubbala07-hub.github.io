"""Offline FHIR R4-shaped fixture to reporting tables and a quality ledger.

This intentionally narrow reporting profile is NOT a full FHIR validator.
No network calls, authentication, clinical decisions or terminology remapping.
"""
from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parent
SUPPORTED = {"Patient", "Observation", "Condition"}
ID = re.compile(r"[A-Za-z0-9\-.]{1,64}\Z")
GENDERS = {"male", "female", "other", "unknown"}
OBS_STATUSES = {"registered", "preliminary", "final", "amended", "corrected",
                "cancelled", "entered-in-error", "unknown"}
REFERENCE_DATE = date(2026, 1, 31)


def valid_birth_date(value):
    """Preserve legal FHIR date precision; never impute a complete date."""
    if not isinstance(value, str):return False
    try:
        if re.fullmatch(r"\d{4}", value):d=date(int(value),1,1)
        elif re.fullmatch(r"\d{4}-\d{2}", value):d=date.fromisoformat(value+"-01")
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):d=date.fromisoformat(value)
        else:return False
        return d <= REFERENCE_DATE
    except ValueError:return False


def valid_timestamp(value):
    """The demo reporting profile requires a timezone-bearing timestamp."""
    if not isinstance(value,str) or "T" not in value:return False
    try:
        return datetime.fromisoformat(value.replace("Z","+00:00")).tzinfo is not None
    except ValueError:return False


def classify(bundle):
    if not isinstance(bundle,dict) or bundle.get("resourceType") != "Bundle" or bundle.get("type") != "collection":
        raise ValueError("Expected a collection Bundle for this local demo")
    if not isinstance(bundle.get("entry"),list):raise ValueError("Bundle.entry must be an array")
    records=[]
    for i,entry in enumerate(bundle["entry"],1):
        r=entry.get("resource") if isinstance(entry,dict) else None
        full=entry.get("fullUrl") if isinstance(entry,dict) else None
        r=r if isinstance(r,dict) else {}
        kind=r.get("resourceType");rid=r.get("id")
        kind=kind if isinstance(kind,str) else "Unknown"
        rid=rid if isinstance(rid,str) else ""
        records.append({"entry":i,"type":kind,"id":rid,"key":kind+"/"+rid,
                        "resource":r,"full_url":full if isinstance(full,str) else None,
                        "errors":[],"warnings":[]})
    identities=Counter(r["key"] for r in records if r["id"])
    urls=Counter(r["full_url"] for r in records if r["full_url"])
    for row in records:
        r=row["resource"];errors=row["errors"]
        if not r:errors.append("missing_resource")
        elif row["type"] not in SUPPORTED:errors.append("outside_demo_scope")
        if not ID.fullmatch(row["id"]):errors.append("invalid_or_missing_id")
        if row["id"] and identities[row["key"]]>1:errors.append("duplicate_identity")
        if row["full_url"] and urls[row["full_url"]]>1:errors.append("ambiguous_full_url")
        if row["type"]=="Patient":
            if r.get("gender") is not None and (not isinstance(r["gender"],str) or r["gender"] not in GENDERS):errors.append("invalid_gender_code")
            if r.get("birthDate") is None:row["warnings"].append("missing_birth_date")
            elif not valid_birth_date(r["birthDate"]):errors.append("invalid_birth_date")
            if r.get("gender") is None:row["warnings"].append("missing_gender")
        if row["type"]=="Observation":
            if not isinstance(r.get("status"),str) or r["status"] not in OBS_STATUSES:errors.append("invalid_observation_status")
            codes=r.get("code",{}).get("coding",[]) if isinstance(r.get("code"),dict) else []
            if not isinstance(codes,list) or not any(isinstance(c,dict) and c.get("system")=="http://loinc.org" and c.get("code")=="8867-4" for c in codes):
                errors.append("outside_heart_rate_profile")
            q=r.get("valueQuantity",{})
            if not isinstance(q,dict):q={}
            value=q.get("value")
            # bool is a Python int; explicitly reject it as a measurement.
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not (float("-inf")<value<float("inf")):
                errors.append("missing_or_invalid_quantity")
            if q.get("system")!="http://unitsofmeasure.org" or q.get("code")!="/min":
                errors.append("unexpected_unit")
            if not valid_timestamp(r.get("effectiveDateTime")):errors.append("invalid_effective_timestamp")
        if row["type"]=="Condition":
            codes=r.get("code",{}).get("coding",[]) if isinstance(r.get("code"),dict) else []
            # Restrict this small example to exactly one coded concept, keeping
            # system and code together. Multi-coding resources need a child table.
            if not isinstance(codes,list) or len(codes)!=1 or not isinstance(codes[0],dict) or not all(isinstance(codes[0].get(k),str) and codes[0][k] for k in ["system","code"]):
                errors.append("outside_single_coding_profile")
    patients={r["key"]:r for r in records if r["type"]=="Patient" and not r["errors"]}
    aliases={r["full_url"]:r["key"] for r in patients.values() if r["full_url"]}
    for row in records:
        if row["type"] in {"Observation","Condition"}:
            subject=row["resource"].get("subject",{})
            ref=subject.get("reference") if isinstance(subject,dict) else None
            key=ref if isinstance(ref,str) and ref in patients else aliases.get(ref) if isinstance(ref,str) else None
            if key is None:row["errors"].append("unresolved_patient_reference")
            else:row["patient_id"]=patients[key]["id"]
        row["status"]="Quarantined" if row["errors"] else "Loaded with warning" if row["warnings"] else "Loaded"
    return records


def run(bundle):
    records=classify(bundle)
    db=sqlite3.connect(":memory:")
    db.row_factory=sqlite3.Row
    db.executescript((ROOT/"sql/schema.sql").read_text(encoding="utf-8"))
    # Load parent rows before their dependents, regardless of Bundle order.
    for row in sorted(records, key=lambda r: r["type"] != "Patient"):
        db.execute("INSERT INTO audit VALUES(?,?,?,?,?)",(row["entry"],row["type"],row["key"],row["status"],"; ".join(row["errors"]+row["warnings"])))
        if row["errors"]:continue
        r=row["resource"]
        if row["type"]=="Patient":
            db.execute("INSERT INTO patient VALUES(?,?,?)",(r["id"],r.get("gender"),r.get("birthDate")))
        elif row["type"]=="Observation":
            db.execute("INSERT INTO observation VALUES(?,?,?,?,?)",(r["id"],row["patient_id"],r["status"],r["effectiveDateTime"],r["valueQuantity"]["value"]))
        elif row["type"]=="Condition":
            coding=r["code"]["coding"][0]
            db.execute("INSERT INTO condition_record VALUES(?,?,?,?)",(r["id"],row["patient_id"],coding["system"],coding["code"]))
    coverage=dict(db.execute((ROOT/"sql/coverage.sql").read_text(encoding="utf-8")).fetchone())
    accepted=[r for r in records if not r["errors"]]
    ledger=[{k:r[k] for k in ["entry","type","key","status","errors","warnings"]} for r in records]
    totals={"input_entries":len(records),"loaded":len(accepted),"quarantined":len(records)-len(accepted),
            "warning_entries":sum(bool(r["warnings"]) and not r["errors"] for r in records)}
    by_type=[]
    for kind in sorted({r["type"] for r in records}):
        subset=[r for r in records if r["type"]==kind]
        by_type.append({"type":kind,"input":len(subset),"loaded":sum(not r["errors"] for r in subset),
                        "quarantined":sum(bool(r["errors"]) for r in subset)})
    # Row-level issue counts may exceed quarantined rows; expose both denominators.
    issues=Counter(issue for r in records for issue in r["errors"])
    checks={
        "input_equals_loaded_plus_quarantined":totals["input_entries"]==totals["loaded"]+totals["quarantined"],
        "type_totals_reconcile":sum(r["input"] for r in by_type)==len(records),
        "patient_denominator_reconciles":coverage["patients"]==coverage["with_final_observation"]+coverage["without_final_observation"],
        "foreign_keys_valid":not db.execute("PRAGMA foreign_key_check").fetchall(),
        "no_missing_birth_date_imputed":db.execute("SELECT COUNT(*) FROM patient WHERE birth_date IS NULL").fetchone()[0]==sum(r["type"]=="Patient" and r["resource"].get("birthDate") is None for r in accepted),
    }
    assert all(checks.values()),"Reconciliation failed"
    result={"provenance":"New 2026 portfolio extension with intentionally flawed, wholly fictional records",
            "reference_date":str(REFERENCE_DATE),"totals":totals,"by_type":by_type,"coverage":coverage,
            "issue_counts":dict(sorted(issues.items())),"checks":checks,"ledger":ledger}
    db.close()
    return result


def main():
    bundle=json.loads((ROOT/"data/demo-bundle.json").read_text(encoding="utf-8"))
    result=run(bundle)
    out=ROOT/"outputs";out.mkdir(exist_ok=True)
    (out/"summary.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n", encoding="utf-8")
    t=result["totals"];c=result["coverage"]
    (out/"findings.md").write_text(f"""# Data quality before the denominator

All figures below come from intentionally flawed synthetic demo records. They are
not measurements of the academic team's original system or a production feed.

- **{t['input_entries']} input entries = {t['loaded']} loaded + {t['quarantined']} quarantined.**
- **{t['warning_entries']} loaded record(s) have a warning.** Missing birth dates
  stay null; the pipeline does not fabricate a demographic value to pass a check.
- **{c['with_final_observation']} of {c['patients']} loaded patients** have at least
  one accepted observation with status exactly `final`. There are
  {c['final_observation_rows']} final observation rows: counting rows instead of
  distinct patients would overstate coverage.
- **{c['without_final_observation']} loaded patients have no accepted final observation.**
  A left join keeps them in the reporting denominator. Absence from this fixture
  is not evidence that someone missed care.
- All {len(result['checks'])} reconciliation checks pass.

## Decision

Resolve duplicate identities and patient references before reporting. Review
quarantined resources with the source owner; do not guess which duplicate is
authoritative or replace clinical codes with more specific concepts.

## Scope

The pipeline implements a small local reporting profile for Patient, scalar
heart-rate Observation and single-coding Condition resources. A valid FHIR
resource can fall outside this profile. Passing these checks is not full FHIR
conformance, clinical validation, or evidence of privacy compliance.
""", encoding="utf-8")
    print(json.dumps({"totals":t,"coverage":c,"checks":result["checks"]}))


if __name__=="__main__":main()
