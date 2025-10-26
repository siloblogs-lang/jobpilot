import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

##### LOGIN PAGES SELECTORS #####
LOGIN_EMAIL = (By.CSS_SELECTOR, "input[name=\"email\"]") 
EMAIL_SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[data-testid='sign-in-button']")

LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[name=\"password\"]")
PASSWORD_SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[data-testid='submit-password']")

##### USER DASHBOARD SELECTORS #####
### Handle headers Shadow Root ###
SHADOW_ROOT = (By.CSS_SELECTOR, "dhi-seds-nav-header")
HEADER_PROFILE_NAME = (By.CSS_SELECTOR, "button.dropdown-button[aria-label^=\"User: \"]")
PROFILE_GREETING = (By.CSS_SELECTOR, "h3[aria-label=\"Greeting\"]")
ONLINE_STATUS_INDICATOR = (By.CSS_SELECTOR, "div[data-testid='online-status-indicator']")
USER_ONLINE_INDICATOR = (By.CSS_SELECTOR, "span.sr-only")


SEARCH_KEYWORD_INPUT = (By.ID, "search-field-keyword")
SEARCH_LOCATION_INPUT = (By.ID, "google-location-search")
SEARCH_SUBMIT = (By.CSS_SELECTOR, "button[data-cy='searchButton']")

RESULT_CARDS = (By.CSS_SELECTOR, "[data-cy='search-card']")
RESULT_TITLE = (By.CSS_SELECTOR, "[data-cy='search-card-title']")
RESULT_COMPANY = (By.CSS_SELECTOR, "[data-cy='search-card-company']")
RESULT_LINK = (By.CSS_SELECTOR, "a")
EASY_APPLY_BADGE = (By.XPATH, ".//*[contains(., 'Easy Apply') or contains(., 'Quick Apply')]")

APPLY_BUTTON = (By.XPATH, "//button[contains(., 'Easy Apply') or contains(., 'Quick Apply')]")
UPLOAD_RESUME_INPUT = (By.CSS_SELECTOR, "input[type='file']")
SUBMIT_APPLICATION = (By.XPATH, "//button[contains(., 'Submit') or contains(., 'Apply')]")
CONFIRMATION_TOAST = (By.CSS_SELECTOR, "[role='alert'], .Toast, .notification")