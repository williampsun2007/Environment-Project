'''
Page object for the CNCAP "Online Simulation" screen: creates a new
task with a name/year range, uploads an Excel input via the file
chooser, and downloads the results once a task finishes processing.
'''

from playwright.sync_api import Page
import time

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

        time.sleep(2)
        self.submit_ok.click()
        time.sleep(2)
        self.confirm_back.click()
        time.sleep(2)
        self.edit_control_data.click()
        time.sleep(2)
        self.confirm_back_2.click()
        time.sleep(3)  # extra wait after fully done

    def download_results(self, task_name: str, download_path: str):
        print(f"Downloading task: {task_name}")
        row = self.page.locator("tr").filter(has=self.page.locator(f"span:text-is('{task_name}')"))

     # Wait for either completed or failed state
        while True:
            if row.locator("button.download").is_visible():
                break  # completed, proceed to download
            if row.locator("span.case-state-name:text-is('失败')").is_visible():
                raise Exception(f"Task {task_name} failed on server")
            time.sleep(5)  # neither yet, keep waiting

        download_button = row.locator("button.download")
        download_button.wait_for(state = "visible", timeout = 0)
        time.sleep(2)

        with self.page.expect_download(timeout=0) as download_info:
            download_button.click()

        download = download_info.value
        download.save_as(download_path)
        print(f"Finished downloading: {task_name}")
