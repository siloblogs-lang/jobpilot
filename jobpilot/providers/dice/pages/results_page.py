from typing import List, Set
import hashlib

from .base_page import BasePage
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from ..selectors import (
    RESULT_CARDS, 
    RESULT_TITLE, 
    RESULT_COMPANY, 
    RESULT_LINK, 
    EASY_APPLY_BADGE,
)

from jobpilot.models.job import JobPosting

class ResultsPage(BasePage):
    def _card(self):
        self.wait.until(EC.presence_of_all_elements_located(RESULT_CARDS))
        return self.driver.find_elements(*RESULT_CARDS)
    
    def _safe_text(self, we, by):
        elements = we.find_elements(*by)
        return elements[0].text.strip() if elements else ""
    
    def _safe_href(self, we, by):
        elements = we.find_elements(*by)
        return elements[0].get_attribute("href") if elements else ""
    
    def _has_easy_apply(self, card) -> bool:
        # Return true if the card has EasyApply badge
        try:
            card.find_element(*EASY_APPLY_BADGE)
            return True
        except NoSuchElementException:
            return False
        
    def _company_url(self, card) -> str:
        """ 
        Best-effort extraction of the company profile URL.
        We use CSS 'a + a' (adjacent sibling)
        """
        try:
            link = card.find_element(By.CSS_SELECTOR, '.logo a + a ')
        except Exception:
            return ""
        
    def _make_job_id(self, url: str) -> str:
        """
        Create a stable job ID from the URL
        
        Using a hash here decouples your internal ID from the site's
        implementation details, but stays stable for a given URL.
        """    

        if not url:
            return ""
        return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    
    #### --- Public API ------

    def iterate_all(self, max_results: int = 100) -> List[JobPosting]:
        """"
        Walk all loaded result cards (with simple pagination/scroll),
        convert them into JobPosting objects and stop when:
        - we've reached max_results or
        - no new cards appear after scrolling

        De-deduplicated by URL job ID
        """

        jobs: List[JobPosting] = []
        seen_ids: Set[str] = set()

        last_card_count = 0

        while len(jobs) < max_results:
            cards = self._card()
            if not cards:
                break
            
            for idx, card in enumerate(cards):
                url = self._safe_href(card, RESULT_LINK)
                if not url:
                    continue

                job_id = self._make_job_id(url)
                if job_id in seen_ids:
                    continue

                title = self._safe_text(card, RESULT_TITLE)
                company = self._safe_text(card, RESULT_COMPANY)
                easy_apply = self._has_easy_apply(card)

                # Location is not wired yet – we’d need a stable selector.
                # To avoid InvalidSelector bugs, we keep it empty for now.
                location = ''

                metadata = {
                    "source_card_index": str(idx),
                    "raw_company_url": self._company_url(card)
                }

                jobs.append(
                    JobPosting(
                        id=job_id,
                        title=title,
                        company=company,
                        location=location,
                        url=url,
                        provider='dice',
                        easy_apply=easy_apply,
                        metadata=metadata
                    )
                )

                seen_ids.add(job_id)

                if len(jobs) >= max_results:
                    break

            if len(jobs) >= max_results:
                break

            # --- Simple pagination / infinate scroll handling --- 
            current_card_count = len(cards)
            if current_card_count == last_card_count:
                break

            last_card_count = current_card_count

            # Scroll to the last caard to trigger lazy-loading / infinate scroll
            last_card = cards[-1]
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: end});", last_card
                )   
            except Exception:
                # If JS scrolling fails, just bail out of pagination.
                break
            
            # Give ppage a chance to load additional cards
            # We will stop if this times out 
            try: 
                self.wait.until(
                    lambda d: len(d.find_elements(*RESULT_CARDS)) > current_card_count
                )
            except Exception:
                break

        return jobs

    def iterate_first_n(self, n=10):
        out = []
        for card in self._card():
            print(card)
            out.append({
                "title": self._safe_text(card, RESULT_TITLE),
                "company": self._safe_text(card, RESULT_COMPANY),
                "url": self._safe_href(card, RESULT_LINK),
                #"easy_apply": bool(card.find_element(EASY_APPLY_BADGE))
            })
            print(out)    
            if len(out) >= n:
                break

        return out
