import unittest

from dc_bias import calculate_dc_bias, kohm_to_ohm

VALID = dict(vcc=12, r1=100_000, r2=22_000, rc=2_200, re=1_000, beta=100, vbe=0.70)


def calc(**overrides):
    return calculate_dc_bias(**{**VALID, **overrides})


class TestKohmToOhm(unittest.TestCase):
    def test_converts_kohm_to_ohm(self):
        self.assertAlmostEqual(kohm_to_ohm(100), 100_000.0)
        self.assertAlmostEqual(kohm_to_ohm("2.2"), 2_200.0)


class TestReferenceValues(unittest.TestCase):
    def test_example_circuit(self):
        r = calc()
        self.assertAlmostEqual(r["vth"], 2.1639, delta=1e-3)
        self.assertAlmostEqual(r["rth"], 18_032.79, delta=0.1)
        self.assertAlmostEqual(r["ib"], 12.299e-6, delta=0.01e-6)
        self.assertAlmostEqual(r["ic"], 1.2299e-3, delta=0.01e-3)
        self.assertAlmostEqual(r["ie"], 1.2422e-3, delta=0.01e-3)
        self.assertAlmostEqual(r["ve"], 1.2422, delta=1e-3)
        self.assertAlmostEqual(r["vb"], 1.9422, delta=1e-3)
        self.assertAlmostEqual(r["vc"], 9.2943, delta=1e-3)
        self.assertAlmostEqual(r["vce"], 8.0521, delta=1e-3)
        self.assertEqual(r["region"], "Forward Active")
        self.assertEqual(r["warning"], "")


class TestValidation(unittest.TestCase):
    def test_zero_or_negative_components(self):
        for field in ("vcc", "r1", "r2", "rc", "re"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    calc(**{field: 0})
                with self.assertRaises(ValueError):
                    calc(**{field: -1})

    def test_invalid_beta(self):
        with self.assertRaises(ValueError):
            calc(beta=0)
        with self.assertRaises(ValueError):
            calc(beta=-5)

    def test_negative_vbe(self):
        with self.assertRaises(ValueError):
            calc(vbe=-0.1)

    def test_non_numeric_blank_and_malformed(self):
        for value in ("abc", "", None, "1,000"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calc(vcc=value)

    def test_non_finite(self):
        for value in (float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calc(r1=value)

    def test_kohm_to_ohm_rejects_bad_values(self):
        for value in (0, -1, "abc", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    kohm_to_ohm(value)


class TestRegion(unittest.TestCase):
    def test_cutoff_when_vth_below_vbe(self):
        r = calc(r2=1_000)
        self.assertEqual(r["region"], "Cutoff")
        self.assertIn("cutoff", r["warning"].lower())

    def test_saturation_when_vce_below_limit(self):
        r = calc(re=100)
        self.assertEqual(r["region"], "Saturation")
        self.assertIn("saturation", r["warning"].lower())

    def test_forward_active_has_no_warning(self):
        r = calc()
        self.assertEqual(r["region"], "Forward Active")
        self.assertEqual(r["warning"], "")


if __name__ == "__main__":
    unittest.main()
