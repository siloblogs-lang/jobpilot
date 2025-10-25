import os
import pytest
from dotenv import load_dotenv
from jobpilot.browser.engine import build_driver
from jobpilot.providers.dice.pages.login_page_email_submit import LoginPageEmailSubmit

def have_creds():
    return bool(os.getenv("DICE_EMAIL"))

@pytest.mark.skipif(not have_creds(), reason="DICE_EMAIL not set")
def test_can_open_email_submit():
    load_dotenv()
    d = build_driver(headless=False)
    try:
        page = LoginPageEmailSubmit(d).open()
        page.login_email_submit(os.getenv("DICE_EMAIL"))
        # Assert that browser navigates to password page
        assert "/login/password" in d.current_url.lower()

    finally:
        d.quit()