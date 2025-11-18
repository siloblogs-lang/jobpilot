import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

##### LOGIN PAGES SELECTORS #####
LOGIN_EMAIL = (By.CSS_SELECTOR, "input[name='email']") 
EMAIL_SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[data-testid='sign-in-button']")

LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[name='password']")
PASSWORD_SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[data-testid='submit-password']")

##### USER DASHBOARD SELECTORS #####
### Handle headers Shadow Root ###
SHADOW_ROOT = (By.CSS_SELECTOR, "dhi-seds-nav-header")
PROFILE_GREETING = (By.CSS_SELECTOR, "h3[aria-label=\"Greeting\"]")
ONLINE_STATUS_INDICATOR = (By.CSS_SELECTOR, "div[data-testid='online-status-indicator']")
USER_ONLINE_INDICATOR = (By.CSS_SELECTOR, "span.sr-only")

##### SEARCH FUNCTIONALITY SELECTORS #####
OPEN_FILTERS_PANEL = (By.XPATH, "//button[@type='button' and .//span[normalize-space()='All filters']]")
# SEARCH_KEYWORD_INPUT = (By.XPATH, "//input[@role='combobox' and @name='q' and normalize-space(@aria-label)='Job title, skill, company, keyword']")
SEARCH_KEYWORD_INPUT = (
    By.CSS_SELECTOR,
    "input[id*='search-field-keyword'], input[name='q'], input[aria-label*='job title' i], input[aria-label*='keyword' i]"
)
# SEARCH_LOCATION_INPUT = (By.XPATH, "//input[@role='combobox' and @name='location' and normalize-space(@aria-label)='Location Field']")
SEARCH_LOCATION_INPUT = (
    By.CSS_SELECTOR,
    "input[id*='google-location-search'], input[name='location'], input[aria-label*='location' i]"
)
SEARCH_SUBMIT = (By.CSS_SELECTOR, "button[data-testid='job-search-search-bar-search-button']")

###### FILTERS PANEL OPEN/CLOSE #####
FILTERS_PANEL = (By.XPATH, "//div[contains(@class,'z-modal')][.//h2[normalize-space()='Filter Results']]")
# APPLY_FILTERS_BUTTON = (By.XPATH, "//div[contains(@class,'border-t')]//button[.//span[normalize-space()='Apply filters'] or normalize-space()='Apply filters']")
#APPLY_FILTERS_BUTTON = (By.XPATH, "//button[normalize-space()='Apply filters']")
APPLY_FILTERS_BUTTON = (
    By.XPATH,
    "//button[.//span[normalize-space()='Apply filters'] and not(@disabled)]"
)
# CLEAR_FILTERS_BUTTON = (By.XPATH, "//div[contains(@class,'border-t')]//button[.//span[normalize-space()='Clear filters'] or normalize-space()='Clear filters']")
#CLEAR_FILTERS_BUTTON = (By.XPATH, "//button[normalize-space()='Clear filters']")
CLEAR_FILTERS_BUTTON = (
    By.XPATH,
    "//button[.//span[normalize-space()='Clear filters']]"
)
CLOSE_FILTERS_BUTTON = (By.CSS_SELECTOR, "button[data-testid='undefined-close-button']")

### Filters selectors ###
JOBS_POSTED_TODAY = (By.CSS_SELECTOR, "input[name='postedDateOption'][value='ONE']")
JOBS_POSTED_THREE_DAYS = (By.CSS_SELECTOR, "input[name='postedDateOption'][value='THREE']")
JOBS_POSTED_SEVEN_DAYS = (By.CSS_SELECTOR, "input[name='postedDateOption'][value='SEVEN']")
EASY_APPLY_CHECKBOX = (By.CSS_SELECTOR, "input[name='easyApply']")
WORK_SETTING_REMOTE = (By.CSS_SELECTOR, "input[name='workPlaceTypeOptions.remote']")
WORK_SETTING_HYBRID = (By.CSS_SELECTOR, "input[name='workPlaceTypeOptions.hybrid']")
WORK_SETTING_ONSITE = (By.CSS_SELECTOR, "input[name='workPlaceTypeOptions.onsite']")
FULL_TIME = (By.CSS_SELECTOR, "input[name='employmentTypeOptions.fullTime']")
PART_TIME = (By.CSS_SELECTOR, "input[name='employmentTypeOptions.partTime']")
CONTRACT = (By.CSS_SELECTOR, "input[name='employmentTypeOptions.partTime']")
THIRD_PARTY = (By.CSS_SELECTOR, "input[name='employmentTypeOptions.thirdParty']")
TEN_MILES_DISTANCE = (By.XPATH, "//div[@role='radiogroup' and contains(@aria-label, 'How far')]//label[.//input[@type='radio' and @name='radius' and @value='10']]")
THIRTY_MILES_DISTANCE = (By.XPATH, "//div[@role='radiogroup' and contains(@aria-label, 'How far')]//label[.//input[@type='radio' and @name='radius' and @value='30']]")
DIRECT_HIRE = ()
RECRUITER = ()

###### Search Reasults #######
RESULTS_CONTAINER = (By.CSS_SELECTOR, "div[data-testid='job-search-results-container']")
JOB_SEARCH_RESULTS = (By.XPATH, "//div[@role='list' and normalize-space(@aria-label)='Job search results']")
RESULT_CARDS = (By.CSS_SELECTOR, "div[data-testid='job-card']")
EAST_APPLY_BUTTON = (By.XPATH, "//div[@data-testid='job-card']//a[.//span[normalize-space()='Easy Apply']]")
APPLY_NOW_BUTTON = (By.XPATH, "//div[@data-testid='job-card']//a[.//span[normalize-space()='Apply Now']]")

RESULT_TITLE = (By.CSS_SELECTOR, "a[data-testid=\"job-search-job-detail-link\"]")
# RESULT_COMPANY = (By.CSS_SELECTOR, "//a[@aria-label='Company Logo']/following-sibling::a[1]")
RESULT_COMPANY = (By.XPATH, ".//span[contains(@class,'logo')]//a[p]/p")
RESULT_LINK = (By.CSS_SELECTOR, "a[data-testid='job-search-job-detail-link']")
EASY_APPLY_BADGE = (By.XPATH, "//a[contains(.,'Easy Apply')]")

# EAST_APPLY_BUTTON = (By.XPATH, "//button[contains(., 'Easy Apply') or contains(., 'Quick Apply')]")
UPLOAD_RESUME_INPUT = (By.CSS_SELECTOR, "input[type='file']")
SUBMIT_APPLICATION = (By.XPATH, "//button[contains(., 'Submit') or contains(., 'Apply')]")
CONFIRMATION_TOAST = (By.CSS_SELECTOR, "[role='alert'], .Toast, .notification")

######## Job Details Page ######
JOB_DESCRIPTION_CONTAINER = (By.CSS_SELECTOR, "div[data-testid='jobDescription']")
JOB_DESCRIPTION_TOGGLE_BUTTON = (By.CSS_SELECTOR, "button[id='descriptionToggle']")
# JOB_DESCRIPTION_CONTAINER = (By.CSS_SELECTOR, "div[class^='job-detail-description-module__'][class$='__jobDescription']")
# The xpath version for backup
# JOB_DESCRIPTION_CONTAINER = (By.XPATH,  "//h3[normalize-space()='Summary']/following::div"
#     "[contains(@class,'job-detail-description-module')][1]")

