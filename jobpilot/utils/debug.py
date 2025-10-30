def dump_page(driver, prefix="artifacts/last"):
    import os
    os.makedirs("artifacts", exist_ok=True)
    driver.save_screenshot(f"{prefix}.png")
    with open(f"{prefix}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)