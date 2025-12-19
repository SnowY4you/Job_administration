<!-- TOC -->
* [Job Application Tracker & AF-Auto](#job-application-tracker--af-auto)
  * [Version](#Version)
  * [Features](#features)
  * [Requirements & Installation](#requirements--installation)
    * [Plugins](#plugins)
  * [How to Get Started](#how-to-get-started)
    * [Starting the App](#starting-the-app)
    * [Adding Data](#adding-data)
    * [Using AF-Auto (🔗 AF Button)](#using-af-auto--af-button)
  * [Updating & Maintenance](#updating--maintenance)
    * [Updating Status](#updating-status)
    * [Backup](#backup)
    * [Deleting Entries](#deleting-entries)
    * [Known Limitations](#known-limitations)
  * [Licence Summary](#licence-summary)
  * [Author](#author)
  * [Changelog](#changelog)
    * [1.2.0 – (2025-12-19)](#120--2025-12-19)
    * [1.1.0 – (2025-12-16)](#110--2025-12-16)
    * [1.0.0 – (2025-12-14)](#100--2025-12-14)
<!-- TOC -->

# Job Application Tracker & AF-Auto
A powerful Flask-based dashboard to manage job applications, visualize your search statistics, and automate the monthly activity reporting to Arbetsförmedlingen using Selenium.

## Version 
**1.2.0**

## Features
- Job Dashboard: Track job titles, companies, cities, and application dates.
- Live Statistics: View total applications, monthly trends, and status distribution (with percentages).
- Side-by-Side Analytics: Compare your progress at a glance with a responsive flexbox layout.
- Multi-Format Export:
  - JSON: Export monthly data for backup or external processing.
  - PDF: Generate official-looking activity reports for a custom date range.
- AF-Automation: Automatically uploads your applications to the Arbetsförmedlingen portal via Selenium (requires manual BankID login).
- Database Management: Built-in search functionality and a 1-click database backup feature.

---

## Requirements & Installation
1. Required Files
Ensure your project folder structure looks like this:

```bash
├── Activity_Report.pdf
├── README.md
├── Report_Okt 2025.json
├── af_uploader.py
├── app.py
├── folder_structure.txt
├── fonts
│   ├── DejaVuSansCondensed-Bold.ttf
│   └── DejaVuSansCondensed.ttf
├── images
│   ├── add_new_application.png
│   ├── job_statistics.png
│   ├── search_function.png
│   └── tracked_applications.png
├── job_tracker.db
├── jobs_import.json
├── json_importer.py
├── mock_up_data_script.py
├── requirements.txt
├── static
│   └── style.css
└── templates
    └── index.html

```    
2. Install Dependencies
Open your terminal/command prompt and run:
```bash
pip install flask selenium easygui fpdf
```
Note: You also need the Microsoft Edge WebDriver (or Chrome/Firefox equivalent) installed and added to your system PATH for the automation to work.

### Plugins
| Plugin   | README                                       |
|----------|----------------------------------------------|
| EasyGUI  | https://easygui.sourceforge.net/             |
| Flask    | https://flask.palletsprojects.com/en/stable/ |
| fpdf2    | https://pypi.org/project/fpdf2/              |
| NumPy    | https://numpy.org/                           |
| Selenium | https://www.selenium.dev/                    |


## How to Get Started
### Starting the App
1. Navigate to your project folder.
2. Run the application:
Bash `python app.py`

3. Open your browser and go to `http://127.0.0.1:5000`.

### Adding Data
- Fill in the "Add New Application" form.
- The "Time Waiting" field updates automatically relative to today's date.
- Use the Search bar to find specific companies or roles.

### Using AF-Auto (🔗 AF Button)
1. Select a Start Date and End Date in the Export box.
2. Click the 🔗 AF button.
3. An Edge browser window will open. Log in with BankID manually.
4. Navigate to the "Add Activity" (Lägg till aktivitet) page.
5. Click OK on the popup box to let the script begin auto-filling your data.

---

## Updating & Maintenance
### Updating Status
- On any job entry, use the dropdown menu to change the status (e.g., from "Waiting" to "Rejected").
- Click Update. The "Last Update" date will automatically refresh to today.

### Backup
- Regularly click the 💾 Backup Database button in the top right. This downloads a copy of your `job_tracker.db` file to your computer.

### Deleting Entries
- Each job entry has a 🗑️ icon. Clicking this will permanently remove the entry from your database after a confirmation prompt.

---

### Known Limitations
- BankID: Due to security protocols, the BankID login cannot be automated. You must be present to scan your QR code.
- Browser: The current `af_uploader.py` is configured for Microsoft Edge. To use Chrome, change `webdriver.Edge()` to `webdriver.Chrome()` in `af_uploader.py`.

## Licence Summary
This sample code is made available under the MIT-0 license. See the LICENSE file.

## Author
**Sandra van Buggenum**

- GitHub: [SnowY4you](https://github.com/SnowY4you)
- LinkedIn: [Sandra van Buggenum](https://www.linkedin.com/in/sandravanbuggenum)

## Changelog
### 1.2.0 – 2025-12-19
- Added PDF report generation
- Improved UI layout
- Fixed date formatting bug

### 1.1.0 – 2025-12-16
- Added monthly statistics view

### 1.0.0 – 2025-12-14
- Initial release