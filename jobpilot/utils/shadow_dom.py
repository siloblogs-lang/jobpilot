from selenium.webdriver.common.by import By

def find_in_shadow_chain(driver_or_root, host_selectors, final_locators):

    """
    host_selectors: list of CSS selectors  for shadow hosts in order 
    (outtter -> inner).
    final_locator: tuple (By, selector) to find inside the deepest 
    shadow root.    
    Returns a WebElement for final_locator.
    """
    current = driver_or_root
    for host_css in host_selectors:
        host = current.find_element(By.CSS_SELECTOR, host_css)
        current = host.shadow_root 
        return current.find_element(*final_locators)
    
def exists_in_shadow_chain(driver_or_root, host_selectors, final_locator):
    try:
        find_in_shadow_chain(driver_or_root, host_selectors, final_locator)
        return True
    except Exception:
        return False    