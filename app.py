"""U.S. Labor Statistics Dashboard (Streamlit).

Reads bls_data.csv, which bls_pipeline.py refreshes monthly from the BLS API.

Run:  pip install -r requirements.txt
      streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="U.S. Labor Statistics Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("bls_data.csv", parse_dates=["date"])
    return df.sort_values("date")


def fmt(value, unit):
    """Format a number for its unit: whole numbers for job counts, 2 decimals otherwise."""
    if unit == "%":
        return f"{value:.1f}%"
    if unit.startswith("$"):
        return f"${value:,.2f}"
    return f"{value:,.0f}K jobs"


df = load_data()
series_names = list(df["series_name"].unique())
latest_date = df["date"].max()

st.title("📊 U.S. Labor Statistics Dashboard")
st.caption(f"Source: U.S. Bureau of Labor Statistics API · Data through **{latest_date:%B %Y}** · "
           "Updated automatically every month")

# Sidebar filters
st.sidebar.header("Filters")
min_date, max_date = df["date"].min().date(), latest_date.date()
start, end = st.sidebar.slider("Date range", min_value=min_date, max_value=max_date,
                               value=(min_date, max_date), format="MMM YYYY")
df_range = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]

tab_single, tab_compare = st.tabs(["📈 Explore one indicator", "⚖️ Compare indicators"])

# ---- Tab 1: one indicator with key numbers ----
with tab_single:
    choice = st.selectbox("Indicator", series_names)
    data = df_range[df_range["series_name"] == choice]
    unit = data["unit"].iloc[0]

    if len(data) >= 2:
        latest = data.iloc[-1]
        prev_month = data.iloc[-2]
        year_ago = data[data["date"] == latest["date"] - pd.DateOffset(years=1)]

        col1, col2, col3 = st.columns(3)
        col1.metric(f"Latest ({latest['date']:%b %Y})", fmt(latest['value'], unit))
        col2.metric("Change vs. last month", f"{latest['value'] - prev_month['value']:+,.2f}")
        if not year_ago.empty:
            col3.metric("Change vs. a year ago", f"{latest['value'] - year_ago['value'].iloc[0]:+,.2f}")

    fig = px.line(data, x="date", y="value", markers=True,
                  labels={"date": "", "value": unit}, title=f"{choice} ({unit})")
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

    with st.expander("Show data table"):
        st.dataframe(data[["date", "value"]].sort_values("date", ascending=False),
                     hide_index=True, width="stretch")
    st.download_button("📥 Download this data (CSV)",
                       data[["date", "series_name", "value", "unit"]].to_csv(index=False).encode("utf-8"),
                       file_name=f"{choice.lower().replace(' ', '_')}.csv", mime="text/csv")

# ---- Tab 2: compare growth of several indicators ----
with tab_compare:
    st.write("Indicators have different units, so each one is **indexed to 100** at the start "
             "of the selected period. A value of 105 means 5% higher than at the start.")
    picks = st.multiselect("Indicators to compare", series_names, default=series_names[:2])

    if picks:
        comp = df_range[df_range["series_name"].isin(picks)].copy()
        first_values = comp.groupby("series_name")["value"].transform("first")
        comp["index"] = comp["value"] / first_values * 100

        fig2 = px.line(comp, x="date", y="index", color="series_name",
                       labels={"date": "", "index": "Index (start = 100)", "series_name": ""})
        fig2.add_hline(y=100, line_dash="dot", line_color="gray")
        fig2.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig2, width="stretch")

# Sidebar: about
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
### ℹ️ About
Monthly U.S. labor market indicators from the
[Bureau of Labor Statistics](https://www.bls.gov).
A GitHub Actions pipeline pulls fresh data from the BLS API every month.

**Built by:** Mahmuda Akhter Nishu
[LinkedIn](https://www.linkedin.com/in/mahmuda-nishu) ·
[GitHub](https://github.com/Mahmuda-Nishu)
"""
)
