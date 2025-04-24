import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(page_title="CrimeSync", layout="wide")
st.title("🚓 CrimeSync: Crime Data Explorer")
st.markdown("Explore and visualize your crime data interactively using SQL queries.")

# -------------------------------
# Connect to SQLite Database
# -------------------------------
@st.cache_resource
def get_connection():
    return sqlite3.connect("crime_data.db", check_same_thread=False)

conn = get_connection()

# -------------------------------
# View Table List
# -------------------------------
with st.expander("📋 View Tables in the Database", expanded=False):
    tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
    st.dataframe(tables_df, use_container_width=True)
    table_names = tables_df['name'].tolist()

# -------------------------------
# SQL Query Input Section
# -------------------------------
st.markdown("### 🔍 Run Custom SQL Query")

with st.form("sql_query_form"):
    query = st.text_area("Enter SQL Query", "SELECT * FROM crime_data LIMIT 10;")
    submit_query = st.form_submit_button("Run Query")

if submit_query:
    try:
        df = pd.read_sql_query(query, conn)
        st.success("✅ Query executed successfully!")
        st.dataframe(df, use_container_width=True)

        # -------------------------------
        # Optional Plot Section
        # -------------------------------
        num_cols = df.select_dtypes(include='number').columns.tolist()

        if len(num_cols) >= 2:
            st.markdown("### 📊 Visualize Result Data")

            with st.form("plot_form"):
                chart_type = st.selectbox("Select Chart Type", ["Scatter", "Bar", "Line"])
                x_axis = st.selectbox("X-axis", num_cols, key="x_axis_dropdown")
                y_axis = st.selectbox("Y-axis", num_cols, key="y_axis_dropdown")
                plot_btn = st.form_submit_button("Generate Plot")

            if plot_btn:
                if chart_type == "Scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                elif chart_type == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                elif chart_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")

