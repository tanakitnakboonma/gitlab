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


if __name__ == "__main__":
    unittest.main()
