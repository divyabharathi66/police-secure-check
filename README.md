# police-secure-check
Initially i download my dataset csv file(traffic_stop_traffic_stop_with_vehicle_number .csv)
I create my new file police.ipynb file and i change the time stamp ,date actually it was in text type  and i convert it into date & time format.
I made another file main.py by using sqlalchemy i push csv.file into postgresql  
Finally i open another new file project1.py and import(streamlit,pandas,sqlalchemy,psycopg2,plotly.express) create connection to postgresql to fetch data database,
I kept title in streamlit"Securecheck:Police Check Post Digital Ldger"table have shown in streamlit  and quick matrix showing four column(total police stop, total arrest, total warning,drug related stop)Advance queries. 
I wrote 15 queries in postgre sql in the select box and i solved the queries by making query_map and i ran the query using st.button.
the same way i did complex queries(six queries)
Custom Natural Language Filter and input form for all fields(excluding output) 
Filter data for prediction and predict outcome and violation after that i create nature language summary
