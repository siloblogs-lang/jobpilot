from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_TIMEOUT = 20

class BasePage:
    URL = None # set by child pages

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    def open(self, url: str | None = None):
        target = url or self.URL
        if not target:
            raise ValueError("No URL provided and no URL attribte set on page")
        self.driver.get(target)
        return self  # chainable

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type(self, locator, text):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))
    
    def url_contains(self, fragment: str):
        self.wait.until(EC.url_contains(fragment))
        return self