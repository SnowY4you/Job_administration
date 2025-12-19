import sqlite3
from datetime import date
import sys
import json
import os

# --- CONFIGURATION ---
# Using the absolute path you provided to ensure we hit the correct file
DB_NAME = r'C:\Users\svanb\OneDrive\Python\Job_administration\job_administration_public\job_tracker.db'

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def import_jobs_from_json(file_path):
    """
    Reads a JSON file and inserts data into the 7 data columns of the 'jobs' table.
    (The 8th column, 'id', is handled automatically by SQLite).
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at path: {file_path}")
        return

    conn = get_db_connection()
    today_str = date.today().isoformat()
    success_count = 0
    failure_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ File Error: Could not read JSON. Details: {e}")
        conn.close()
        return

    if not isinstance(data, list):
        print("❌ Data Structure Error: JSON must be a list of job objects.")
        conn.close()
        return

    try:
        for i, job_data in enumerate(data):
            # 1. Extract required fields
            job_tittle = job_data.get('job_tittle')
            company = job_data.get('company')

            if not job_tittle or not company:
                print(f"🛑 Skipped Record {i + 1}: Missing job_tittle or company.")
                failure_count += 1
                continue

            # 2. Extract optional fields with defaults
            city = job_data.get('city', 'Unknown')
            date_of_apply = job_data.get('date_of_apply', today_str)
            status = job_data.get('status', 'Applied')
            tags = job_data.get('tags', '')

            # 3. Handle last_status_update logic
            last_status_update = job_data.get('last_status_update')
            if not last_status_update or last_status_update == "":
                last_status_update = date_of_apply

            # 4. Execute Insert (7 columns of data)
            conn.execute('''
                INSERT INTO jobs 
                (job_tittle, company, city, date_of_apply, status, last_status_update, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (job_tittle, company, city, date_of_apply, status, last_status_update, tags))

            success_count += 1

        conn.commit()
        print(f"\n=== Import Summary for {DB_NAME} ===")
        print(f"✅ Successfully inserted: {success_count} jobs.")
        print(f"❌ Skipped/Failed: {failure_count}")

    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Database Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python json_importer.py <your_file.json>')
        sys.exit(1)

    import_jobs_from_json(sys.argv[1])