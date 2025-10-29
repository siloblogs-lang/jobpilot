from .base_page import BasePage
from selenium.webdriver.support import expected_conditions as EC
from ..selectors import (RESULT_CARDS, RESULT_TITLE, 
    RESULT_COMPANY, RESULT_LINK, EASY_APPLY_BADGE,
    JOB_SEARCH_RESULTS)

class ResultsPage(BasePage):
    def _card(self):
        self.wait.until(EC.presence_of_all_elements_located(JOB_SEARCH_RESULTS))
        return self.driver.find_elements(*JOB_SEARCH_RESULTS)
    
    def _safe_text(self, we, by):
        elements = we.find_elements(*by)
        return elements[0].text.strip() if elements else ""
    
    def _safe_href(self, we, by):
        elements = we.find_elements(*by)
        return elements[0].get_attribute("href") if elements else ""
    
    def iterate_first_n(self, n=10):
        out = []
        for card in self._card():
            print(card)
            out.append({
                "title": card
                # "title": self._safe_text(card, RESULT_TITLE),
                # "company": self._safe_text(card, RESULT_COMPANY),
                # "url": self._safe_href(card, RESULT_LINK),
                # "easy_apply": bool(card.find_element(EASY_APPLY_BADGE))
            })
            print(out)    
            if len(out) >= n:
                break

        return out
