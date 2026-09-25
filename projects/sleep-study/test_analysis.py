"""Independent numerical and source invariants for the published reanalysis."""
import tempfile
from pathlib import Path
import unittest
import numpy as np
from scipy import stats
from analysis import analyze, ols, read_source


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_source()
        cls.result = analyze(cls.rows)

    def test_hand_calculated_line(self):
        fit = ols([[1,0],[1,1],[1,2],[1,3]], [1,3,5,7], ["intercept","slope"])
        np.testing.assert_allclose([c["estimate"] for c in fit["coefficients"]], [1,2])

    def test_simple_fit_matches_independent_scipy(self):
        a = [r["Physical Activity Level"] for r in self.rows]
        y = [r["Quality of Sleep"] for r in self.rows]
        fit = stats.linregress(a,y)
        self.assertAlmostEqual(self.result["groups"]["all"]["slope"], fit.slope, places=12)

    def test_checksum_rejects_modified_input(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"changed.csv";p.write_text("modified")
            with self.assertRaises(ValueError):read_source(p)

    def test_group_denominators_reconcile(self):
        self.assertEqual(sum(self.result["bmi_counts"].values()), 374)
        groups=self.result["groups"]
        self.assertEqual(groups["gender-female"]["n"]+groups["gender-male"]["n"],374)
        for g in groups.values():self.assertEqual(sum(p["count"] for p in g["points"]),g["n"])

    def test_source_labels_and_none_are_preserved(self):
        self.assertEqual(set(self.result["bmi_counts"]),{"Normal","Normal Weight","Overweight","Obese"})
        self.assertTrue(any(r["Sleep Disorder"] == "None" for r in self.rows))
        self.assertEqual(self.result["unique_profiles"],132)

    def test_group_slopes_match_interaction_parameterization(self):
        b=[c["estimate"] for c in self.result["gender_interaction"]["coefficients"]]
        self.assertAlmostEqual(b[1],self.result["groups"]["gender-female"]["slope"],places=12)
        self.assertAlmostEqual(b[1]+b[3],self.result["groups"]["gender-male"]["slope"],places=12)

    def test_rank_deficient_design_rejected(self):
        with self.assertRaises(ValueError):ols([[1,1],[1,1],[1,1]],[1,2,3],["a","b"])

if __name__ == "__main__":unittest.main()
