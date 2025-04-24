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
# Table Descriptions
# -------------------------------
with st.expander("📚 Table Descriptions", expanded=False):
    st.markdown("""
**1. `crime_type`**  
Stores crime categories and descriptions.  
- `Crm_Cd` (NUMERIC): Unique crime code.  
- `Crm_Cd_Desc` (VARCHAR): Description of the crime.

**2. `location`**  
Details where crimes occurred.  
- `Premis_Cd` (NUMERIC): Code for the location type.  
- `Premis_Desc` (VARCHAR): Description of the premise (e.g., Street, Residence).

**3. `weapon`**  
Lists weapon types used in crimes.  
- `Weapon_Used_Cd` (NUMERIC): Weapon code.  
- `Weapon_Desc` (VARCHAR): Description of the weapon.

**4. `crime_data`**  
The main table containing crime incidents.  
- `DR_NO`: Unique report ID.  
- `Date_Rptd`, `DATE_OCC`: Dates of report and occurrence.  
- `TIME_OCC`: Time (24-hour format).  
- `AREA`, `AREA_NAME`: Geographic code and name.  
- `Crm_Cd`: Crime type code (FK to `crime_type`).  
- `Vict_Age`, `Vict_Sex`: Age and sex of the victim.  
- `Premis_Cd`: Location type (FK to `location`).  
- `Weapon_Used_Cd`: Weapon used (FK to `weapon`).  
- `Status`: Status code (e.g., IC, AO).  
- `LOCATION`, `LAT`, `LON`: Full location and coordinates.
    """)

# -------------------------------
# Table List Viewer
# -------------------------------
with st.expander("🗂 Available Tables", expanded=False):
    tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
    st.dataframe(tables_df, use_container_width=True)
    table_names = tables_df['name'].tolist()

# -------------------------------
# SQL Query Input
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
    except Exception as e:
        st.error(f"❌ Error: {e}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")

