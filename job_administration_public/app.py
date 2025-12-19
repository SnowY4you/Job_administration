from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import date, datetime
import json
import io
import os
import subprocess

app = Flask(__name__)
DB_NAME = 'job_tracker.db'


# --- 1. Database & Utility Functions ---

def init_db():
    """Initializes the database schema if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS jobs
              (
                  id                 INTEGER PRIMARY KEY,
                  job_tittle         TEXT NOT NULL,
                  company            TEXT NOT NULL,
                  city               TEXT,
                  date_of_apply      TEXT,
                  status             TEXT,
                  last_status_update TEXT,
                  tags               TEXT
              )
              ''')
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def calculate_time_waiting(start_date_str):
    """Calculates elapsed time in a human-readable format."""
    today = date.today()
    try:
        start_date = date.fromisoformat(start_date_str)
        diff = (today - start_date).days
        if diff < 0: return "Future Date"
        if diff < 7:
            return f"{diff} days"
        elif diff < 30:
            return f"{diff // 7} weeks, {diff % 7} days"
        else:
            return f"approx. {diff // 30} months"
    except:
        return "N/A"


# --- 2. Primary Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    TAG_OPTIONS = ["devops", "it_service_specialist", "it_manager", "second_line", "team_lead", "on_site_support", "first_line"]
    search_query = request.args.get('search', '')

    # Handle Adding New Job
    if request.method == 'POST' and 'job_tittle' in request.form:
        job_tittle = request.form['job_tittle']
        company = request.form['company']
        city = request.form['city']
        date_of_apply = request.form['date_of_apply']
        status = request.form.get('status', 'Waiting for response')
        tags = ", ".join(request.form.getlist('tags'))

        conn.execute('''
                     INSERT INTO jobs (job_tittle, company, city, date_of_apply, status, last_status_update, tags)
                     VALUES (?, ?, ?, ?, ?, ?, ?)
                     ''', (job_tittle, company, city, date_of_apply, status, date_of_apply, tags))
        conn.commit()
        return redirect(url_for('index'))

    # Handle Search vs All
    if search_query:
        query = "SELECT * FROM jobs WHERE job_tittle LIKE ? OR company LIKE ? ORDER BY date_of_apply DESC"
        jobs_from_db = conn.execute(query, (f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        jobs_from_db = conn.execute('SELECT * FROM jobs ORDER BY date_of_apply DESC').fetchall()

    # Data Processing
    jobs = []
    status_counts = {}
    tag_counts = {tag: 0 for tag in TAG_OPTIONS}
    monthly_counts = {}
    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'Maj', '06': 'Jun',
        '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Okt', '11': 'Nov', '12': 'Dec'
    }

    for row in jobs_from_db:
        j = dict(row)
        j['time_waiting'] = calculate_time_waiting(j['date_of_apply'])
        j['time_since_status'] = calculate_time_waiting(j['last_status_update'])
        jobs.append(j)

        # Statistics Tallying
        s = j.get('status', 'Waiting for response')
        status_counts[s] = status_counts.get(s, 0) + 1

        if j.get('tags'):
            current_tags = [t.strip() for t in j['tags'].split(',')]
            for t in current_tags:
                if t in tag_counts: tag_counts[t] += 1

        try:
            m_num = j['date_of_apply'][5:7]
            year = j['date_of_apply'][:4]
            key = f"{month_names[m_num]} {year}"
            monthly_counts[key] = monthly_counts.get(key, 0) + 1
        except:
            pass

    # Percentage Calculations
    total_jobs = len(jobs)
    status_percentages = {}
    if total_jobs > 0:
        for status, count in status_counts.items():
            status_percentages[status] = f"({(count / total_jobs) * 100:.1f}%)"

    conn.close()
    return render_template('index.html',
                           jobs=jobs,
                           tag_options=TAG_OPTIONS,
                           total_jobs=total_jobs,
                           status_counts=status_counts,
                           tag_counts=tag_counts,
                           status_percentages=status_percentages,
                           monthly_counts=monthly_counts,
                           search_query=search_query)


# --- 3. Export & Management Routes ---

@app.route('/monthly_report_json', methods=['POST'])
def monthly_report_json():
    selected = request.form.get('month_selection')
    if not selected: return redirect(url_for('index'))
    conn = get_db_connection()
    all_jobs = [dict(row) for row in conn.execute('SELECT * FROM jobs').fetchall()]
    conn.close()

    month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'Maj': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                 'Sep': '09', 'Okt': '10', 'Nov': '11', 'Dec': '12'}
    m_name, year = selected.split(' ')
    target = f"{year}-{month_map[m_name]}"

    filtered = [j for j in all_jobs if j['date_of_apply'].startswith(target)]
    output = json.dumps(filtered, indent=4, ensure_ascii=False)
    return send_file(io.BytesIO(output.encode('utf-8')), mimetype='application/json', as_attachment=True,
                     download_name=f"Report_{selected}.json")

@app.route('/render_report', methods=['POST'])
def render_report():
    from fpdf import FPDF
    start, end = request.form.get('start_date'), request.form.get('end_date')

    conn = get_db_connection()
    data = conn.execute("""
        SELECT * FROM jobs 
        WHERE date_of_apply BETWEEN ? AND ? 
        ORDER BY date_of_apply ASC
    """, (start, end)).fetchall()
    conn.close()

    # --- Prepare PDF ---
    pdf = FPDF()
    pdf.add_page()

    pdf = FPDF()
    pdf.add_page()

    # Load Unicode font properly
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")

    pdf.add_font("DejaVu", "", os.path.join(font_dir, "DejaVuSansCondensed.ttf"))
    pdf.add_font("DejaVu", "B", os.path.join(font_dir, "DejaVuSansCondensed-Bold.ttf"))

    pdf.set_font("DejaVu", "", 12)

    # Month names
    month_names = {
        1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
        7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"
    }

    # Group applications by year → month
    applications_by_year_month = {}

    for app in data:
        date = datetime.strptime(app['date_of_apply'], '%Y-%m-%d')
        year, month = date.year, date.month

        applications_by_year_month.setdefault(year, {})
        applications_by_year_month[year].setdefault(month, [])
        applications_by_year_month[year][month].append(app)

    # --- Build PDF content ---
    for year in sorted(applications_by_year_month.keys()):
        for month in sorted(applications_by_year_month[year].keys()):
            apps = applications_by_year_month[year][month]
            month_name = month_names[month]
            total = len(apps)

            # Header
            pdf.set_font("DejaVu", "B", 14)
            header = f"===== {month_name} {year} - Total Applications: {total} ====="
            pdf.cell(0, 10, header, new_x="LMARGIN", new_y="NEXT")

            # Table header...
            pdf.set_font("DejaVu", "B", 10)
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(40, 8, "Date", border=1, fill=True)
            pdf.cell(80, 8, "Job Title", border=1, fill=True)
            pdf.cell(70, 8, "Company", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

            # Table rows
            pdf.set_font('', '', 10)
            for app in apps:
                pdf.cell(40, 8, app['date_of_apply'], border=1)
                pdf.cell(80, 8, app['job_tittle'], border=1)
                pdf.cell(70, 8, app['company'], border=1, ln=True)

            pdf.ln(5)  # spacing after each month

    # --- Output PDF ---
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)

    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name="Activity_Report.pdf"
    )


@app.route('/upload_to_af', methods=['POST'])
def upload_to_af():
    start, end = request.form.get('start_date'), request.form.get('end_date')
    conn = get_db_connection()
    jobs = [dict(row) for row in
            conn.execute("SELECT * FROM jobs WHERE date_of_apply BETWEEN ? AND ?", (start, end)).fetchall()]
    conn.close()
    if jobs: subprocess.Popen(['python', 'af_uploader.py', json.dumps(jobs)])
    return redirect(url_for('index'))


@app.route('/update_status/<int:job_id>', methods=['POST'])
def update_status(job_id):
    new_status = request.form.get('status')
    conn = get_db_connection()
    conn.execute('UPDATE jobs SET status = ?, last_status_update = ? WHERE id = ?',
                 (new_status, date.today().isoformat(), job_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/backup_db')
def backup_db():
    with open(DB_NAME, 'rb') as f:
        data = f.read()
    return send_file(io.BytesIO(data), mimetype='application/x-sqlite3', as_attachment=True,
                     download_name=f"backup_{date.today()}.db")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)