import unittest

from analyze import aggregate, open_database, read_financials


class MetricsTest(unittest.TestCase):
    def setUp(self):
        self.db = open_database()
        self.addCleanup(self.db.close)
        self.db.executemany("INSERT INTO lines VALUES (?, ?, ?, ?, ?)", [
            ("1", "2010-12-20 10:00:00", "A", 2, 10),
            ("1", "2010-12-20 10:00:00", "A", 1, 5),
            ("2", "2011-01-19 10:00:00", "A", 1, 20),
            ("3", "2010-12-23 10:00:00", None, 1, 15),
            ("C4", "2010-12-23 10:00:00", "A", -1, 5),
            ("C5", "2010-12-23 10:00:00", "C", 1, 100),
            ("6", "2010-12-23 10:00:00", "C", 1, 0),
            ("7", "2010-12-23 10:00:00", "C", -2, 3),
            ("8", "2011-11-15 10:00:00", "B", 1, 7),
            ("9", "2011-12-02 10:00:00", "B", 1, 9),
            ("10", "2011-02-01 10:00:00", "D", 1, 10),
            ("11", "2011-02-01 10:00:00", "D", 1, 10),
        ])
        self.results = aggregate(self.db)

    def test_order_grain_coverage_and_growth(self):
        december, january = self.results["monthly"][:2]
        self.assertEqual(len(self.results["monthly"]), 12)
        self.assertEqual(december["orders"], 2)
        self.assertEqual(december["identified_orders"], 1)
        self.assertEqual(december["gross_gbp"], 40)
        self.assertEqual(december["aov_gbp"], 20)
        self.assertIsNone(december["mom"])
        self.assertEqual(january["mom"], -.5)

    def test_retention_uses_observed_zero_and_omits_censored_months(self):
        december = [row for row in self.results["retention"] if row["cohort"] == "2010-12-01"]
        november = [row for row in self.results["retention"] if row["cohort"] == "2011-11-01"]
        self.assertEqual([row["rate"] for row in december[:3]], [1, 1, 0])
        self.assertEqual([row["age"] for row in november], [0])

    def test_repeat_window_and_strictly_later_purchase(self):
        self.assertEqual(self.results["repeat_30d"], [
            {"eligible_buyers": 2, "repeat_buyers": 1, "rate": .5},
        ])

    def test_financial_reconciliation(self):
        history = read_financials()
        self.assertEqual([row["year"] for row in history], list(range(2021, 2026)))
        self.assertIsNone(history[0]["yoy"])
        self.assertEqual(history[-1]["revenue_rmb_thousands"], 37120052)
        self.assertAlmostEqual(history[-1]["yoy"] * 100, 184.7, places=1)


if __name__ == "__main__":
    unittest.main()
