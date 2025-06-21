import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
csv_url = "https://raw.githubusercontent.com/Aliidaher/Healthcare-Project/main/outbreaks.csv"
df = pd.read_csv(csv_url)

# Page config
st.set_page_config(page_title="Food Safety Dashboard", layout="wide")
st.title("🦠 Foodborne Illness Outbreaks in the U.S.")

# === Cleaning ===
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

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter the Data")
available_years = sorted(df["Year"].dropna().unique().astype(int))
available_states = sorted(df["State"].dropna().unique())
available_species = sorted(df["Species"].dropna().unique())
available_locations = sorted(df["Location"].dropna().unique())

selected_years = st.sidebar.slider("Select Year Range", min(available_years), max(available_years), (min(available_years), max(available_years)))
selected_state = st.sidebar.multiselect("Select State(s)", available_states, default=available_states)
selected_species = st.sidebar.multiselect("Select Pathogen(s)", available_species, default=available_species)
selected_location = st.sidebar.multiselect("Select Location(s)", available_locations, default=available_locations)

filtered_df = df[
    (df["Year"] >= selected_years[0]) & (df["Year"] <= selected_years[1]) &
    (df["State"].isin(selected_state)) &
    (df["Species"].isin(selected_species)) &
    (df["Location"].isin(selected_location))
]

# === Raw Data Preview ===
st.subheader("Raw Data Preview")
st.dataframe(filtered_df.head())

st.subheader("Summary Statistics")
st.write(filtered_df.describe(include='all'))

# === Trends Over Time ===
st.subheader("📈 Trends Over Time")
trend_data = filtered_df.groupby("Year")["Illnesses"].sum().reset_index()
fig = px.line(trend_data, x="Year", y="Illnesses", title="Total Foodborne Illnesses Reported by Year", markers=True)
st.plotly_chart(fig, use_container_width=True)

# === Exposure Location ===
st.subheader("🏠 Distribution by Exposure Location")
location_data = filtered_df.groupby("Location")["Illnesses"].sum().sort_values(ascending=False).reset_index()
fig = px.bar(location_data, x="Location", y="Illnesses", title="Total Illnesses by Exposure Location", height=500)
st.plotly_chart(fig, use_container_width=True)
st.caption("ℹ️ Gender and age data were not available in this dataset. Exposure location is used as a proxy for setting-related risk.")

# === U.S. Map ===
st.subheader("🗺️ U.S. Map of Foodborne Illnesses by State")
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
    'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}
state_data = filtered_df.groupby("State")["Illnesses"].sum().reset_index()
state_data["StateCode"] = state_data["State"].map(state_abbrev)
state_data = state_data.dropna(subset=["StateCode"])
fig = px.choropleth(state_data, locations="StateCode", locationmode="USA-states", color="Illnesses", scope="usa", color_continuous_scale="Reds")
st.plotly_chart(fig, use_container_width=True)

# === Pathogen Subtypes ===
st.subheader("🧬 Subtype Analysis – Most Common Pathogens")
species_data = filtered_df.dropna(subset=["Species"]).groupby("Species")["Illnesses"].sum().sort_values(ascending=False).reset_index().head(10)
fig = px.bar(species_data, x="Species", y="Illnesses", title="Top 10 Pathogens Causing Foodborne Illnesses", height=500)
st.plotly_chart(fig, use_container_width=True)

# === Severity by Pathogen ===
st.subheader("💉 Pathogen Severity – Hospitalization Rate")
severity_data = (
    filtered_df.dropna(subset=["Species", "Illnesses", "Hospitalizations"])
    .groupby("Species")[["Illnesses", "Hospitalizations"]]
    .sum()
    .reset_index()
)
severity_data["Hospitalization Rate (%)"] = (severity_data["Hospitalizations"] / severity_data["Illnesses"]) * 100
severity_data = severity_data.sort_values("Hospitalization Rate (%)", ascending=False).head(10)
fig = px.bar(severity_data, x="Species", y="Hospitalization Rate (%)", title="Top 10 Pathogens by Hospitalization Rate", height=500)
st.plotly_chart(fig, use_container_width=True)

# === Monthly Trends by Year ===
st.subheader("📅 Seasonal Trend of Foodborne Illnesses by Year")
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
monthly_trend = filtered_df.dropna(subset=["Month", "Year", "Illnesses"])
monthly_trend = monthly_trend.groupby(["Year", "Month"])["Illnesses"].sum().reset_index()
monthly_trend["Month"] = pd.Categorical(monthly_trend["Month"], categories=month_order, ordered=True)
monthly_trend = monthly_trend.sort_values(["Year", "Month"])
fig = px.line(monthly_trend, x="Month", y="Illnesses", color="Year", title="Monthly Trend of Illnesses by Year", markers=True)
st.plotly_chart(fig, use_container_width=True)

# === Average Monthly Illnesses (All Years) ===
st.subheader("📊 Average Illnesses by Month (Across All Years)")
monthly_avg = (
    filtered_df.dropna(subset=["Month", "Illnesses"])
    .groupby("Month")["Illnesses"]
    .mean()
    .reindex(month_order)
    .reset_index()
)
fig = px.bar(monthly_avg, x="Month", y="Illnesses", title="Average Number of Illnesses by Month", height=400)
st.plotly_chart(fig, use_container_width=True)

# === Food Type Breakdown ===
st.subheader("🍗 Food Type Breakdown – Top Foods Involved in Outbreaks")
df_food = filtered_df.copy()
df_food["Food"] = df_food["Food"].astype(str).str.strip().str.title()
df_food["Food"] = df_food["Food"].replace(["None", "Nan", "NaN", "Unspecified", "Unk", ""], pd.NA)
df_food = df_food.dropna(subset=["Food"])
food_data = df_food.groupby("Food")["Illnesses"].sum().sort_values(ascending=False).reset_index().head(10)
fig = px.bar(food_data, x="Food", y="Illnesses", title="Top 10 Food Items Associated with Outbreaks", height=500)
st.plotly_chart(fig, use_container_width=True)

st.subheader("🥧 Food Type Distribution (Top 10) – Pie Chart")

if not df_food.empty:
    food_totals = (
        df_food.groupby("Food")["Illnesses"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .head(10)
    )

    fig_pie = px.pie(
        food_totals,
        names="Food",
        values="Illnesses",
        title="Top 10 Food Categories Involved in Illnesses"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("No food data available for the selected filters.")

st.subheader("📉 Yearly Trends – Illnesses, Hospitalizations & Fatalities")

# Group and sum all severity indicators by year
yearly_summary = (
    filtered_df
    .groupby("Year")[["Illnesses", "Hospitalizations", "Fatalities"]]
    .sum()
    .reset_index()
)

# Melt for multiple lines on same chart
yearly_melted = yearly_summary.melt(id_vars="Year", value_vars=["Illnesses", "Hospitalizations", "Fatalities"],
                                     var_name="Outcome", value_name="Count")

fig = px.line(
    yearly_melted,
    x="Year",
    y="Count",
    color="Outcome",
    markers=True,
    title="Yearly Trends of Illnesses, Hospitalizations, and Fatalities"
)
st.plotly_chart(fig, use_container_width=True)
