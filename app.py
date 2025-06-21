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
