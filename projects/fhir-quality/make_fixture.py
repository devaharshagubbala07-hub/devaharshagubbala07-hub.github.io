"""Create a deterministic, wholly fictional local test bundle with known faults."""
from copy import deepcopy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE="https://example.org/fhir/"


def make_bundle():
    entries=[]
    def add(resource):
        entries.append({"fullUrl":BASE+resource["resourceType"]+"/"+resource["id"],"resource":resource})
    for i in range(1,9):
        r={"resourceType":"Patient","id":f"p{i:02}","gender":"female" if i%2 else "male"}
        if i!=7:r["birthDate"]={3:"1976",4:"1990-04"}.get(i,f"198{i}-02-15")
        add(r)
    add({"resourceType":"Patient","id":"p-bad","gender":"unspecified","birthDate":"1991-02-15"})
    def observation(rid,pid,status="final"):
        return {"resourceType":"Observation","id":rid,"status":status,
                "code":{"coding":[{"system":"http://loinc.org","code":"8867-4","display":"Heart rate"}]},
                "subject":{"reference":"Patient/"+pid},"effectiveDateTime":"2026-01-15T09:00:00Z",
                "valueQuantity":{"value":72,"unit":"beats/minute","system":"http://unitsofmeasure.org","code":"/min"}}
    for i in range(1,13):
        r=observation(f"o{i:03}",f"p{(i-1)//2+1:02}","preliminary" if i==3 else "final")
        r["valueQuantity"]["value"]=65+i
        if i==2:r["subject"]["reference"]=BASE+"Patient/p01"
        add(r)
    add(observation("o-orphan","p404"))
    wrong_unit=observation("o-unit","p01");wrong_unit["valueQuantity"]["code"]="beats/min";add(wrong_unit)
    wrong_date=observation("o-date","p01");wrong_date["effectiveDateTime"]="2026-01-15T09:00:00";add(wrong_date)
    foreign=observation("o-foreign","p01");foreign["subject"]["reference"]="https://other.example.org/fhir/Patient/p01";add(foreign)
    # Both copies are quarantined. No arbitrary 'keep first' rule.
    entries.append(deepcopy(next(e for e in entries if e["resource"]["id"]=="o001")))
    for i,pid in enumerate(["p01","p02","p07","p08","p404"],1):
        add({"resourceType":"Condition","id":f"c{i:03}",
             "clinicalStatus":{"coding":[{"system":"http://terminology.hl7.org/CodeSystem/condition-clinical","code":"active"}]},
             "subject":{"reference":"Patient/"+pid},
             "code":{"coding":[{"system":"https://example.org/fhir/CodeSystem/demo-conditions","code":"DEMO-A"}]}})
    add({"resourceType":"Procedure","id":"outside-scope","status":"completed","subject":{"reference":"Patient/p01"}})
    entries.append({"fullUrl":BASE+"Patient/missing-resource"})
    return {"resourceType":"Bundle","type":"collection","entry":entries}


if __name__=="__main__":
    (ROOT/"data").mkdir(exist_ok=True)
    (ROOT/"data/demo-bundle.json").write_text(json.dumps(make_bundle(),indent=2)+"\n")
