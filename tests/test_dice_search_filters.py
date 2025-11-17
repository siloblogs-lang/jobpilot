import os, pytest
import time
from dotenv import load_dotenv
from jobpilot.browser.engine import build_driver
from jobpilot.providers.dice.pages.login_page_email_submit import LoginPageEmailSubmit
from jobpilot.providers.dice.pages.login_page_password_submit import LoginPagePasswordSubmit
from jobpilot.providers.dice.pages.search_page import SearchPage
from jobpilot.providers.dice.pages.filters_modal import FiltersModal
from jobpilot.providers.dice.pages.results_page import ResultsPage
from jobpilot.utils.debug import dump_page



# Creds
login_email = os.getenv("DICE_EMAIL")
password = os.getenv("DICE_PASSWORD")

def have_creds():
    return bool(login_email and password)

@pytest.mark.skipif(not have_creds(), reason="DICE_EMAIL or DICE_PASSWORD not set")
def test_search_with_date_worktype_filters():
    load_dotenv()
    driver = build_driver(headless=False)
    try:
        LoginPageEmailSubmit(driver).open().login_email_submit(login_email)
        LoginPagePasswordSubmit(driver).login_password_submit(password)
        time.sleep(15)
        SearchPage(driver).open().search(keyword="QA Automation", location="Remote")
        filters_modal = SearchPage(driver).open_filters()
        filters_modal.wait_open()\
            .set_posted_date("today")\
            .set_work_settings(remote=True)\
            .set_distance("10_miles")\
            .apply_filters()
        # FiltersModal(driver).set_posted_date("today")
        # FiltersModal(driver).set_work_settings(remote=True)
        # FiltersModal(driver).set_distance("10_miles")
        results = ResultsPage(driver).iterate_first_n(3)
        print(results)
        assert len(results) > 0
    except Exception:
        dump_page(driver)
        raise
    finally:
        driver.quit()