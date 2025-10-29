from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from ..selectors import (
    SEARCH_KEYWORD_INPUT, SEARCH_LOCATION_INPUT, SEARCH_SUBMIT,
    RESULTS_CONTAINER, RESULT_CARDS, FILTERS_PANEL, OPEN_FILTERS_PANEL
)
from .fitlers_modal import FiltersModal

class SearchPage(BasePage):
    URL = "https://www.dice.com/jobs"

    def open(self):
        return super().open(self.URL)
    
    def search(self, keyword: str, location: str | None = None):
        self.type(SEARCH_KEYWORD_INPUT, keyword)
        if location:
            self.type(SEARCH_KEYWORD_INPUT, location)

        self.click(SEARCH_SUBMIT)

        # wait for results and filters to exist (nop sleeps)
        self.visible(RESULTS_CONTAINER)
        self.wait.until(EC.presence_of_all_elements_located(RESULT_CARDS))
        # self.wait.until(EC.presence_of_element_located(FILTERS_PANEL))
        return self
    
    def open_filters(self) -> FiltersModal:
        self.click(OPEN_FILTERS_PANEL)