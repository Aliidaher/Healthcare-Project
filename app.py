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
