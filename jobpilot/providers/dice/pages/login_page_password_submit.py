from .base_page import BasePage
from ..selectors import LOGIN_PASSWORD, PASSWORD_SUBMIT_BUTTON
from .dashboard_page import DashboardPage

class LoginPagePasswordSubmit(BasePage):

    URL = "https://www.dice.com/dashboard/login/password"

    def open(self):
        return super().open(self.URL)
    
    def login_password_submit(self, password: str):
        self.type(LOGIN_PASSWORD, password)
        self.click(PASSWORD_SUBMIT_BUTTON)
        return DashboardPage(self.driver).wait_loaded()
        # Wait for dashboard/home after login
        #self.url_contains("/dashboard")
        #return self