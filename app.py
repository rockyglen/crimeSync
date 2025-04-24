import streamlit as st
import sqlite3
import pandas as pd

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(page_title="CrimeSync", layout="wide")
st.title("🚓 CrimeSync: Crime Data Explorer")

# -------------------------------
# Dataset Description
# -------------------------------
with st.expander("📄 Dataset Description", expanded=True):
    st.markdown("""
**Source**: [Crime Data from 2020 to Present](https://catalog.data.gov/dataset/crime-data-from-2020-to-present)  
**Provider**: Los Angeles Police Department (LAPD) via Data.gov  
**Standards**: Compliant with NIBRS (National Incident-Based Reporting System)

---

This dataset contains detailed incident-level crime reports collected by the Los Angeles Police Department (LAPD) from 2020 to the present. The data has been made publicly available to promote transparency, aid public safety analysis, and support data-driven decision-making by researchers, journalists, policymakers, and community members.

The database captures structured records of reported crimes, including:
- The **type of crime**
- **Time and date** of occurrence and report
- **Location** of the incident (down to latitude/longitude)
- **Victim demographics** (age, sex)
- **Weapons involved**
- **Administrative status** codes

To ensure data normalization and reduce redundancy, the database is implemented in **Boyce-Codd Normal Form (BCNF)** and split into logically related tables such as `crime_data`, `crime_type`, `location`, and `weapon`.

Key use cases for this database include:
- Analyzing crime trends over time or geography
- Understanding correlations between crime types and weapon use
- Investigating how location types affect crime frequency
- Generating custom reports through SQL-based queries

The `crime_data` table acts as the primary fact table and references normalized lookup tables to enable flexible, scalable analysis.
    """)

# -------------------------------
# Connect to SQLite Database
# -------------------------------
@st.cache_resource
def get_connection():
    return sqlite3.connect("crime_data.db", check_same_thread=False)

conn = get_connection()

# -------------------------------
# Cached SQL Query Execution
# -------------------------------
@st.cache_data(show_spinner=False)
def run_query(sql):
    return pd.read_sql_query(sql, conn)

# -------------------------------
# Interactive Table Descriptions
# -------------------------------
with st.expander("📚 Table Descriptions", expanded=False):
    selected_table = st.selectbox("Select a table to view its description:", [
        "crime_type", "location", "weapon", "crime_data"
    ])

    table_descriptions = {
        "crime_type": """
**`crime_type`**

Stores crime categories and descriptions.  
- `Crm_Cd` (NUMERIC): Unique crime code.  
- `Crm_Cd_Desc` (VARCHAR): Description of the crime.
""",
        "location": """
**`location`**

Details where crimes occurred.  
- `Premis_Cd` (NUMERIC): Code for the location type.  
- `Premis_Desc` (VARCHAR): Description of the premise (e.g., Street, Residence).
""",
        "weapon": """
**`weapon`**

Lists weapon types used in crimes.  
- `Weapon_Used_Cd` (NUMERIC): Weapon code.  
- `Weapon_Desc` (VARCHAR): Description of the weapon.
""",
        "crime_data": """
**`crime_data`**

Main table with crime incidents.  
- `DR_NO`: Unique report ID  
- `Date_Rptd`, `DATE_OCC`: Report and occurrence dates  
- `TIME_OCC`: 24-hour time of occurrence  
- `AREA`, `AREA_NAME`: Area codes and names  
- `Crm_Cd`: Crime code (FK to `crime_type`)  
- `Vict_Age`, `Vict_Sex`: Victim details  
- `Premis_Cd`: Premise code (FK to `location`)  
- `Weapon_Used_Cd`: Weapon code (FK to `weapon`)  
- `Status`: Status code (e.g., IC, AO)  
- `LOCATION`, `LAT`, `LON`: Location description and coordinates
"""
    }

    st.markdown(table_descriptions[selected_table])

# -------------------------------
# Table List Viewer
# -------------------------------
with st.expander("🗂 Available Tables", expanded=False):
    tables_df = run_query("SELECT name FROM sqlite_master WHERE type='table';")
    st.dataframe(tables_df, use_container_width=True)

# -------------------------------
# SQL Query Input
# -------------------------------
st.markdown("### 🔍 Run Custom SQL Query")

with st.form("sql_query_form"):
    query = st.text_area("Enter SQL Query", "SELECT * FROM crime_data LIMIT 10;")
    submit_query = st.form_submit_button("Run Query")

if submit_query:
    try:
        df = run_query(query)
        st.success("✅ Query executed successfully!")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error: {e}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")

