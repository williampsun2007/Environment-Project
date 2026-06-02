from socket import timeout
import time
from urllib import response
import requests
from playwright.sync_api import Page

class OnlineSimulationPage:
    #Initialize the page object and define locators for the elements on the page
    def __init__(self, page: Page):
        #Wait for the page to load and the add task button to be visible before initializing the locators
        self.page = page
        page.wait_for_selector("button.addTask", state="visible")

        #Define locators for the elements on the page
        self.add_task_button = page.locator("button.addTask")
        self.task_name_input = page.locator("input.taskName")
        self.first_year_select = page.locator("select.inventory-timeRange").first
        self.second_year_select = page.locator("select.meteorological-timeRange")
        self.next_step = page.locator("button[data-i18n-text='nextStep']")
        self.upload_button = page.locator("button.uploadUpdate")
        self.file_chooser_button = page.locator("div.uploader-browsebutton a")
        self.submit_ok = page.locator("button.submitOk")
        self.confirm_back = page.locator("button.confirm[btntype='contrlback']")
        self.edit_control_data = page.locator("button.btn-editControlData")
        self.confirm_back_2 = page.locator("button.confirm[btntype='back']")

    #Define methods for interacting with the page, such as creating a new task, uploading a file, and downloading results
    def create_task(self, task_name: str, year_1: str, year_2: str):
        self.add_task_button.click()
        self.task_name_input.fill(task_name)
        self.first_year_select.select_option(year_1)
        self.second_year_select.select_option(year_2)
        self.next_step.click()

    def upload_file(self, file_path: str):
        self.upload_button.click()
        with self.page.expect_file_chooser() as fc_info:
            self.file_chooser_button.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)

        self.submit_ok.click()
        self.confirm_back.click()
        self.edit_control_data.click()
        self.confirm_back_2.click()

    def download_results(self, task_name: str, download_path: str):
        row = self.page.locator("tr").filter(has=self.page.locator(f"span:text-is('{task_name}')"))
        row.locator("span.case-state-2").first.wait_for(state="visible", timeout = 0)
        
        download_button = row.locator("button.download")
        download_button.wait_for(state="visible", timeout = 0)

        with self.page.expect_download(timeout=0) as download_info:
            download_button.click()

        download = download_info.value
        download_url = download.url

        response = requests.get(download_url, stream=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
