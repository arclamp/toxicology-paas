import pandas as pd
import streamlit as st

st.title("Toxicology - Prediction as a Service")

@st.cache(show_spinner=False)
def df_from_file(file) -> pd.DataFrame:
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

upload_container = st.empty()
data_file = upload_container.file_uploader('Select data', type=['csv', 'xlsx'])

if data_file:
    upload_container.empty()

    df = df_from_file(data_file)
    df[:20]
