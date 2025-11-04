from selenium import webdriver
from jobpilot.browser.engine import build_driver
from jobpilot.utils.config import load_configs
from jobpilot.providers.dice.provider import DiceProvider


def main() -> None:
    # Load all the YAML configs
    cfg = load_configs()

    # Build selenium driver
    driver = build_driver(headless=False)

    try:
        # Create provider with driver + config
        provider = DiceProvider(driver, cfg)

        # Login to Dice
        provider.login()

        # Run a search and get JobPosting objects
        jobs = provider.search(max_results=5)
        for job in jobs:
            # Pring fields for validation
            print(job.title, "|", job.company, "|", job.url, "| easy:", job.easy_apply)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()