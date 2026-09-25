from copy import deepcopy
import unittest
from make_fixture import make_bundle
from pipeline import run, classify, valid_birth_date


class PipelineTests(unittest.TestCase):
    def setUp(self):self.bundle=make_bundle()

    def test_known_totals_and_coverage(self):
        r=run(self.bundle)
        self.assertEqual(r["totals"],{"input_entries":33,"loaded":23,"quarantined":10,"warning_entries":1})
        self.assertEqual(r["coverage"],{"patients":8,"with_final_observation":6,"without_final_observation":2,"final_observation_rows":10})
        self.assertTrue(all(r["checks"].values()))

    def test_reorder_does_not_change_decisions(self):
        before=run(self.bundle)
        self.bundle["entry"].reverse()
        after=run(self.bundle)
        self.assertEqual(before["totals"],after["totals"])
        self.assertEqual(before["coverage"],after["coverage"])
        self.assertEqual(before["issue_counts"],after["issue_counts"])

    def test_duplicate_identity_rejects_every_copy(self):
        rows=[r for r in classify(self.bundle) if r["key"]=="Observation/o001"]
        self.assertEqual(len(rows),2)
        self.assertTrue(all("duplicate_identity" in r["errors"] for r in rows))

    def test_reference_namespace_is_not_discarded(self):
        rows={r["key"]:r for r in classify(self.bundle)}
        self.assertFalse(rows["Observation/o002"]["errors"])
        self.assertIn("unresolved_patient_reference",rows["Observation/o-foreign"]["errors"])

    def test_invalid_patient_cascades_to_dependents(self):
        for e in self.bundle["entry"]:
            if e.get("resource",{}).get("id")=="p01":e["resource"]["gender"]="bad"
        rows={r["key"]:r for r in classify(self.bundle)}
        self.assertIn("unresolved_patient_reference",rows["Observation/o002"]["errors"])

    def test_missing_birth_date_is_warning_not_fabricated(self):
        rows={r["key"]:r for r in classify(self.bundle)}
        p=rows["Patient/p07"]
        self.assertFalse(p["errors"])
        self.assertEqual(p["warnings"],["missing_birth_date"])
        self.assertNotIn("birthDate",p["resource"])
        self.assertTrue(valid_birth_date("1976"));self.assertTrue(valid_birth_date("1990-04"))
        self.assertFalse(valid_birth_date("1990-02-30"))

    def test_empty_bundle_has_zero_denominator(self):
        r=run({"resourceType":"Bundle","type":"collection","entry":[]})
        self.assertEqual(r["coverage"]["patients"],0)
        self.assertEqual(r["coverage"]["with_final_observation"],0)

    def test_input_is_not_mutated(self):
        original=deepcopy(self.bundle);run(self.bundle);self.assertEqual(original,self.bundle)

    def test_malformed_coding_is_quarantined(self):
        for e in self.bundle["entry"]:
            if e.get("resource",{}).get("id")=="c001":e["resource"]["code"]["coding"]=None
        rows={r["key"]:r for r in classify(self.bundle)}
        self.assertIn("outside_single_coding_profile",rows["Condition/c001"]["errors"])

if __name__=="__main__":unittest.main()
