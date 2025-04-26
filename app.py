import streamlit as st
import sqlite3
import pandas as pd

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(page_title="CrimeSync", layout="wide")
st.title("CrimeSync: Crime Data Explorer")

# -------------------------------
# Dataset Description
# -------------------------------
with st.expander("📄 Dataset Description", expanded=True):
    st.markdown("""
**Source**: [Crime Data from 2020 to Present](https://catalog.data.gov/dataset/crime-data-from-2020-to-present)  
**Provider**: Los Angeles Police Department (LAPD) via Data.gov  
**Standards**: Compliant with NIBRS (National Incident-Based Reporting System)

This dataset contains detailed incident-level crime reports collected by LAPD from 2020 to the present.  
It includes the type of crime, time/date, victim demographics, weapons used, and geolocation.

The schema is normalized into:
- `crime_data`: Facts table (date, victim, weapon, location, status)
- `crime_type`: Crime category descriptions
- `weapon`: Weapon type descriptions
- `location`: Premise/location type
    """)

# -------------------------------
# Connect to SQLite Database
# -------------------------------
@st.cache_resource
def get_connection():
    return sqlite3.connect("crime_data.db", check_same_thread=False)

conn = get_connection()

@st.cache_data(show_spinner=False)
def run_query(sql: str) -> pd.DataFrame:
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

- `Crm_Cd` (NUMERIC): Unique crime code  
- `Crm_Cd_Desc` (VARCHAR): Description of the crime
""",
        "location": """
**`location`**

- `Premis_Cd` (NUMERIC): Location type code  
- `Premis_Desc` (VARCHAR): Location description (e.g., Street, Residence)
""",
        "weapon": """
**`weapon`**

- `Weapon_Used_Cd` (NUMERIC): Weapon type code  
- `Weapon_Desc` (VARCHAR): Weapon description
""",
        "crime_data": """
**`crime_data`**

- `DR_NO`: Report ID  
- `Date_Rptd`, `DATE_OCC`: Date reported / occurred  
- `TIME_OCC`: Time of occurrence (24h)  
- `AREA`, `AREA_NAME`: Crime area code / name  
- `Crm_Cd`: Crime type (FK to `crime_type`)  
- `Vict_Age`, `Vict_Sex`: Victim age / sex  
- `Premis_Cd`: Location type (FK to `location`)  
- `Weapon_Used_Cd`: Weapon used (FK to `weapon`)  
- `Status`: Report status  
- `LOCATION`, `LAT`, `LON`: Address and coordinates
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
# Predefined Expert Queries
# -------------------------------
with st.expander("🧠 Explore Predefined Expert Queries", expanded=True):

    query_options = {
        "Top 10 Crime Types in 2023": {
            "query": """
SELECT ct.Crm_Cd_Desc AS Crime_Type, COUNT(*) AS Total_Incidents
FROM crime_data cd
JOIN crime_type ct ON cd.Crm_Cd = ct.Crm_Cd
WHERE substr(cd.DATE_OCC, 1, 4) = '2023'
GROUP BY ct.Crm_Cd_Desc
ORDER BY Total_Incidents DESC
LIMIT 10;
""",
            "description": "Shows the most frequently reported crime types in the year 2023."
        },
        "Top 5 Areas with Most Violent Crimes (2023)": {
            "query": """
SELECT 
    cd.AREA_NAME,
    COUNT(*) AS Total_Violent_Crimes,
    ROUND(AVG(cd.Vict_Age), 1) AS Avg_Victim_Age
FROM crime_data cd
JOIN crime_type ct ON cd.Crm_Cd = ct.Crm_Cd
WHERE substr(cd.DATE_OCC, 1, 4) = '2023'
  AND ct.Crm_Cd_Desc LIKE '%ASSAULT%'
GROUP BY cd.AREA_NAME
ORDER BY Total_Violent_Crimes DESC
LIMIT 5;
""",
            "description": "Top 5 areas with the most assault-related crimes in 2023 with victim age averages."
        },
        "Weapon Use by Area (Top 5 Areas, 2022–2023)": {
            "query": """
WITH TopAreas AS (
    SELECT AREA
    FROM crime_data
    WHERE Weapon_Used_Cd IS NOT NULL
      AND substr(DATE_OCC, 1, 4) IN ('2022', '2023')
    GROUP BY AREA
    ORDER BY COUNT(*) DESC
    LIMIT 5
)
SELECT 
    cd.AREA_NAME,
    w.Weapon_Desc,
    COUNT(*) AS Weapon_Incidents
FROM crime_data cd
JOIN weapon w ON cd.Weapon_Used_Cd = w.Weapon_Used_Cd
WHERE cd.Weapon_Used_Cd IS NOT NULL
  AND substr(cd.DATE_OCC, 1, 4) IN ('2022', '2023')
  AND cd.AREA IN (SELECT AREA FROM TopAreas)
GROUP BY cd.AREA_NAME, w.Weapon_Desc
ORDER BY cd.AREA_NAME, Weapon_Incidents DESC;
""",
            "description": "Weapon use breakdown across top 5 crime-heavy areas for 2022–2023."
        },
        "Crime Count by Gender in 2023": {
            "query": """
SELECT Vict_Sex, COUNT(*) AS Total_Reports
FROM crime_data
WHERE substr(DATE_OCC, 1, 4) = '2023'
GROUP BY Vict_Sex;
""",
            "description": "Shows how crime reports in 2023 break down by victim gender."
        },
        "Most Dangerous Times of Day (2023)": {
            "query": """
SELECT TIME_OCC / 100 AS Hour_Block, COUNT(*) AS Reports
FROM crime_data
WHERE substr(DATE_OCC, 1, 4) = '2023'
GROUP BY Hour_Block
ORDER BY Reports DESC
LIMIT 10;
""",
            "description": "Identifies hours of the day with highest crime activity in 2023."
        }
    }

    selected_example = st.selectbox("Choose a predefined query to run:", list(query_options.keys()))
    st.markdown(f"**Description:** {query_options[selected_example]['description']}")

    if st.button("Run Selected Query"):
        try:
            df = run_query(query_options[selected_example]["query"])
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# -------------------------------
# SQL Query Input
# -------------------------------
st.markdown("### 🛠️ Run Custom SQL Query")

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

st.markdown("""
**Created by**  
- AjitKumar Senthil Kumar  
- Marian Glen Louis  
- Vaishak Muralidharan
""")