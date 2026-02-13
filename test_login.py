#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = '/usr/bin/chromium'

driver = webdriver.Chrome(options=options)
driver.get("https://espaceclient.ooredoo.tn/")
time.sleep(5)

print("Page title:", driver.title)
print("\nPage source (first 2000 chars):")
print(driver.page_source[:2000])

print("\n\nLooking for buttons:")
buttons = driver.find_elements(By.TAG_NAME, 'button')
print(f"Found {len(buttons)} buttons")
for i, btn in enumerate(buttons[:5]):
    print(f"  Button {i}: text='{btn.text}', class='{btn.get_attribute('class')}'")

print("\n\nLooking for submit inputs:")
submits = driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
print(f"Found {len(submits)} submit buttons")
for i, sub in enumerate(submits):
    print(f"  Submit {i}: value='{sub.get_attribute('value')}', class='{sub.get_attribute('class')}'")

driver.quit()
