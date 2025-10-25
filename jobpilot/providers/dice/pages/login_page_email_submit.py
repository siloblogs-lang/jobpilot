from .base_page import BasePage
from ..selectors import LOGIN_EMAIL, EMAIL_SUBMIT_BUTTON

class LoginPageEmailSubmit(BasePage):
    URL = "https://www.dice.com/dashboard/login"

    def open(self):
        return super().open(self.URL)
    
    # def login(self, email: str, password: str):
    #     self.type(LOGIN_EMAIL, email)
    #     self.type(LOGIN_PASSWORD, email)
    #     # self.click(LOGIN_SUBMIT)

    def login_email_submit(self, email:str):
        self.type(LOGIN_EMAIL, email)
        self.click(EMAIL_SUBMIT_BUTTON)

        # Dice navigates to /login/password
        self.url_contains("/login/password")
        return self