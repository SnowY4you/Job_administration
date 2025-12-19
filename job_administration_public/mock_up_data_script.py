import sqlite3
import numpy as np
from datetime import datetime, timedelta

# --- Configuration ---
DB_NAME = "job_tracker.db"
TARGET_TOTAL_JOBS = 100

# The Key is the Category (Main Tag), the Value is the pool of job titles
TITTLES_CONFIG = {
    "devops": ["Systemingenjör", "System Integratör", "System Engineerare", "DevOps", "Site Reliability Engineer",
               "Platform Engineer", "Automation Engineer"],
    "it_service_specialist": ["System Owner", "IT Service Specialist", "Process Specialist", "IT Process Manager",
                              "Service Delivery Specialist", "IT Coordinator"],
    "it_team_lead": ["IT Team Lead", "Technical Lead", "Scrum Master", "Agile Coach"],
    "it_manager": ["Projektled", "IT Manager", "IT Driftchef", "Head of IT", "Operations Manager"],
    "first_line": ["IT-supporttekniker 1st line", "Servicedeskmedarbetare", "Helpdesk Support"],
    "second_line": ["IT-tekniker", "IT-tekniker 2nd line", "Supporttekniker", "Systemtekniker"],
    "on_site_support": ["On-site Supporttekniker", "Fälttekniker IT", "Local IT Support"]
}

COMPANIES = [
    "Saab", "Ericsson", "Scania", "Volvo", "ABB", "Spotify",
    "Sectra", "IFS", "Klarna",
    "Combitech", "Toyota Material Handling", "Siemens Energy", "H&M Group",
    "Skanska IT", "CGI", "Capgemini", "Afry", "Vattenfall", "Atea"
]
CITIES = ["Linköping", "Stockholm", "Gothenburg", "Norrköping", "Malmö", "Remote"]
STATUS_OPTIONS = ["Waiting for response", "Tests under review", "Interview 1 Scheduled", "Rejected",
                  "Rejected without response"]

tag_options = ["devops", "it_service_specialist", "it_manager", "second_line", "team_lead", "on_site_support", "first_line"]

# --- Helper Functions ---

def generate_monthly_distribution(total_target, min_per_month, max_per_month):
    """Generates a list of job counts per month that sum up to exactly total_target."""
    # Define range from April to November 2025
    months = np.arange('2025-04', '2025-12', dtype='datetime64[M]')
    n_months = len(months)

    # Initialize with random values within constraints
    counts = np.random.randint(min_per_month, max_per_month + 1, size=n_months)

    # Adjust counts iteratively until the sum matches the target (100)
    while counts.sum() != total_target:
        if counts.sum() < total_target:
            counts[np.random.randint(0, n_months)] += 1
        else:
            idx = np.random.randint(0, n_months)
            if counts[idx] > min_per_month:
                counts[idx] -= 1
    return list(zip(months, counts))


def generate_mock_data():
    """Main function to create the database and populate it with randomized data."""
    conn = sqlite3.connect(DB_NAME)

    # Ensure the database uses UTF-8 encoding for Swedish characters
    conn.execute("PRAGMA encoding = 'UTF-8';")
    cursor = conn.cursor()

    # Reset the database table
    cursor.execute("DROP TABLE IF EXISTS jobs")
    cursor.execute('''
                   CREATE TABLE jobs
                   (
                       id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                       job_tittle         TEXT NOT NULL,
                       company            TEXT NOT NULL,
                       city               TEXT,
                       date_of_apply      TEXT,
                       status             TEXT,
                       last_status_update TEXT,
                       tags               TEXT
                   )
                   ''')

    # Get the randomized monthly counts (between 10 and 18 per month)
    distribution = generate_monthly_distribution(TARGET_TOTAL_JOBS, 10, 18)

    # Extract the Keys (categories) from the configuration
    categories = list(TITTLES_CONFIG.keys())
    all_entries = []

    for month_dt, count in distribution:
        # Define the start and end of the specific month
        next_month = month_dt + np.timedelta64(1, 'M')
        days_in_month = np.arange(month_dt, next_month, dtype='datetime64[D]')

        # Pick 'count' random days within this specific month
        chosen_days = np.random.choice(days_in_month, size=count, replace=True)

        for day in chosen_days:
            # 1. Select the Category (The Dictionary KEY)
            category_key = np.random.choice(categories)

            # 2. Select a Title from the chosen category's list (The Dictionary VALUE)
            title = np.random.choice(TITTLES_CONFIG[category_key])

            # 3. Use the Category Key as the Tag (ensures perfect matching in Flask)
            tag = category_key

            apply_date_str = str(day)
            apply_dt = datetime.strptime(apply_date_str, '%Y-%m-%d')

            # Status update occurs 0-10 days after application
            update_gap = np.random.randint(0, 11)
            update_dt = apply_dt + timedelta(days=int(update_gap))

            all_entries.append((
                title,
                np.random.choice(COMPANIES),
                np.random.choice(CITIES),
                apply_date_str,
                np.random.choice(STATUS_OPTIONS),
                update_dt.strftime('%Y-%m-%d'),
                tag
            ))

    # Sort entries by application date to maintain a chronological timeline
    all_entries.sort(key=lambda x: x[3])

    # Bulk insert all generated jobs into the SQLite database
    cursor.executemany('''
                       INSERT INTO jobs (job_tittle, company, city, date_of_apply, status, last_status_update, tags)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       ''', all_entries)

    conn.commit()
    conn.close()

    print(f"✅ SUCCESS: Created {len(all_entries)} jobs in '{DB_NAME}'.")
    print(f"✅ LOGIC: Titles selected from values, categories used as tags.")
    print(f"✅ ENCODING: UTF-8 (Support for Swedish characters confirmed).")


if __name__ == "__main__":
    generate_mock_data()