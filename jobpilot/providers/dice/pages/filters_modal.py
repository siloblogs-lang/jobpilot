from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
from .base_page import BasePage
from ..selectors import (FILTERS_PANEL, APPLY_FILTERS_BUTTON, EASY_APPLY_CHECKBOX,
                         CLEAR_FILTERS_BUTTON, CLOSE_FILTERS_BUTTON,
                         JOBS_POSTED_TODAY, JOBS_POSTED_THREE_DAYS, JOBS_POSTED_SEVEN_DAYS,
                         WORK_SETTING_REMOTE, WORK_SETTING_ONSITE, WORK_SETTING_HYBRID,
                         FULL_TIME, CONTRACT, THIRD_PARTY, RESULTS_CONTAINER, RESULT_CARDS,
                         THIRTY_MILES_DISTANCE, TEN_MILES_DISTANCE, JOB_SEARCH_RESULTS
                         )

class FiltersModal(BasePage):
    def wait_open(self):
        try:
            self.visible(FILTERS_PANEL)
        except Exception:
            pass
        return self
    
    def _click_label_of(self, input_locator):
        input_field = self.driver.find_element(*input_locator)
        label_of_input_field = input_field.find_element(By.XPATH, "./ancestor::label[1]")
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", label_of_input_field)
        except Exception:
            ActionChains(self.driver).move_to_element(label_of_input_field).perform()

        try:
            label_of_input_field.click()
        except ElementNotInteractableException:
            self.driver.execute_script("arguments[0].click()")

    def _set_checkbox(self, locator, desired: bool | None):
        """Toggle chechbox to desired state (True/False); ingore None (no-op)
        """
        if desired is None:
            return
        
        box = self.driver.find_element(*locator)
        checked = box.is_selected() or (box.get_attribute("checked") in ("true", "checked"))
        # (box.get_attribute("checked") == "true") or (box.is_selected())
        if desired != checked:
            #click its label (parent label) if input visually hidden
            label = box.find_element(By.XPATH, "./ancestor::label[1]") if box.get_attribute("type") == "checkbox" else box
            label.click()

    def _click_radio(self, locator):
        radio = self.driver.find_element(*locator)
        # click closest label input is visually hidden
        label = radio.find_element(By.XPATH, "./ancestor::label[1]") if radio.get_attribute("type") == "radio" else radio
        
        # Bring the radio button into the view 1st
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", label)
        except Exception:
            ActionChains(self.driver).move_to_element(label).perform()

        try:
            label.click()
        except ElementNotInteractableException:
            self.driver.execute_script("arguments[0].click();", label)

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
    
    # ----------- Distance ---------
    def set_distance(self, key: str):
        distance_mapping = {
            "10_miles": TEN_MILES_DISTANCE,
            "30_miles": THIRTY_MILES_DISTANCE
        }

        if key not in distance_mapping:
            raise ValueError(f"Unknown posted_date key: {key}")
        self._click_radio(distance_mapping[key])
        return self

    # ---- Apply / Clear / Close -----
    def apply_filters(self):
        """ 
        Click 'Apply filters' and wait for model to close and results to refresh    
        """

        apply_filters_button = self.wait.until(EC.presence_of_element_located(APPLY_FILTERS_BUTTON))

        # scroll into view to avoid "not interactable"
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", apply_filters_button)
        except Exception:
            pass

        # Try normal click 1st if selenium complains ues JS click
        try:
            if apply_filters_button.is_enabled():
                apply_filters_button.click()
            else: 
                self.driver.execute_script("arguments[0].click()", apply_filters_button)
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.driver.execute_script("arguments[0].click()", apply_filters_button)
        # wait until modal disappears
        try:
            self.wait.until(EC.invisibility_of_element_located(FILTERS_PANEL))
        except Exception:
            pass
        # then wait for results to re-render
        self.visible(RESULTS_CONTAINER)
        self.wait.until(EC.presence_of_all_elements_located(RESULT_CARDS))
        return self
    
    def clear_filters(self):
        self.click(CLEAR_FILTERS_BUTTON)
        return self
    
    def close(self):
        try:
            self.click(CLOSE_FILTERS_BUTTON)
            self.wait.until(EC.invisibility_of_element_located(FILTERS_PANEL))
        except Exception:
            pass
        return self