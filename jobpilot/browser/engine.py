from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def build_driver(headless: bool = False):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")

    # Anti-automation fingerprints
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    #  # 👇 This keeps the browser window open after the driver quits
    # opts.add_experimental_option("detach", True)

    # Useful for CI/macs
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.implicitly_wait(0)
    return driver