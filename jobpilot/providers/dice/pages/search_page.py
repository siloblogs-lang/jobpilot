from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from ..selectors import (
    SEARCH_KEYWORD_INPUT, SEARCH_LOCATION_INPUT, SEARCH_SUBMIT,
    RESULTS_CONTAINER, JOB_SEARCH_RESULTS, FILTERS_PANEL, 
    OPEN_FILTERS_PANEL, RESULT_CARDS
)
from .filters_modal import FiltersModal

class SearchPage(BasePage):
    URL = "https://www.dice.com/jobs"

    def open(self):
        return super().open(self.URL)
    
    def _confirm_typehead(self, locator, text: str):
        # wait for clickable input
        el = self.wait.until(EC.element_to_be_clickable(locator))

        # pick truly interactable input
        candidates = self.driver.find_elements(*locator)
        for candidate in candidates:
            if candidate.is_displayed() and candidate.is_enabled():
                element = candidate
                break

        # Focus on selected candidate
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        element.click()

        # DO NOT use el.clear() on comboboxes; instead send CTRL/CMD+A then DELETE
        # clear selected fields
        try:
            element.send_keys(Keys.COMMAND, "a")
            element.send_keys(Keys.DELETE)
        except Exception:
            element.send_keys(Keys.COMMAND, "a")
            element.send_keys(Keys.DELETE)
        
        # type the text and confirm the typehead with ENTER
        element.send_keys(text)
        element.send_keys(Keys.ENTER)

    def search(self, keyword: str, location: str | None = None):
        self._confirm_typehead(SEARCH_KEYWORD_INPUT, keyword)
        if location:
            self._confirm_typehead(SEARCH_LOCATION_INPUT, location)

        try: 
            self.click(SEARCH_SUBMIT)
        except Exception:
            pass

        # wait for results and filters to exist (no sleeps)
        self.visible(RESULTS_CONTAINER)
        self.wait.until(EC.presence_of_all_elements_located(RESULT_CARDS))
        # self.wait.until(EC.presence_of_element_located(FILTERS_PANEL))
        return self
    
    def open_filters(self):
        try:
            self.click(OPEN_FILTERS_PANEL)
        except Exception:
            pass

        try:
            self.visible(FILTERS_PANEL)
        except Exception:
            pass

        return FiltersModal(self.driver)