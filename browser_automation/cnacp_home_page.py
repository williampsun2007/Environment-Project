'''
Page object for the CNCAP home/menu screen: hovers the main menu and
clicks through to the Online Simulation page.
'''

from playwright.sync_api import Page

class HomePage:
    #Initialize the page object and define locators for the elements on the page
    def __init__(self, page: Page):
        self.page = page
        self.menu = page.locator("#menu-item-1171 > a")
        self.submenu = page.locator("#menu-item-1174 > a")
        self.online_simulation = page.locator("p[data-i18n-text_call='menu_assessment_tasks']")

    #Define methods for interacting with the page, such as navigating to the online simulation page
    def navigate_to_online_simulation(self):
        self.menu.hover()
        self.submenu.click()
        self.online_simulation.click()