from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from ..selectors import (FILTERS_PANEL, APPLY_FILTERS_BUTTON, EASY_APPLY_CHECKBOX,
                         CLEAR_FILTERS_BUTTON, CLOSE_FILTERS_BUTTON,
                         JOBS_POSTED_TODAY, JOBS_POSTED_THREE_DAYS, JOBS_POSTED_SEVEN_DAYS,
                         WORK_SETTING_REMOTE, WORK_SETTING_ONSITE, WORK_SETTING_HYBRID,
                         FULL_TIME, CONTRACT, THIRD_PARTY, RESULTS_CONTAINER, RESULT_CARDS
                         )

class FiltersModal(BasePage):
    def wait_open(self):
        self.visible(FILTERS_PANEL)
        return self
    
    def _set_checkbox(self, locator, desired: bool | None):
        """Toggle chechbox to desired state (True/False);
            ingore None (no-op)
        """
        if desired is None:
            return
        
        box = self.driver.find_element(*locator)
        checked = (box.get_attribute("checked") == "true") or (box.is_selected())
        if desired != checked:
            #click its label (parent label) if input visually hidden
            label = box.find_element(By.XPATH, "./ancestor::label[1]") if box.get_attribute("type") == "checkbox" else box
            label.click()

    def _click_radio(self, locator):
        radio = self.driver.find_element(*locator)
        # click closest label input is visually hidden
        label = radio.find_element(By.XPATH, "./ancestor::label[1]") if radio.get_attribute("type") == "radio" else radio
        label.click()

    # ---- Job post featires -------
    def set_easy_apply(self, desired: bool | None = None):
        self._set_checkbox(EASY_APPLY_CHECKBOX, desired)
        return self
    
    # ------ Selection of one of the posted dates ------
    def set_posted_date(self, key: str):
        mapping = {
            "today": JOBS_POSTED_TODAY,
            "last_3_days": JOBS_POSTED_THREE_DAYS,
            "last_7_days": JOBS_POSTED_SEVEN_DAYS
        }

        if key not in mapping:
            raise ValueError(f"Unknown posted_date key: {key}")
        self._click_radio(mapping[key])
        return self
    
    # ------ Work settings --------
    def set_work_settings(self, *, remote: bool | None = None, hybrid: bool | None = None, onsite: bool | None = None):
        self._set_checkbox(WORK_SETTING_REMOTE, remote)
        self._set_checkbox(WORK_SETTING_HYBRID, hybrid)
        self._set_checkbox(WORK_SETTING_ONSITE, onsite)
        return self
    
    # ------ Employment type ---------
    def set_employment_type(self, *, full_time: bool | None = None, contract: bool | None = None, third_party: bool | None = None):
        self._set_checkbox(FULL_TIME,  full_time)
        self._set_checkbox(CONTRACT, contract)
        self._set_checkbox(THIRD_PARTY, third_party)
        return self
    
    # ---- Apply / Clear / Close -----
    def apply_filters(self):
        """ 
        Click 'Apply filters' and wait for model to close and results to refresh    
        """

        self.click(APPLY_FILTERS_BUTTON)
        # wait until modal disappears
        self.wait.until(EC.invisibility_of_element_located(FILTERS_PANEL))
        # then wait for results to re-render
        self.visible(RESULTS_CONTAINER)
        self.wait.until(EC.presence_of_all_elements_located(RESULT_CARDS))
        return self
    
    def clear_filters(self):
        self.click(CLEAR_FILTERS_BUTTON)
        return self
    
    def close(self):
        self.click(CLOSE_FILTERS_BUTTON)
        self.wait.until(EC.invisibility_of_element_located(FILTERS_PANEL))
        return self