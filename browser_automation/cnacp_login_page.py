'''
Page object for the CNCAP login screen: navigates to the login form,
fills in username/password, and submits/confirms the login.
'''

from playwright.sync_api import Page

class LoginPage:
    #Initialize the page object and define locators for the elements on the page
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("button[action='login']")
        self.success_button = page.locator("button[action='success']")
    
    #Define methods for interacting with the page, such as entering the username and password, and clicking the login button
    def enter_username(self, username: str):
        self.username_input.fill(username)
    
    def enter_password(self, password: str):
        self.password_input.fill(password)
    
    #Define a method for logging in
    def login(self, username: str, password: str):
        self.page.locator("#menu-item-1090 a").click()
        self.page.wait_for_selector("button[action='login']")

        self.enter_username(username)
        self.enter_password(password)

        self.login_button.click()
        self.success_button.click()