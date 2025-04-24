import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(page_title="CrimeSync", layout="wide")
st.title("🚓 CrimeSync: Crime Data Explorer")

# -------------------------------
# Connect to SQLite Database
# -------------------------------
@st.cache_resource
def get_connection():
    return sqlite3.connect("crime_data.db", check_same_thread=False)


conn = get_connection()

# -------------------------------
# View Tables
# -------------------------------
st.markdown("### 📋 Tables in the Database")
tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
st.write(tables_df)
table_names = tables_df['name'].tolist()

# -------------------------------
# SQL Query Execution
# -------------------------------
st.markdown("### 🔍 Enter a SQL Query")
query = st.text_area("SQL Query", "SELECT * FROM crime_data LIMIT 10;")

if st.button("Run Query"):
    try:
        df = pd.read_sql_query(query, conn)
        st.success("✅ Query executed successfully!")
        st.dataframe(df, use_container_width=True)

        # -------------------------------
        # Optional Plot (if numeric data)
        # -------------------------------
        num_cols = df.select_dtypes(include='number').columns
        if len(num_cols) >= 2:
            st.markdown("### 📊 Visualize Data")
            x_axis = st.selectbox("X-axis", num_cols, key='x')
            y_axis = st.selectbox("Y-axis", num_cols, key='y')
            fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
