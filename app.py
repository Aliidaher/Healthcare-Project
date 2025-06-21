import streamlit as st
import pandas as pd

# Load the dataset from the raw GitHub URL
csv_url = "https://raw.githubusercontent.com/Aliidaher/Healthcare-Project/main/outbreaks.csv"

df = pd.read_csv(csv_url)

# Streamlit App
st.set_page_config(page_title="Food Safety Dashboard", layout="wide")
st.title("🦠 Foodborne Illness Outbreaks in the U.S.")

st.subheader("Raw Data Preview")
st.dataframe(df.head())

st.subheader("Summary Statistics")
st.write(df.describe(include='all'))
# ✅ Cleaning
df.replace("None", pd.NA, inplace=True)
df.dropna(how='all', axis=1, inplace=True)

cols_to_numeric = ["Year", "Illnesses", "Hospitalizations", "Fatalities"]
df[cols_to_numeric] = df[cols_to_numeric].apply(pd.to_numeric, errors='coerce')

cat_cols = ["State", "Location", "Food", "Species", "Ingredient"]
for col in cat_cols:
    df[col] = df[col].astype(str).str.strip().str.title()

df.drop_duplicates(inplace=True)
df = df[(df["Illnesses"] > 0) | (df["Hospitalizations"] > 0) | (df["Fatalities"] > 0)]
df = df[df["Year"] >= 1980]
import plotly.express as px

# === Trend Analysis ===
st.subheader("📈 Trends Over Time")

# Group by year and sum illnesses
trend_data = df.groupby("Year")["Illnesses"].sum().reset_index()

# Create line chart
fig = px.line(
    trend_data,
    x="Year",
    y="Illnesses",
    title="Total Foodborne Illnesses Reported by Year",
    markers=True,
    labels={"Illnesses": "Number of Illnesses", "Year": "Year"}
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🏠 Distribution by Exposure Location")

location_data = df.groupby("Location")["Illnesses"].sum().sort_values(ascending=False).reset_index()

fig = px.bar(
    location_data,
    x="Location",
    y="Illnesses",
    title="Total Illnesses by Exposure Location",
    labels={"Illnesses": "Number of Illnesses"},
    height=500
)

st.plotly_chart(fig, use_container_width=True)
st.caption("ℹ️ Gender and age data were not available in this dataset. Exposure location is used as a proxy for setting-related risk.")

# Mapping of state names to 2-letter codes
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
    'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Group by state and sum illnesses
state_data = df.groupby("State")["Illnesses"].sum().reset_index()

# Add state code column for Plotly
state_data["StateCode"] = state_data["State"].map(state_abbrev)

# Remove rows with states not in the mapping (e.g., Guam, Puerto Rico)
state_data = state_data.dropna(subset=["StateCode"])

# Plotly choropleth map
st.subheader("🗺️ U.S. Map of Foodborne Illnesses by State")

fig = px.choropleth(
    state_data,
    locations="StateCode",
    locationmode="USA-states",
    color="Illnesses",
    scope="usa",
    color_continuous_scale="Reds",
    title="Total Foodborne Illnesses by State"
)

st.plotly_chart(fig, use_container_width=True)


