"""Fetch U.S. labor statistics from the BLS API and save them as a clean CSV.

Runs automatically every month through GitHub Actions
(.github/workflows/update_data.yml), so the dashboard always shows the
latest five years of data.

The API key is read from the BLS_API_KEY environment variable
(a GitHub Actions secret). It is never stored in the code.

Run locally:
    export BLS_API_KEY=your_key_here
    python bls_pipeline.py
"""

import datetime as dt
import os
import sys

import pandas as pd
import requests

BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
OUTPUT_FILE = "bls_data.csv"
YEARS_OF_HISTORY = 5

# Series ID -> (display name, unit)
SERIES = {
    "CES0000000001": ("Total Nonfarm Employment", "thousands of jobs"),
    "LNS14000000": ("Unemployment Rate", "%"),
    "LNS11300000": ("Labor Force Participation Rate", "%"),
    "LNS12300000": ("Employment-Population Ratio", "%"),
    "CES0500000003": ("Average Hourly Earnings (private)", "$ per hour"),
    "CES3000000001": ("Manufacturing Employment", "thousands of jobs"),
}


def fetch(api_key):
    end_year = dt.date.today().year
    payload = {
        "seriesid": list(SERIES),
        "startyear": str(end_year - YEARS_OF_HISTORY + 1),
        "endyear": str(end_year),
    }
    if api_key:
        payload["registrationkey"] = api_key

    response = requests.post(BLS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API error: {data.get('message')}")
    return data


def process(data):
    rows = []
    for series in data["Results"]["series"]:
        series_id = series["seriesID"]
        name, unit = SERIES[series_id]
        for entry in series["data"]:
            period = entry["period"]
            if not period.startswith("M") or period == "M13":  # skip annual averages
                continue
            try:
                value = float(entry["value"])
            except ValueError:  # BLS uses "-" for missing values
                continue
            rows.append({
                "series_id": series_id,
                "series_name": name,
                "unit": unit,
                "date": f"{entry['year']}-{period[1:]}-01",
                "value": value,
            })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["series_id", "date"]).reset_index(drop=True)


def main():
    api_key = os.environ.get("BLS_API_KEY")
    if not api_key:
        print("Warning: BLS_API_KEY is not set; using the lower unregistered API limits.")

    try:
        df = process(fetch(api_key))
    except Exception as error:
        # Exit with an error so the GitHub Action fails visibly
        # and the existing CSV is NOT overwritten with bad data.
        print(f"Data update failed: {error}")
        sys.exit(1)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df):,} rows for {df['series_id'].nunique()} series "
          f"({df['date'].min():%b %Y} to {df['date'].max():%b %Y}) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
