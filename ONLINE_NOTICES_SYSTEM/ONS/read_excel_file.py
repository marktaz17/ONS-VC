import pandas as pd
import sqlite3

# Load the Excel file
excel_file_path = r'E:\ONS\ONLINE_NOTICES_SYSTEM\Exported_Data.xlsx'
df = pd.read_excel(excel_file_path, sheet_name='Sheet1')

# Convert 'first_notice_date' to datetime and extract only the date
df['first_notice_date'] = pd.to_datetime(df['first_notice_date'], errors='coerce').dt.date
df['second_notice_date'] = pd.to_datetime(df['second_notice_date'], errors='coerce').dt.date
df['third_notice_date'] = pd.to_datetime(df['third_notice_date'], errors='coerce').dt.date
df['for_legal_notice_date'] = pd.to_datetime(df['for_legal_notice_date'], errors='coerce').dt.date

# Connect to SQLite database
conn = sqlite3.connect('db.sqlite3')

# Fetch existing IDs from the database
existing_ids = pd.read_sql_query("SELECT id FROM ONS_building_record", conn)

# Fill NaN values
df['final_status'] = df['final_status'].fillna('')  # Replace with appropriate value
df['status'] = df['status'].fillna('')  # Replace with appropriate value
df['created_at'] = df['created_at'].fillna('')  # Replace with appropriate value
df['occupancy_permit'] = df['occupancy_permit'].fillna('')  # Replace with appropriate value
df['electrical_permit'] = df['electrical_permit'].fillna('')  # Replace with appropriate value
df['comment'] = df['comment'].fillna('')  # Replace with appropriate value
df['for_legal_comment'] = df['for_legal_comment'].fillna('')  # Replace with appropriate value
df['second_comment'] = df['second_comment'].fillna('')  # Replace with appropriate value
df['third_comment'] = df['third_comment'].fillna('')  # Replace with appropriate value
df['lot_owner'] = df['lot_owner'].fillna('')  # Replace with appropriate value
df['contact_number'] = df['contact_number'].fillna('')  # Replace with appropriate value
df['building_owner'] = df['building_owner'].fillna('')  # Replace with appropriate value
df['address'] = df['address'].fillna('')  # Replace with appropriate value

# Filter the DataFrame to include only new records
df_new_records = df[~df['id'].isin(existing_ids['id'])]

# Insert the new records into the existing table
table_name = 'ONS_building_record'
df_new_records.to_sql(table_name, conn, if_exists='append', index=False)

# Close the connection
conn.close()
