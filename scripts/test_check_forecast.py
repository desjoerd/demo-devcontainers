from copy import deepcopy
import unittest

from check_forecast import validate_forecast


class ForecastValidationTests(unittest.TestCase):
    def setUp(self):
        self.forecast = [
            {"date": f"2026-01-{day:02}", "temperatureC": -5,
             "temperatureF": 24, "summary": "Cold"}
            for day in range(1, 6)
        ]

    def test_accepts_valid_forecast(self):
        validate_forecast(self.forecast)

    def test_rejects_wrong_count(self):
        with self.assertRaisesRegex(ValueError, "exactly five"):
            validate_forecast(self.forecast[:4])

    def test_rejects_invalid_fields(self):
        for field, value in (
            ("date", "not-a-date"),
            ("date", None),
            ("temperatureC", True),
            ("temperatureC", 55),
            ("temperatureF", 99),
            ("summary", " "),
        ):
            with self.subTest(field=field, value=value):
                forecast = deepcopy(self.forecast)
                forecast[0][field] = value
                with self.assertRaises(ValueError):
                    validate_forecast(forecast)

    def test_rejects_nonconsecutive_dates(self):
        self.forecast[1]["date"] = "2026-01-10"
        with self.assertRaisesRegex(ValueError, "consecutive"):
            validate_forecast(self.forecast)

    def test_rejects_invalid_shapes(self):
        for forecast in (None, {}, [None] * 5):
            with self.subTest(forecast=forecast):
                with self.assertRaises(ValueError):
                    validate_forecast(forecast)


if __name__ == "__main__":
    unittest.main()
