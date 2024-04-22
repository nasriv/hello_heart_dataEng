## initialization scripts for postgres DB
import requests
import pandas as pd
import psycopg2

## init global params
global dbname, user, password, host, port

# Connection parameters
dbname = 'hhdb'
user = 'user'
password = 'password'
host = 'localhost'  # Assuming PostgreSQL is running locally on default port
port = '4510'  # Default PostgreSQL port


def fetch_data_init(api_url, limit, offset):
    ### data repo found at https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh/about_data
    #### department of health has a 1000 row limit on fetches
    all_data = []
    while True:
        try:
            response = requests.get(api_url, params={"$limit": limit, "$offset": offset})
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

            data = response.json()  # Convert response to JSON format
            if not data:
                break  # No more data available
            all_data.extend(data)
            offset += limit

        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            return None
    
    df = pd.DataFrame(all_data) # dump into dataframe and return

    ## filter out only specific columns to load
    cols_to_keep = ['state','date','inpatient_beds','inpatient_beds_used', 'all_pediatric_inpatient_beds', 'all_pediatric_inpatient_bed_occupied' ]
    df = df[cols_to_keep]

    ## replace NaN with zeros to insert into db
    df = df.fillna(0)

    return df

def init_table():
    # Connect to the database
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        print("Connected to the database")
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)
        exit()

    try:
        ## create cursor
        cursor = conn.cursor()

        ## drop exists if there
        cursor.execute("DROP TABLE IF EXISTS hospital_bed_usage")
        conn.commit()
        print("TABLE DROPPED...")

        # Define your SQL statement to create a table
        create_table_query = '''
            CREATE TABLE hospital_bed_usage (
                state TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                inpatient_beds INT,
                inpatient_beds_used INT,
                all_pediatric_inpatient_beds INT,
                all_pediatric_inpatient_bed_occupied INT,
                UNIQUE (state, date)
            )
        '''
        # Execute the SQL statement
        cursor.execute(create_table_query)
        conn.commit()
        print("Table created successfully!")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)

    finally:
    # Close database connection
        if conn:
            conn.close()
            print("PostgreSQL connection is closed")

def insert_db_rows(dataframe):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        ## create cursor
        cursor = conn.cursor()
        print("Connected to the database")
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)
        exit()

    for index, row in dataframe.iterrows():
        try:
            cursor.execute("""
                           INSERT INTO hospital_bed_usage
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, tuple(row))
            conn.commit()
        except psycopg2.OperationalError as error:
            print(f"Error: {error}")
            print(tuple(row))
            continue

    # Close database connection
    if conn:
        conn.close()
        print("PostgreSQL connection is closed")

## main program call
init_table()
df = fetch_data_init(
    api_url="https://healthdata.gov/resource/g62h-syeh.json",
    limit=1000,
    offset=0
    )

insert_db_rows(df)



