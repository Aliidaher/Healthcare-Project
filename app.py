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

st.subheader("🧬 Subtype Analysis – Most Common Pathogens")

# Convert "Species" column to proper NaN if value is the string "nan" or "None"
df["Species"] = df["Species"].replace(["nan", "NaN", "None"], pd.NA)

# Drop missing values from Species column
df_species = df.dropna(subset=["Species"])

# Group and sort
species_data = (
    df_species.groupby("Species")["Illnesses"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Get top 10
top_species = species_data.head(10)

# Chart
fig = px.bar(
    top_species,
    x="Species",
    y="Illnesses",
    title="Top 10 Pathogens Causing Foodborne Illnesses",
    labels={"Illnesses": "Number of Illnesses"},
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("💉 Pathogen Severity – Hospitalization Rate")

# Drop missing values
df_severity = df.dropna(subset=["Species", "Illnesses", "Hospitalizations"])

# Group and calculate hospitalization rate
severity_data = (
    df_severity.groupby("Species")[["Illnesses", "Hospitalizations"]]
    .sum()
    .reset_index()
)
severity_data["Hospitalization Rate (%)"] = (severity_data["Hospitalizations"] / severity_data["Illnesses"]) * 100
severity_data = severity_data.sort_values("Hospitalization Rate (%)", ascending=False).head(10)

# Bar chart
fig = px.bar(
    severity_data,
    x="Species",
    y="Hospitalization Rate (%)",
    title="Top 10 Pathogens by Hospitalization Rate",
    labels={"Species": "Pathogen", "Hospitalization Rate (%)": "Hospitalization Rate (%)"},
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("📅 Seasonal Trend of Foodborne Illnesses by Year")

# Drop missing months/years
df_seasonal = df.dropna(subset=["Month", "Year", "Illnesses"])

# Ensure month order is correct
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

# Group by Year + Month
monthly_trend = (
    df_seasonal.groupby(["Year", "Month"])["Illnesses"]
    .sum()
    .reset_index()
)

# Convert Month to categorical to sort properly
monthly_trend["Month"] = pd.Categorical(monthly_trend["Month"], categories=month_order, ordered=True)
monthly_trend = monthly_trend.sort_values(["Year", "Month"])

# Plot line chart with one line per year
fig = px.line(
    monthly_trend,
    x="Month",
    y="Illnesses",
    color="Year",
    title="Monthly Trend of Illnesses by Year",
    markers=True,
    labels={"Illnesses": "Number of Illnesses"},
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Average Illnesses by Month (Across All Years)")

# Prepare month order
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

# Drop missing
df_avg_month = df.dropna(subset=["Month", "Illnesses"])

# Group and calculate average
monthly_avg = (
    df_avg_month.groupby("Month")["Illnesses"]
    .mean()
    .reindex(month_order)
    .reset_index()
)

# Bar chart
fig_avg = px.bar(
    monthly_avg,
    x="Month",
    y="Illnesses",
    title="Average Number of Illnesses by Month (All Years)",
    labels={"Illnesses": "Avg Illnesses"},
    height=400
)

st.plotly_chart(fig_avg, use_container_width=True)

st.subheader("🍗 Food Type Breakdown – Top Foods Involved in Outbreaks")

# Drop missing or vague entries
df_food = df.dropna(subset=["Food"])

# Clean whitespace, convert to title case
df_food["Food"] = df_food["Food"].astype(str).str.strip().str.title()

# Group and sum illnesses
food_data = (
    df_food.groupby("Food")["Illnesses"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Take top 10 food types
top_foods = food_data.head(10)

# Bar chart
fig_food = px.bar(
    top_foods,
    x="Food",
    y="Illnesses",
    title="Top 10 Food Items Associated with Outbreaks",
    labels={"Illnesses": "Number of Illnesses"},
    height=500
)

st.plotly_chart(fig_food, use_container_width=True)
