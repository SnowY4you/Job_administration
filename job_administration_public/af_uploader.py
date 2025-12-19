import json
import time
import sys
import easygui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Element Locators (Specific to AF 2025 Interface) ---
LOCATORS = {
    "sökta_jobb_btn": (By.XPATH, "//button[contains(., 'Sökta jobb')]"),
    "job_role_input": (By.CSS_SELECTOR, "#soktjobb-soktTjanst"),
    "company_input": (By.CSS_SELECTOR, "#soktjobb-arbetsgivare"),
    "city_input": (By.CSS_SELECTOR, "#soktjobb-ort"),
    "date_input": (By.CSS_SELECTOR, "#soktjobb-aktivitetsdatum"),
    "save_button": (By.XPATH, "//button[.//span[text()='Spara']]")
}


def add_job_application(driver, job_data):
    """Automates the entry of a single job into the AF portal."""
    try:
        # 1. Click 'Sökta jobb' to open the entry form
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(LOCATORS["sökta_jobb_btn"])).click()

        # 2. Fill Job Role and handle the AF suggestion dropdown
        role_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(LOCATORS["job_role_input"]))
        role_input.send_keys(job_data.get("job_tittle", ""))  # Using your DB field spelling
        time.sleep(2)  # Wait for AF suggestion list to populate
        role_input.send_keys(Keys.ARROW_DOWN)
        role_input.send_keys(Keys.ENTER)

        # 3. Fill Company and City
        driver.find_element(*LOCATORS["company_input"]).send_keys(job_data.get("company", ""))
        driver.find_element(*LOCATORS["city_input"]).send_keys(job_data.get("city", ""))

        # 4. Fill Date (Force clear to avoid format conflicts)
        date_field = driver.find_element(*LOCATORS["date_input"])
        date_field.send_keys(Keys.CONTROL + "a")
        date_field.send_keys(Keys.DELETE)
        date_field.send_keys(job_data.get("date_of_apply", ""))

        # 5. Save the entry
        save_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(LOCATORS["save_button"]))
        save_btn.click()

        print(f"✅ Auto-added: {job_data.get('company')}")
        time.sleep(2)  # Buffer for AF's background processing

    except Exception as e:
        print(f"❌ Error adding {job_data.get('company')}: {e}")


if __name__ == "__main__":
    # 1. Load data from Flask sys.argv
    if len(sys.argv) < 2:
        print("No job data provided.")
        sys.exit(1)

    try:
        job_applications = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Invalid JSON data.")
        sys.exit(1)

    # 2. Initialize Browser (Edge as per your personal setup)
    driver = webdriver.Edge()
    target_url = "https://arbetsformedlingen.se/for-arbetssokande/mina-sidor/aktivitetsrapportera/lagg-till-aktivitet"

    try:
        driver.get(target_url)

        # 3. User Login Sync
        easygui.msgbox(
            "BANKID LOGIN REQUIRED\n\n"
            "1. Logga in med BankID i den nya webbläsaren.\n"
            "2. Navigera till sidan för Aktivitetsrapportering.\n"
            "3. Klicka på OK här när du är framme för att påbörja autouppladdningen.",
            title="Automation - Login Sync"
        )

        # 4. Iterate and Upload
        for job in job_applications:
            add_job_application(driver, job)

        easygui.msgbox(
            f"Klart! {len(job_applications)} jobb har laddats upp till AF.",
            title="Succé"
        )

    finally:
        driver.quit()