from __future__ import annotations
from typing import Iterable, List
from selenium.webdriver.remote.webdriver import WebDriver

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

    def search(self, max_results: int=100) -> List(JobPosting):
        """
         Perform a search and return JobPosting objects

        """
        max_results = min(
            max_results,
            int(self.search_cfg.get("max_results", max_results))
        )

        keywords = self.search_cfg.get("keywords") or []
        locations = self.search_cfg.get("locations") or []

        if not keywords or not locations:
            raise RuntimeError("No keyword or locations configured for search")
        
        keyword = keywords[0]
        location = locations[0]

        search_page = SearchPage(self.driver).open()
        search_page.search(keyword=keyword, location=location)

        results_page = ResultsPage(self.driver)
        jobs = results_page.iterate_all(max_results=max_results)

        return jobs
    
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
        return bool(job.easy_apply())
    
    def apply(self, job: JobPosting) -> ApplyResult:
        return ApplyResult(
            status="SKIPPED",
            app_id=None,
            notes="Apply() not implemented yet for DiceProvoder"
        )
        
    def open_job(self, job):
        self.driver.get(job.url)

