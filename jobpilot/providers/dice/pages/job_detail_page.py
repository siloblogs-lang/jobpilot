from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage
from ..selectors import JOB_DESCRIPTION_CONTAINER

class JobDetailPage(BasePage):
    """
    Page Object for a single Dice job detail page.

    Responsibilities:
    - Navigate to a job URL
    - Wait for the job description to be present
    - Extract the description text in a safe, robust way
    """

    def wait_loaded(self) -> "JobDetailPage":

        # Wait for the job description area to be present/visible.
        # Return self for chaining;
        try: 
            self.visible(JOB_DESCRIPTION_CONTAINER)
        except Exception:
            # As a defensive measure, do one last wait on presence (less strict than visible).
            self.wait.until(EC.presence_of_element_located(JOB_DESCRIPTION_CONTAINER))

        return self
    
    def get_description_text(self) -> str:
        """
        Extract the full job description text.
        Returns an empty string if the description cannot be found.

        This method should never raise an exception for "normal" missing elements.
        """
        try:
            container = self.visible(JOB_DESCRIPTION_CONTAINER)
        except Exception:
            try:
                container = self.wait.until(
                    EC.presence_of_element_located(JOB_DESCRIPTION_CONTAINER)
                )
            except TimeoutException:
                # Defensive scrapint: don't blow up the whole run for one job
                return ""
        
        raw_text = container.text or ""
        # Normalize whitespace (collapse multiple spaces/newlines)
        return " ".join(raw_text.split())