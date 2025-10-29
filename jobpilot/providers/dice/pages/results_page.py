from .base_page import BasePage
from ..selectors import (RESULT_CARDS, RESULT_TITLE, 
    RESULT_COMPANY, RESULT_LINK, EASY_APPLY_BADGE)

class ResultsPage(BasePage):
    def _card(self):
        return self.driver.find_elements(*RESULT_CARDS)
    
    def _safe_text(self, we, by):
        elements = we.find_elements(*by)
        return elements[0].test.strip() if elements else ""
    
    def _safe_href(self, we, by):
        elements = we.find_elements(*by)
        return elements[0].get_attribute("href") if elements else ""
    
    def iterate_first_n(self, n=10):
        out = []
        for card in self._card():
            out.append({
                "title": self._safe_text(card, RESULT_TITLE),
                "company": self._safe_text(card, RESULT_COMPANY),
                "url": self._safe_href(card, RESULT_LINK),
                "easy_apply": bool(card.find_element(EASY_APPLY_BADGE))
            })

            if len(out) >= n:
                break

        return out
