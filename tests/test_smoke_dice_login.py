import os
import pytest
from dotenv import load_dotenv
from jobpilot.browser.engine import build_driver
from jobpilot.providers.dice.pages.login_page_email_submit import LoginPageEmailSubmit
from jobpilot.providers.dice.pages.login_page_password_submit import LoginPagePasswordSubmit
from jobpilot.providers.dice.pages.dashboard_page import DashboardPage

def have_creds():
    return bool(os.getenv("DICE_EMAIL") and os.getenv("DICE_PASSWORD"))

@pytest.mark.skipif(not have_creds(), reason="DICE_EMAIL or DICE_PASSWORD not set")
def test_can_login_and_land_on_dashboard():
    load_dotenv()
    driver = build_driver(headless=False)
    try:
        # 1) email -> password
        LoginPageEmailSubmit(driver).open().login_email_submit(os.getenv("DICE_EMAIL"))
        assert "/login/password" in driver.current_url.lower()
        
        # 2) password -> dashboard
        # returns DashboardPage and waits for it to load
        LoginPagePasswordSubmit(driver).login_password_submit(os.getenv("DICE_PASSWORD"))
 
        # 3) assert user online status text
        # Check for logged in user
        full_name = os.getenv("FULL_NAME")
        expected_text = f"{full_name} is Online"
        dashboard = DashboardPage(driver)
        dashboard.wait_online_status_for(full_name)

        # verify the text 
        actual_text = dashboard.online_status_text()
        assert actual_text == expected_text, f"Expected '{expected_text}', got '{actual_text}'"

    finally:
        driver.quit()
