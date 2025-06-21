import streamlit as st
import pandas as pd

# Load the dataset from the raw GitHub URL
csv_url = "https://raw.githubusercontent.com/Alidaher/Healthcare-Project/main/outbreaks.csv"
df = pd.read_csv(csv_url)

# Streamlit App
st.set_page_config(page_title="Food Safety Dashboard", layout="wide")
st.title("🦠 Foodborne Illness Outbreaks in the U.S.")

st.subheader("Raw Data Preview")
st.dataframe(df.head())

st.subheader("Summary Statistics")
st.write(df.describe(include='all'))
