import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
csv_url = "https://raw.githubusercontent.com/Aliidaher/Healthcare-Project/main/outbreaks.csv"
df = pd.read_csv(csv_url)

# Page config
st.set_page_config(page_title="Food Safety Dashboard", layout="wide")

# === Sidebar ===
st.sidebar.image("https://i.imgur.com/o8QwN8F.png", width=150)
st.sidebar.title("🍽️ Food Safety Explorer")
st.sidebar.markdown("Use the filters below to explore the outbreak data.")

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

# === Title ===
st.title("🦠 Foodborne Illness Outbreaks in the U.S.")
st.markdown("Explore food safety data in the U.S. including illnesses, hospitalizations, fatalities, and pathogens.")

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

# === Heatmap (Calendar View) ===
st.subheader("📆 Calendar Heatmap – Monthly Illness Trends by Year")
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
df_heat = filtered_df.dropna(subset=["Month", "Year", "Illnesses"]).copy()
df_heat["Month"] = pd.Categorical(df_heat["Month"], categories=month_order, ordered=True)
pivot = df_heat.groupby(["Year", "Month"])["Illnesses"].sum().unstack().fillna(0)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.5, annot=True, fmt=".0f", ax=ax)
plt.title("Monthly Illness Count Heatmap by Year")
plt.xlabel("Month")
plt.ylabel("Year")
st.pyplot(fig)

# === Footer ===
st.markdown("---")
st.markdown("### 📌 Key Takeaways")
st.markdown("""
- 🗓️ **Illnesses peak in warmer months** (especially July & August)
- 🥩 **Restaurants and homes** are frequent outbreak locations
- 🧫 **Salmonella** and **Norovirus** are the most common pathogens
- ⚠️ Severity varies — some foods have **higher hospitalization risks**
- 🧭 Dashboard supports filtering by year, state, species, and more
""")
