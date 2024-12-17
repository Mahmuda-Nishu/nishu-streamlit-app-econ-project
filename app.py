import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv("C:/Users/mnishu/Downloads/bls_data_project.csv")

# Dashboard Title
st.title("📊 US Labor Statistics Dashboard")
st.markdown("""
This dashboard visualizes labor statistics data from the **US Bureau of Labor Statistics (BLS)**.
Select a series below to view trends over time. Use the tools to explore and analyze the data! 📈
""")

# Dropdown to select a series
series_dict = {
    "CES0000000001": "Total Non-Farm Workers",
    "LNS14000000": "Unemployment Rate",
    "CES0500000003": "Average Weekly Hours of Production Employees",
    "CES3000000001": "Manufacturing Employment",
    "LNS14100000": "Employment-Population Ratio"
}
df['series_name'] = df['series_id'].map(series_dict)
selected_series_name = st.selectbox(
    "🔍 Select a Series to Visualize", 
    df['series_name'].unique()
)

# Filter data for the selected series
filtered_df = df[df['series_name'] == selected_series_name]

# Define dynamic labels and colors
if "Rate" in selected_series_name or "Ratio" in selected_series_name:
    y_label = "Value (%)"
    line_color = "#2ca02c"  # Green
else:
    y_label = "Value (in thousands)"
    line_color = "#1f77b4"  # Blue

# Plot the data
st.subheader(f"📈 Trends for **{selected_series_name}**")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=filtered_df, 
    x='year_month', 
    y='value', 
    marker='o', 
    color=line_color, 
    ax=ax,
    label=selected_series_name
)
ax.set_title(f"{selected_series_name} Over Time", fontsize=18, fontweight='bold')
ax.set_xlabel("Year-Month", fontsize=14, labelpad=10)
ax.set_ylabel(y_label, fontsize=14, labelpad=10)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12)
plt.grid(alpha=0.3, linestyle='--', linewidth=0.5)
st.pyplot(fig)

# Display raw data
st.subheader("🗂 Raw Data")
st.dataframe(filtered_df)

# Add data download button
st.markdown("### 📥 Download the Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
    help="Download the filtered data as a CSV file."
)

# Add a sidebar with additional information
st.sidebar.title("ℹ️ About This Dashboard")
st.sidebar.markdown("""
- **Source**: [US Bureau of Labor Statistics](https://www.bls.gov)
- **Metrics Included**:
    - Total Non-Farm Workers
    - Unemployment Rate
    - Average Weekly Hours of Production Employees
    - Manufacturing Employment
    - Employment-Population Ratio
- **Data Range**: Starting from 2022
- This dashboard is interactive: select a series and view trends or download the raw data.
""")

# Sidebar Styling
st.sidebar.markdown("### 🛠 Created By:")
st.sidebar.markdown("Nishu")
