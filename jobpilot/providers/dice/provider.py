from __future__ import annotations
from typing import Iterable, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait 

from jobpilot.providers.base import BaseProvider
from jobpilot.models.job import JobPosting, ApplyResult

from jobpilot.providers.dice.pages.login_page_email_submit import LoginPageEmailSubmit
from jobpilot.providers.dice.pages.login_page_password_submit import LoginPagePasswordSubmit
from jobpilot.providers.dice.pages.search_page import SearchPage
from jobpilot.providers.dice.pages.results_page import ResultsPage
from jobpilot.providers.dice.pages.dashboard_page import DashboardPage
from jobpilot.providers.dice.pages.job_detail_page import JobDetailPage


class DiceProvider(BaseProvider):
    """
    Wraps the page objects and exposes clean methods:
    - login()
    - search()
    - open_job()
    - apply()
    """

    NAME = "dice"

    def __init__ (self, driver: WebDriver, cfg: dict) -> None:
        self.driver = driver
        self.cfg = cfg

        self.env = cfg.get("env", {})
        self.search_cfg = cfg.get("dice", {})

    # --- BaseProvider API implementations ----
    def login(self) -> None:
        """ Login to Dice using existing POMs """
        email = self.env.get("DICE_EMAIL")
        password = self.env.get("DICE_PASSWORD")

        if not email or not password:
            # Fail loud and early - easy to debug
            raise RuntimeError("EMAIL OR PASSWORD missing from env config")
        
        LoginPageEmailSubmit(self.driver).open().login_email_submit(email)
        LoginPagePasswordSubmit(self.driver).login_password_submit(password)
        DashboardPage(self.driver).wait_loaded()

    def search(self, max_results: int=100) -> List[JobPosting]:
        """
         Perform a search and return JobPosting objects

        """
        max_results = min(
            max_results,
            int(self.search_cfg.get("max_results", max_results))
        )

        keywords = self.search_cfg.get("keywords") or []
        locations = self.search_cfg.get("locations") or []

        print(f"[All Search terms]=> {keywords}")
        print(f"[All locations]=> {locations}")

        if not keywords or not locations:
            raise RuntimeError("No keyword or locations configured for search")
        
        all_jobs: List[JobPosting] = []
        seen_ids = set()

        for keyword in keywords:
            for location in locations:

                remaining = max_results - len(all_jobs)
                if remaining <= 0:
                    return all_jobs
                print(f"[DiceProvider.search] => Processing {keyword} + {location}")
                search_page = SearchPage(self.driver).open()
                search_page.search(keyword=keyword, location=location)

                results_page = ResultsPage(self.driver)
                jobs = results_page.iterate_all(max_results=remaining)
                print(f"[DiceProvider.search] => Found {len(jobs)} jobs for {keyword} + {location}")
                for job in jobs:
                    if job.id in seen_ids:
                        continue

                    md = dict(job.metadata or {})
                    md["search_keyword"] = keyword
                    md["search_location"] = location
                    job.metadata = md

                    all_jobs.append(job)
                    seen_ids.add(job.id)

                    if len(all_jobs) >= max_results:
                        return all_jobs
                print(f"[DiceProvider.search] => Total collected so far = {len(all_jobs)}")
        return all_jobs
        
        # Legacy logic relplaced the nested 'for loop' above
        # keyword = keywords[0]
        # location = locations[0]

        # search_page = SearchPage(self.driver).open()
        # search_page.search(keyword=keyword, location=location)

        # results_page = ResultsPage(self.driver)
        # jobs = results_page.iterate_all(max_results=max_results)

        # return jobs
    
    def get_job_description(self, job: JobPosting) -> str:
        """
        Open a job detail page and return the normalized description text.

        This is a thin wrapper around the Dice JobDetailPage, so that
        the orchestrator doesn't need to know about Dice DOM details.
        """
        page = JobDetailPage(self.driver).open(job.url)
        page.toggle_open_description()
        return page.get_description_text()

    def is_easy_apply(self, job: JobPosting) -> bool:
        return bool(job.easy_apply)
    
    def apply(self, job: JobPosting) -> ApplyResult:
        apply_window = None
        original_window = self.driver.current_window_handle

        try:
            # 1) Force open job in a new tab and switch
            before = set(self.driver.window_handles)
            original_window = self._open_in_new_tab_and_switch(job.url, timeout=10)
            after = set(self.driver.window_handles)
            new_handles = list(after - before)
            apply_window = new_handles[0] if new_handles else None

            # 2) Now we are in the job detail tab
            detail_page = JobDetailPage(self.driver)
            detail_page.wait_loaded()

            # 3) Click Apply/Easy Apply -> Step 1
            form_page = detail_page.click_easy_apply()

            # 4) Step 1 -> Next
            form_page.wait_step1_loaded()
            form_page.click_next_step()

            # 5) Step 2 -> Submit
            form_page.wait_step2_loaded()
            form_page.click_submit()

            # 6) Confirmation
            ok = form_page.wait_submission_confirmation()
            success = ok and form_page.is_submission_successful()

            if success:
                return ApplyResult(status="APPLIED", app_id=None, notes="Applied via Easy Apply.")
            return ApplyResult(status="ERROR", app_id=None, notes="Submit clicked but confirmation was not detected.")

        except Exception as e:
            return ApplyResult(status="ERROR", app_id=None, notes=f"Exception during Easy apply: {e}")

        finally:
            try:
                # Close the apply tab if we opened one
                if apply_window and apply_window in self.driver.window_handles:
                    self.driver.close()
                # Switch back to original
                if original_window in self.driver.window_handles:
                    self.driver.switch_to.window(original_window)
            except Exception:
                pass
    # def apply(self, job: JobPosting) -> ApplyResult:
    #     """
    #     Full Easy Apply flow for Dice.

    #     Flow:
    #     - Open job detail (may be in current tab or new tab).
    #     - Click Apply / Easy apply on the detail page.
    #     - Step 1: click Next.
    #     - Step 2: click Submit.
    #     - Wait for confirmation.
    #     - Close the apply tab if it was a new tab, then return to original window.
    #     """
    #     apply_window = None
    #     original_window = self.driver.current_window_handle
    #     # initial_handles = set(self.driver.window_handles)

    #     try:
    #         # 1. Open job detail page (This )
    #         # new improvement to alow job details_page to open new browser tab
    #         before = set(self.driver.window_handles)
    #         original_window = self._open_in_new_tab_and_switch(job.url, timeout=10)
    #         after = set(self.driver.window_handles)
    #         new_handles = list(after - before)
    #         apply_window = new_handles[0] if new_handles else None
    #         # Legacy code (opens in same browser tab)
    #         # detail_page = JobDetailPage(self.driver).open(job.url)
    #         # detail_page.wait_loaded()

    #         # If Dice opened the job in a new tab (e.g., from a previous click ),
    #         # detect it and switch into it
    #         current_handles = set(self.driver.window_handles)
    #         extra_handles = list(current_handles - initial_handles)
    #         if extra_handles:
    #             apply_window = extra_handles[0]
    #             self.driver.switch_to.window(apply_window)

    #         # 2. click 'Easy apply' => navigates to apply Step 1
    #         before_apply_click = set(self.driver.window_handles)

    #         detail_page = JobDetailPage(self.driver).wait_loaded()
    #         form_page = detail_page.click_easy_apply()

    #         # if Apply button opens another tab, nandle that new tab
    #         after_apply_click = set(self.driver.window_handles)
    #         extra_after_apply = list(after_apply_click - before_apply_click)
    #         if extra_after_apply:
    #             apply_window = extra_after_apply[0]
    #             self.driver.switch_to.window(apply_window)

    #         # 3. Step 1: wait for container then click Next
    #         form_page.wait_step1_loaded()
    #         form_page.click_next_step()
    #         # TODO: if you want to always replace resume here, wire in resume_path
    #         # from profile cfg and call form_page.replace_resume(resume_path)
    #         #
    #         # For now, we assume the correct resume is already attached on Dice profile.
            
    #         # 4. Step 2 of application -> Cick Next button
    #         form_page.wait_step2_loaded()
    #         form_page.click_submit()

    #         # 5. Wait for confirmation + sanity check header test
    #         ok = form_page.wait_submission_confirmation()
    #         success = ok and form_page.is_submission_successful()

    #         if success:
    #             return ApplyResult(
    #                 status="APPLIED",
    #                 app_id=None,
    #                 notes="Applied via Easy Apply."
    #             )
    #         else:
    #             return ApplyResult(
    #                 status="ERROR",
    #                 app_id=None,
    #                 notes="Easy Apply flow finished but confirmation banner was not detected"
    #             )
    #     except Exception as e:
    #         return ApplyResult(
    #             status="ERROR",
    #             app_id=None,
    #             notes=f"Exception during Easy apply: {e}"
    #         )
    #     finally:
    #         # 6.  Clean up: close extra tab if we used one and go back to the original window
    #         try:
    #             if apply_window and apply_window in self.driver.window_handles:
    #                 self.driver.close()
    #             if original_window in self.driver.window_handles:
    #                 self.driver.switch_to.window(original_window)
    #         except Exception:
    #             pass
            
    def open_job(self, job):
        self.driver.get(job.url)

    def _open_in_new_tab_and_switch(self, url: str, timeout: int = 10) -> str:
        """
        Opens given url in the new tab via JS and switches to it
        Returns new window handle
        """
        original = self.driver.current_window_handle
        before = set(self.driver.window_handles)

        self.driver.execute_script("window.open(arguments[0], '_blank');", url)

        WebDriverWait(self.driver, timeout).until(
            lambda d: len(set(d.window_handles) - before) == 1
        )

        new_handle = list(set(self.driver.window_handles) - before)[0]
        self.driver.switch_to.window(new_handle)
        return original