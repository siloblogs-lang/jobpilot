from __future__ import annotations

from pathlib import Path
from typing import Optional

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage
from ..selectors import (
    EASY_APPLY_STEP1_CONTAINER,
    EASY_APPLY_RESUME_REPLACE_BUTTON,
    EASY_APPLY_RESUME_FILE_INPUT,
    EASY_APPLY_STEP1_NEXT_BUTTON,
    EASY_APPLY_STEP2_CONTAINER,
    EASY_APPLY_REVIEW_RESUME_HEADER,
    EASY_APPLY_SUBMIT_BUTTON,
    EASY_APPLY_CONFIRMATION_CONTAINER,
    EASY_APPLY_SUBMITTED_HEADER
)

class EasyApplyFormPage(BasePage):
    """
    Page Object for Dice's 2-step Easy Apply flow:

    Step 1: Resume & Cover Letter  (/apply)
    Step 2: Review & Submit        (/apply/submit)

    This class is intentionally minimal for now:
    - wait for Step 1 to load
    - optionally replace/upload resume
    - click Next
    - wait for review step
    - click Submit
    """

    # ---------- STEP 1: RESUME & COVER LETTER ------------
    def wait_step1_loaded(self, timeout: int = 15) -> "EasyApplyFormPage":
        """
        Wait till Step 1 container is visible
        """
        try:
            self.wait.until(EC.visibility_of_element_located(EASY_APPLY_STEP1_CONTAINER))
        except TimeoutException:
            # Looser fallback: visibility only
            self.wait.until(EC.presence_of_element_located(EASY_APPLY_STEP1_CONTAINER))

        return self
    
    def _click_replace_resume(self) -> None:
        """
        Click the 'Replace' button if present.
        This typically opens the OS file picker / triggers the underlying <input type="file">.
        """
        try:
            btn = self.visible(EASY_APPLY_RESUME_REPLACE_BUTTON)
            btn.click()
        except Exception:
            return
        
    def _set_resume_file(self, resume_path: str | Path) -> None:
        """
        Send the resume path to an <input type='file'> element, if we can find one.

        This is defensive: if Dice changes the DOM and we don't see the input,
        we simply don't crash – we fall back to the existing resume.
        """
        path_str = str(Path(resume_path).expanduser().resolve())
        try:
            file_input = self.driver.find_element(*EASY_APPLY_RESUME_FILE_INPUT)
            file_input.send_keys(path_str)
        except NoSuchElementException:
            return
        except Exception:
            return
        
    def set_resume(self, resume_path: Optional[str | Path]) -> "EasyApplyFormPage":
        """
        Public method used by the provider:

        - Optionally click 'Replace'
        - Try to send the file path to the resume input

        If resume_path is None, we keep the existing resume.
        """
        if not resume_path:
            return self
        
        self._click_replace_resume()
        self._set_resume_file(resume_path)
        return self
    
    def click_next_step(self) -> "EasyApplyFormPage":
        """
        Click 'Next' to move to step 2
        """
        btn = self.visible(EASY_APPLY_STEP1_NEXT_BUTTON)
        btn.click()
        return self
    
    # ------------ STEP 2: Review & Submit -------------
    def wait_step2_loaded(self, timeout: int = 15) -> "EasyApplyFormPage":
        try:
            # Wait on either the main container or a stable header.
            self.wait.until(EC.visibility_of_element_located(EASY_APPLY_STEP2_CONTAINER))
            self.wait.until(EC.visibility_of_element_located(EASY_APPLY_REVIEW_RESUME_HEADER))

        except TimeoutException:
            self.wait.until(EC.presence_of_element_located(EASY_APPLY_STEP2_CONTAINER))
        return self    
    
    def click_submit(self) -> "EasyApplyFormPage":
        btn = self.visible(EASY_APPLY_SUBMIT_BUTTON)
        btn.click()
        return self
    
    # ------------- Application Confirmation Page --------------
    def wait_submission_confirmation(self, timeout: int = 15) -> bool:
        """
        Wait for the post-apply confirmation banner.
        Return True if see within timeout, False otherwise.
        """

        try:
            self.wait.until(EC.visibility_of_element_located(EASY_APPLY_CONFIRMATION_CONTAINER))
            self.wait.until(EC.visibility_of_element_located(EASY_APPLY_SUBMITTED_HEADER))
            return True
        except TimeoutException:
            return False
        
    def is_submission_successful(self) -> bool:
        """
        Cheap sanity check after wait_submission_confirmation():
        - reads the H1 text
        - checks that it contains 'Application submitted' (case-insensitive)
        """

        try:
            h1 = self.driver.find_element(*EASY_APPLY_SUBMITTED_HEADER)
            text = (h1.text or "").strip().lower()
            return "application submitted" in text
        except Exception:
            return False