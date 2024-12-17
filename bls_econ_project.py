# -*- coding: utf-8 -*-
"""bls_econ_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QFT1IRdvi2pNZozCHzN8cOWKNveoTT9Z
"""

import requests
import pandas as pd
import json

# BLS API Configuration
API_KEY = 'c16ee0e2c0254295a624f21454282715'  # API Key
BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
HEADERS = {'Content-type': 'application/json'}

# Define the series IDs and payload
SERIES_IDS = [
    "CES0000000001",  # Total Non-Farm Workers
    "LNS14000000",    # Unemployment Rate
    "CES0500000003",  # Average Weekly Hours of Production Employees
    "CES3000000001",  # Manufacturing Employment
    "LNS14100000"     # Employment-Population Ratio
]

payload = {
    "seriesid": SERIES_IDS,
    "startyear": "2022",
    "endyear": "2023",
    "registrationkey": API_KEY
}

# Fetch data from the API
try:
    response = requests.post(BLS_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    json_data = response.json()
    print("Data fetched successfully!")

    # Save the raw response for debugging
    with open("raw_bls_response.json", "w") as f:
        json.dump(json_data, f, indent=4)

except requests.exceptions.RequestException as e:
    print(f"Error fetching data from BLS API: {e}")

# Function to process the BLS data
def process_bls_data(json_data):
    series_list = []

    # Ensure the response contains the 'series' key
    if 'Results' in json_data and 'series' in json_data['Results']:
        for series in json_data['Results']['series']:
            series_id = series['seriesID']
            for entry in series['data']:
                series_list.append({
                    "series_id": series_id,
                    "year": entry['year'],
                    "period": entry['period'],
                    "period_name": entry['periodName'],
                    "value": float(entry['value']),  # Convert value to float
                })

    # Create a DataFrame and format it
    df = pd.DataFrame(series_list)
    df['year_month'] = df['year'] + '-' + df['period'].str[1:]
    df = df[['series_id', 'year_month', 'value', 'year', 'period', 'period_name']]

    # Save to CSV
    df.to_csv("bls_data_combined.csv", index=False)
    print("Data processed and saved as 'bls_data_combined.csv'")
    return df

# Process the fetched data
df = process_bls_data(json_data)