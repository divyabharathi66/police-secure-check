import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import plotly.express as px

def create_connection():

    connection = psycopg2.connect(  
           
        host = "localhost",
        port = 5432,
        user ="postgres",
        password = "Divya$66",
        database ="python_db",
             )  
    return connection 

#Fetch data from database
def fetch_data(query):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    colu=[col[0] for col in cursor.description]
                    
                    result = cursor.fetchall()
                    df = pd.DataFrame(result, columns=colu)
                    return df
            finally:
                 connection.close()
        else:
            return pd.DataFrame()

#Stremlit UI
st.set_page_config(page_title = "securecheck police Dashboard", layout="wide")
st.title("securecheck:police check post Digital Ldger")
st.markdown("Real.time monitoring and insights for law emforcement")

#show full table
st.header("police log overview")
data = fetch_data("SELECT * FROM policecheck")
st.dataframe(data,use_container_width=True)

#Quick Matrics
st.header("key Metrial")
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_stops = data.shape[0]
    st.metric("Total policestops",total_stops)
with col2:
    arrests = data[data['stop_outcome'].str.contains("warning",case=False,na=False)].shape[0]
    st.metric("Total Arrests",arrests)
with col3:
    warnings = data[data['stop_outcome'].str.contains("warning",case=False,na=False)].shape[0]
    st.metric("Total warnings",warnings)  
with col4:
    drug_related = data[data['drugs_related_stop']==1].shape[0]
    st.metric("Drug Related stops",drug_related)
              
#Advanced Queries
st.header("Advanced Insights")
 
selected_query = st.selectbox("select Query to Run",[ 
    "Top 10 Vehicle_Number Involved Drug_Related_Stops",
    "Vehicle Most Frequently Searched",
    "Driver Age Group Had The Highest Arrest Rate",
    "The Gender Distribution Of Drivers Stopped In Each Country",
    "Race And Gender Combination Has The Highest Search Rate",
    "Time Of Day Sees The Most Traffic Stops",
    "The Average Stop Duration For Different Violations",
    "Stops During The Night Lead To Arrests",
    "Violations Most Associated With Searches Or Arrests",
    "Violations Are Most Common Among Younger Drivers (<25)",
    "The Countries Report The Highest Rate Of Drug-Related Stops",
    "The Arrest Rate By Country And Violation",
    "The Country Has The Most Stops With Search Conducted",
    "A Violation That Rarely Results In Search Or Arrest"
 ])

query_map ={
    "Top 10 Vehicle_Number Involved Drug_Related_Stops": "SELECT vehicle_number, COUNT(*) AS stop_count FROM  policecheck WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY stop_count DESC LIMIT 10;",
    "Vehicle Most Frequently Searched":"SELECT vehicle_number, COUNT(*) AS search_count FROM  policecheck GROUP BY vehicle_number ORDER BY search_count DESC LIMIT 1;",
    "Driver Age Group Had The Highest Arrest Rate": """
       SELECT age_group,
       COUNT(*) FILTER (WHERE stop_outcome = 'Arrest') * 1.0 / COUNT(*) AS arrest_rate
FROM (
    SELECT *,
           CASE
               WHEN driver_age < 20 THEN 'Under 20'
               WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
               WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
               WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
               WHEN driver_age BETWEEN 50 AND 59 THEN '50-59'
               ELSE '60+'
           END AS age_group
    FROM policecheck
) grouped
GROUP BY age_group
ORDER BY arrest_rate DESC
LIMIT 1; """,
  "The Gender Distribution Of Drivers Stopped In Each Country": """
        SELECT driver_gender, COUNT(*) AS total_stops 
        FROM policecheck 
        GROUP BY driver_gender;
    """,
  "Race And Gender Combination Has The Highest Search Rate": """
        SELECT driver_race, driver_gender, COUNT(*) AS search_count 
        FROM policecheck 
        WHERE search_conducted = TRUE 
        GROUP BY driver_race, driver_gender 
        ORDER BY search_count DESC 
        LIMIT 1;
    """,
  "Time Of Day Sees The Most Traffic Stops": """
        SELECT time_of_day,
       COUNT(*) AS total_stops
FROM (
    SELECT *,
           CASE
               WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 6 AND 11 THEN 'Morning'
               WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 12 AND 17 THEN 'Afternoon'
               WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 18 AND 21 THEN 'Evening'
               ELSE 'Night'
           END AS time_of_day
    FROM policecheck
) categorized
GROUP BY time_of_day
ORDER BY total_stops DESC
LIMIT 1;
    """,
     "The Average Stop Duration For Different Violations": """
        SELECT violation,
       AVG(
           CASE stop_duration
               WHEN '0-15 Min' THEN 7.5
               WHEN '16-30 Min' THEN 23
               WHEN '31-45 Min' THEN 38
               WHEN '46-60 Min' THEN 53
               WHEN '60+ Min' THEN 75
               ELSE NULL
           END
       ) AS avg_duration_minutes
FROM policecheck
GROUP BY violation
ORDER BY avg_duration_minutes DESC; """,

"Stops During The Night Lead To Arrests":"""
  WITH categorized AS (
    SELECT *,
        CASE
            WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 6 AND 11 THEN 'Morning'
            WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 12 AND 17 THEN 'Afternoon'
            WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 18 AND 21 THEN 'Evening'
            ELSE 'Night'
        END AS time_of_day
    FROM policecheck
),
arrest_rates AS (
    SELECT
        time_of_day,
        COUNT(*) FILTER (WHERE is_arrested) * 1.0 / COUNT(*) AS arrest_rate
    FROM categorized
    GROUP BY time_of_day
),
night_vs_rest AS (
    SELECT
        (SELECT arrest_rate FROM arrest_rates WHERE time_of_day = 'Night') AS night_rate,
        (SELECT MAX(arrest_rate) FROM arrest_rates WHERE time_of_day != 'Night') AS max_other_rate
)
SELECT
    CASE
        WHEN night_rate > max_other_rate THEN 'Yes'
        ELSE 'No'
    END AS night_more_likely_to_lead_to_arrest
FROM night_vs_rest;""",

    "Violations Most Associated With Searches Or Arrests": """
        SELECT 
    violation,
    CASE
        WHEN COUNT(*) FILTER (WHERE is_arrested) > COUNT(*) FILTER (WHERE search_conducted)
            THEN 'Arrest'
        WHEN COUNT(*) FILTER (WHERE search_conducted) > COUNT(*) FILTER (WHERE is_arrested)
            THEN 'Search'
        ELSE 'Equal'
    END AS most_common_outcome
FROM policecheck
GROUP BY violation
ORDER BY violation; """,
 
    "Violations Are Most Common Among Younger Drivers (<25)": """
        SELECT violation, COUNT(*) AS stop_count
        FROM policecheck
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY stop_count DESC
        LIMIT 10;
    """,
"The Countries Report The Highest Rate Of Drug-Related Stops": """
        SELECT country_name, COUNT(*) AS drug_related_stops
FROM policecheck
GROUP BY country_name
ORDER BY drug_related_stops DESC
LIMIT 1;
    """,
    "The Arrest Rate By Country And Violation": """
        SELECT
    country_name,
    violation,
    COUNT(*) AS arrest_count
FROM
    policecheck
GROUP BY
    country_name, violation
ORDER BY
    country_name, arrest_count DESC;

    """,
     "The Country Has The Most Stops With Search Conducted": """
        SELECT
  country_name,
  COUNT(*) AS searches_conducted
FROM
  policecheck
WHERE
  search_conducted = TRUE
GROUP BY
  country_name
ORDER BY
  searches_conducted DESC
LIMIT 1;
    """,
    "A Violation That Rarely Results In Search Or Arrest": """
       SELECT 
    violation,
    CASE
        WHEN COUNT(*) FILTER (WHERE is_arrested) < COUNT(*) FILTER (WHERE search_conducted)
            THEN 'Arrest'
        WHEN COUNT(*) FILTER (WHERE search_conducted) < COUNT(*) FILTER (WHERE is_arrested)
            THEN 'Search'
        ELSE 'Equal'
    END AS most_rarely_outcome
FROM policecheck
GROUP BY violation
ORDER BY violation;  """

}

if st.button("Run Query"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No resultfound forthe selected query.")

#Complex Queries
st.header("Complex Insights")
 
selected_query = st.selectbox("select Query to Run",[ 
"Yearly Breakdown of Stops And Arrests By Country",
"Driver Violation Trends Based On Age And Race",
"Time Period Analysis Of Stops",
"Violations With High Search And Arrest Rates",
 "Driver Demographics By Country",
"Top 5 Violations With Highest Arrest Rates"
])

query_map ={
"Yearly Breakdown of Stops And Arrests By Country":"""
SELECT 
    year,
    country_name,
    total_stops,
    total_arrests,
    ROUND(100.0 * total_arrests / total_stops, 2) AS arrest_rate_percent,
    SUM(total_arrests) OVER (PARTITION BY year) AS yearly_total_arrests,
    RANK() OVER (PARTITION BY year ORDER BY total_arrests DESC) AS arrest_rank_in_year
FROM (
    SELECT
        EXTRACT(YEAR FROM stop_date) AS year,
        country_name,
        COUNT(*) AS total_stops,
        COUNT(*) FILTER (WHERE is_arrested) AS total_arrests
    FROM policecheck
    GROUP BY EXTRACT(YEAR FROM stop_date), country_name
) subquery
ORDER BY year, arrest_rank_in_year;""",

"Driver Violation Trends Based On Age And Race":"""
 SELECT 
    pc.driver_race,
    CASE 
        WHEN pc.driver_age BETWEEN 16 AND 25 THEN '16-25'
        WHEN pc.driver_age BETWEEN 26 AND 40 THEN '26-40'
        WHEN pc.driver_age BETWEEN 41 AND 60 THEN '41-60'
        ELSE '60+'
    END AS age_group,
    COUNT(pc.violation) AS total_violations
FROM (
    SELECT 
        violation,
        driver_age,
        driver_race
    FROM policecheck
    WHERE violation IS NOT NULL 
      AND driver_age IS NOT NULL 
      AND driver_race IS NOT NULL
) AS pc
GROUP BY pc.driver_race, age_group
ORDER BY pc.driver_race, age_group;""",

"Time Period Analysis Of Stops":"""
SELECT
  EXTRACT(YEAR FROM stop_date) AS year,
  EXTRACT(MONTH FROM stop_date) AS month,
  EXTRACT(HOUR FROM stop_time) AS hour,
  COUNT(*) AS num_stops
FROM
  policecheck
GROUP BY
  EXTRACT(YEAR FROM stop_date),
  EXTRACT(MONTH FROM stop_date),
  EXTRACT(HOUR FROM stop_time)
ORDER BY
  year, month, hour;""",

"Violations With High Search And Arrest Rates":"""
SELECT *,
       RANK() OVER (ORDER BY search_rate DESC) AS search_rank,
       RANK() OVER (ORDER BY arrest_rate DESC) AS arrest_rank
FROM (
  SELECT
    violation,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE search_conducted) * 100.0 / COUNT(*) AS search_rate,
    COUNT(*) FILTER (WHERE is_arrested) * 100.0 / COUNT(*) AS arrest_rate
  FROM policecheck
  GROUP BY violation
) sub;""",
"Driver Demographics By Country":"""
SELECT 
    country_name,
    CASE 
        WHEN driver_age < 18 THEN 'Under 18'
        WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
        WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
        WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
        ELSE '60+' 
    END AS age_group,
    driver_gender,
    driver_race,
    COUNT(*) AS driver_count
FROM 
    policecheck
GROUP BY 
    country_name,
    age_group,
    driver_gender,
    driver_race
ORDER BY 
    country_name, age_group, driver_gender,driver_race;""",

"Top 5 Violations With Highest Arrest Rates":"""
SELECT 
    violation,
    COUNT(*) AS total_violations,
    SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(100.0 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) / COUNT(*), 2) AS arrest_rate_percentage
FROM 
    policecheck
GROUP BY 
    violation
HAVING 
    COUNT(*) > 0
ORDER BY 
    arrest_rate_percentage DESC
LIMIT 5;"""
}
if st.button("Run Query", key="run_query_btn"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No resultfound forthe selected query.")


st.markdown("---")
st.markdown("Built with ❤️ for Law Enforcement by SecureCheck")
st.header("Custom Natural Language Filter")

st.markdown("Fill in the details below to get a natural language prediction of the stop outcome based on existing data.")

st.header("Add New SecureCheck & Predict Outcome and Violation")

# Input form for all fields (excluding output)
with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a search conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it drug related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    violation = st.text_input("Violation")
    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

    if submitted:
        # Filter data for prediction
        filter_data = data[
            (data['driver_gender'] == driver_gender) &
            (data['driver_age'] == driver_age) &
            (data['search_conducted'] == int(search_conducted)) &
            (data['stop_duration'] == stop_duration) &
            (data['drugs_related_stop'] == int(drugs_related_stop)) &
            (data['violation'] == violation)
        
]

        # Predict stop_outcome and violation
        if not filter_data.empty:
            predicted_outcome = filter_data['stop_outcome'].mode()[0]
            predicted_violation = filter_data['violation'].mode()[0]
        else:
            predicted_outcome = "warning"  # Default fallback
            predicted_violation = "speeding"  # Default fallback

        # Natural language summary
        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug related" if int(drugs_related_stop) else "was not drug related"

        st.markdown("**Prediction Summary**")
        st.markdown(f"""
- **Predicted Violation**: {predicted_violation}  
- **Predicted Outcome**: {predicted_outcome}  

🚗 A {driver_age}-year-old {driver_gender} driver was stopped for **{predicted_violation}** at **{stop_time.strftime('%I:%M %p')}**.  
{search_text}, and the stop {drug_text}.  
**Stop Duration**: {stop_duration}  
**Vehicle Number**: {vehicle_number}  
        """)
