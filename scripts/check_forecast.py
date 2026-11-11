"""Check the running weather API using only Python's standard library."""

import argparse
from datetime import date, timedelta
import json
import sys
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen


def validate_forecast(forecast: object) -> None:
    if not isinstance(forecast, list) or len(forecast) != 5:
        raise ValueError("Expected a JSON array with exactly five forecasts.")

    previous_date = None
    for index, day in enumerate(forecast, start=1):
        if not isinstance(day, dict):
            raise ValueError(f"Forecast {index} must be an object.")
        if not isinstance(day.get("date"), str):
            raise ValueError(f"Forecast {index} must have an ISO date.")
        forecast_date = date.fromisoformat(day["date"])
        if previous_date is not None and forecast_date != previous_date + timedelta(days=1):
            raise ValueError("Forecast dates must be consecutive.")
        previous_date = forecast_date

        celsius = day.get("temperatureC")
        fahrenheit = day.get("temperatureF")
        if type(celsius) is not int or not -20 <= celsius <= 54:
            raise ValueError(f"Forecast {index} has an invalid Celsius temperature.")
        if type(fahrenheit) is not int or fahrenheit != 32 + int(celsius / 0.5556):
            raise ValueError(f"Forecast {index} has an inconsistent Fahrenheit temperature.")
        if not isinstance(day.get("summary"), str) or not day["summary"].strip():
            raise ValueError(f"Forecast {index} needs a non-empty summary.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://localhost:5331",
                        help="API endpoint from the Aspire dashboard (default: %(default)s)")
    args = parser.parse_args()
    parsed = urlparse(args.api_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        parser.error("--api-url must be an absolute HTTP or HTTPS URL.")

    base_url = args.api_url.rstrip("/")
    try:
        with urlopen(f"{base_url}/health", timeout=15) as response:
            if response.status != 200 or response.read().decode().strip() != "Healthy":
                raise ValueError("The API health check did not report Healthy.")
        with urlopen(f"{base_url}/weatherforecast", timeout=15) as response:
            if response.status != 200:
                raise ValueError(f"The forecast endpoint returned HTTP {response.status}.")
            forecast = json.load(response)
        validate_forecast(forecast)
    except (URLError, OSError, ValueError) as error:
        print(f"API check failed: {error}", file=sys.stderr)
        return 1

    print("API check passed: healthy service and five valid, consecutive forecasts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
