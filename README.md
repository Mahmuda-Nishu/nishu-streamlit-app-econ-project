# U.S. Labor Statistics Dashboard

**An automated data pipeline and live dashboard for U.S. labor market trends**

👉 **[Open the live dashboard](https://mahmuda-nishu-nishu-streamlit-app-econ-project-app-twsbcq.streamlit.app/)**

## What it does
- Pulls **six monthly labor market indicators** from the U.S. Bureau of Labor Statistics (BLS) API, covering the last five years
- Refreshes the data **automatically every month** with a scheduled GitHub Actions pipeline
- Shows the data in an interactive **Streamlit** dashboard with key numbers, trend charts, comparisons and CSV downloads

## Indicators
| Indicator | BLS series ID | Unit |
|---|---|---|
| Total Nonfarm Employment | CES0000000001 | thousands of jobs |
| Unemployment Rate | LNS14000000 | % |
| Labor Force Participation Rate | LNS11300000 | % |
| Employment-Population Ratio | LNS12300000 | % |
| Average Hourly Earnings (private) | CES0500000003 | $ per hour |
| Manufacturing Employment | CES3000000001 | thousands of jobs |

## How the pipeline works
```
BLS API  →  bls_pipeline.py  →  bls_data.csv  →  app.py (Streamlit dashboard)
              ↑
   GitHub Actions, 10th of every month
```

1. **Extract:** `bls_pipeline.py` requests the latest five years of data from the BLS API.
2. **Transform:** it removes annual averages and missing values, adds readable names and units, and builds proper monthly dates.
3. **Load:** it saves a clean `bls_data.csv`. If the API call fails, the script stops with an error and the existing data is **not** overwritten.
4. **Automate:** `.github/workflows/update_data.yml` runs the pipeline monthly and commits the new data, and the dashboard picks it up automatically.
5. **Security:** the BLS API key is stored as a GitHub Actions **secret**, never in the code.

## Dashboard features
- **Explore one indicator:** latest value, change vs. last month and vs. a year ago, and an interactive trend chart
- **Compare indicators:** indicators with different units are indexed to 100 at the start of the period, so their growth can be compared on one chart
- Date range filter, data table and CSV download

## Tools
Python · pandas · Plotly · Streamlit · REST API · GitHub Actions

## How to run locally
```bash
pip install -r requirements.txt
export BLS_API_KEY=your_key_here   # free key: https://data.bls.gov/registrationEngine/
python bls_pipeline.py             # refresh the data
streamlit run app.py               # open the dashboard
```

---
*Started as a project for ECON 8320 Tools for Data Analysis, University of Nebraska Omaha; extended in 2026 with a corrected indicator set, secure API key handling, error handling, a working automated update, and an interactive Plotly dashboard.*
