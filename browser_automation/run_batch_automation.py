'''
Automates CNCAP simulation submissions: for each batch folder under
APP_FILE_PATH, logs into the site, creates a task per Excel file and
uploads it, then downloads the results as .zip files. Waits 15 min
between batches; skips to the next batch if one fails.
'''

from playwright.sync_api import Playwright
from cnacp_login_page import LoginPage
from cnacp_home_page import HomePage
from cnacp_simulation_page import OnlineSimulationPage
from pathlib import Path
from dotenv import load_dotenv
import os
import sys
import time

def run(playwright: Playwright) -> None:
    print("SCRIPT STARTED")

    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent.parent
    else:
        base_path = Path(__file__).parent.parent

    #Load environment variables from .env file
    load_dotenv(dotenv_path = base_path / ".env")

    #Use pathlib to get all the excel files in the specified folder, loop through them and upload each file using the file chooser
    base_folder = Path(os.getenv("APP_FILE_PATH"))
    batch_folders = [f for f in base_folder.iterdir() if f.is_dir()]

    for i, batch_folder in enumerate(batch_folders):
        try: 
            #Set up the browser and page
            try:
                #Use chrome if available, otherwise use edge
                browser = playwright.chromium.launch(headless = False, channel = "chrome")
            except:
                browser = playwright.chromium.launch(headless = False, channel = "msedge")

            context = browser.new_context()
            page = context.new_page()

            #Navigate to the website, wait for the page to load before proceeding
            page.goto(os.getenv("APP_BASE_URL"), timeout = 0)

            #Login page, try block if already logged in, skip login step
            try:
                login_page = LoginPage(page)
                login_page.login(os.getenv("APP_USERNAME"), os.getenv("APP_PASSWORD"))
            except Exception as e:
                print(f"Login error: {e}")

            #Home page, click through the menu to get to the online simulation page
            try:
                home_page = HomePage(page)
                home_page.navigate_to_online_simulation()
            except Exception as e:
                print(f"Navigation error: {e}")

            print(f"Processing batch: {batch_folder.name}")

            excel_files = list(batch_folder.glob("*.xlsx"))

            simulation_page = OnlineSimulationPage(page)

            #Loop through the excel files and upload each one using the file chooser
            for file_path in excel_files:
                #Create a new task, fill in the task name, select the year, click through the steps to get to the batch upload page
                parts = file_path.stem.split("-")
                task_name = parts[0]
                year_1 = parts[1]
                year_2 = parts[2]

                #Create a new task and upload the file for each excel file in the folder
                simulation_page.create_task(task_name, year_1, year_2)
                simulation_page.upload_file(str(file_path))

            #After uploading all the files, loop through the tasks and download the results for each one, save the results to a specified folder
            for file_path in excel_files:
                parts = file_path.stem.split("-")
                task_name = parts[0]

                #Use pathlib to construct the download path for each task, and move the downloaded file to the specified folder
                download_path = Path(os.getenv("APP_DOWNLOAD_PATH")) / f"{task_name}_results.zip"
                simulation_page.download_results(task_name, str(download_path))

            print(f"Batch {batch_folder.name} complete. Sleeping...")

            context.close()
            browser.close()

            if i + 1 < len(batch_folders):
                time.sleep(900)
        except Exception as e:
            if context:
                context.close()
            if browser:
                browser.close()
            
            print(f"Batch {batch_folder.name} failed: {e}")
            continue

    print("SCRIPT FINISHED")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        run(playwright)