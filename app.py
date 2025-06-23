# Final Streamlit Dashboard: Foodborne Illness Outbreaks in the U.S.
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
csv_url = "https://raw.githubusercontent.com/Aliidaher/Healthcare-Project/main/outbreaks.csv"
df = pd.read_csv(csv_url)

# Page config
st.set_page_config(page_title="Food Safety Dashboard", layout="wide")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    </style>
""", unsafe_allow_html=True)

# Header
st.image("https://upload.wikimedia.org/wikipedia/commons/6/65/US_FDA_logo.png", width=120)
st.title("\U0001F9A0 Foodborne Illness Outbreaks in the U.S.")
st.caption("A dashboard to explore patterns and trends in reported foodborne illness outbreaks.")

# Cleaning
cols_to_numeric = ["Year", "Illnesses", "Hospitalizations", "Fatalities"]
df.replace("None", pd.NA, inplace=True)
df.dropna(how='all', axis=1, inplace=True)
df[cols_to_numeric] = df[cols_to_numeric].apply(pd.to_numeric, errors='coerce')
cat_cols = ["State", "Location", "Food", "Species", "Ingredient"]
for col in cat_cols:
    df[col] = df[col].astype(str).str.strip().str.title()
df.drop_duplicates(inplace=True)
df = df[(df["Illnesses"] > 0) | (df["Hospitalizations"] > 0) | (df["Fatalities"] > 0)]
df = df[df["Year"] >= 1980]

# Sidebar
st.sidebar.header("\U0001F50D Filter the Data")
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

# Section: Raw Data
st.subheader("Raw Data & Summary")
st.dataframe(filtered_df.head())
st.write(filtered_df.describe(include='all'))

# Section 1: Trends
st.header("\U0001F4C8 Trends Over Time")
col1, col2 = st.columns(2)
with col1:
    trend = filtered_df.groupby("Year")["Illnesses"].sum().reset_index()
    fig = px.line(trend, x="Year", y="Illnesses", title="Illnesses by Year", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    outcome = filtered_df.groupby("Year")[["Illnesses", "Hospitalizations", "Fatalities"]].sum().reset_index()
    melted = outcome.melt(id_vars="Year", var_name="Type", value_name="Count")
    fig = px.line(melted, x="Year", y="Count", color="Type", title="Outcomes by Year", height=350)
    st.plotly_chart(fig, use_container_width=True)

# Section 2: Location & Map
st.header("\U0001F3E0 Exposure Location & Geography")
col3, col4 = st.columns(2)
with col3:
    loc = filtered_df.groupby("Location")["Illnesses"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(loc, x="Location", y="Illnesses", title="Illnesses by Exposure Location", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    abbrev = {...}  # use same state_abbrev dictionary here
    state_df = filtered_df.groupby("State")["Illnesses"].sum().reset_index()
    state_df["StateCode"] = state_df["State"].map(abbrev)
    state_df.dropna(subset=["StateCode"], inplace=True)
    fig = px.choropleth(state_df, locations="StateCode", locationmode="USA-states", color="Illnesses",
                        scope="usa", color_continuous_scale="Reds", title="Illnesses by State")
    st.plotly_chart(fig, use_container_width=True)

# Section 3: Pathogen Subtypes
st.header("\U0001F9EC Pathogens & Food Sources")
col5, col6 = st.columns(2)
with col5:
    species = filtered_df.dropna(subset=["Species"]).groupby("Species")["Illnesses"].sum().sort_values(ascending=False).reset_index().head(10)
    fig = px.bar(species, x="Species", y="Illnesses", title="Top 10 Pathogens", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col6:
    food = filtered_df.dropna(subset=["Food"])
    food = food.groupby("Food")["Illnesses"].sum().sort_values(ascending=False).reset_index().head(10)
    fig = px.pie(food, names="Food", values="Illnesses", title="Top 10 Foods Causing Illness")
    st.plotly_chart(fig, use_container_width=True)

# Section 4: Severity & Correlation
st.header("\U0001F489 Severity & Correlations")
col7, col8 = st.columns(2)
with col7:
    sev = filtered_df.dropna(subset=["Species", "Illnesses", "Hospitalizations"])
    sev = sev.groupby("Species")[["Illnesses", "Hospitalizations"]].sum().reset_index()
    sev["Rate"] = (sev["Hospitalizations"] / sev["Illnesses"]) * 100
    fig = px.bar(sev.sort_values("Rate", ascending=False).head(10), x="Species", y="Rate", title="Hospitalization Rate by Pathogen")
    st.plotly_chart(fig, use_container_width=True)

with col8:
    corr = filtered_df.dropna(subset=["Illnesses", "Hospitalizations", "Fatalities"])
    fig = px.scatter(corr, x="Illnesses", y="Hospitalizations", size="Fatalities", color="Species",
                     hover_data=["State", "Year", "Location"], title="Illnesses vs Hospitalizations (Size: Fatalities)")
    st.plotly_chart(fig, use_container_width=True)

# Section 5: Seasonal Heatmap
st.header("\U0001F4C5 Monthly Trends")
df_heat = filtered_df.dropna(subset=["Year", "Month", "Illnesses"])
df_heat = df_heat.groupby(["Year", "Month"])["Illnesses"].sum().reset_index()
df_pivot = df_heat.pivot(index="Month", columns="Year", values="Illnesses")

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(df_pivot, cmap="Reds", ax=ax)
st.pyplot(fig)

# Final Insights
st.header("\U0001F4DD Summary Insights")
st.markdown("""
- **Illnesses peaked** in the early 2000s.
- **Restaurants and private homes** are leading exposure locations.
- **Salmonella and Norovirus** are among the most reported pathogens.
- **July to September** see the highest seasonal peaks.
- **Dairy, seafood, and poultry** are top food sources in outbreaks.
- **Hospitalization rate** varies significantly by pathogen and exposure type.
""")
