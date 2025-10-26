
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from ..selectors import SHADOW_ROOT, HEADER_PROFILE_NAME, PROFILE_GREETING, USER_ONLINE_INDICATOR

class DashboardPage(BasePage):
    def wait_loaded(self):
        #any marker visible is fine
        def any_marker_visible(driver):
            for by in (SHADOW_ROOT, PROFILE_GREETING):
                if driver.find_elements(*by):
                    return True
            return False
        self.wait.until(any_marker_visible)
        return self
    
    def wait_online_status_for(self, full_name: str):
        expected_text = f"{full_name} is Online".strip()
        # Normalize-space guards against stray whitespaces
        xp = f"//span[contains(@class, 'sr-only') and normalize-space() = '{expected_text}']"
        self.wait.until(EC.presence_of_element_located((By.XPATH, xp)))
        return self
    
    def online_status_text(self) -> str:
        """ Get the text from the sr-only status span (first match)"""
        online_status_element = self.driver.find_element(*USER_ONLINE_INDICATOR)
        return (online_status_element.text.strip() if online_status_element else "")
 