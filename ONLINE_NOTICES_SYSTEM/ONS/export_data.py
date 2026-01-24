import pandas as pd
import sqlite3

# Connect to the SQLite database using the full path
conn = sqlite3.connect(r'E:\ONS\ONLINE_NOTICES_SYSTEM\db.sqlite3')  # Use raw string to avoid issues with backslashes

# Create a cursor object
cursor = conn.cursor()

# Check for existing tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print existing tables
print("Existing tables:", tables)

# Check if the desired table exists
if ('ONS_building_record',) in tables:
    # If it exists, read data into a DataFrame
    df = pd.read_sql_query("SELECT * FROM ONS_building_record", conn)

    # Export DataFrame to Excel
    df.to_excel('Exported_Data.xlsx', index=False)
    print("Data exported to output.xlsx")
else:
    print("Table 'ONS_building_record' does not exist.")

# Close the connection
conn.close()
