import psycopg2

# Connection parameters
dbname = 'hhdb'
user = 'user'
password = 'password'
host = 'localhost'  # Assuming PostgreSQL is running locally on default port
port = '4510'  # Default PostgreSQL port

# Connect to the database
try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    print("Connected to the database")
except psycopg2.Error as e:
    print("Unable to connect to the database:", e)
    exit()

# Create a cursor object
cur = conn.cursor()
cur.execute("""
            select * from hospital_bed_usage
            """)
print(cur.fetchall())

