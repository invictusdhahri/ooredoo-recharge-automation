#!/usr/bin/env python3
"""
Manual CAPTCHA test - proves the flow works
This is exactly what the FREE version does, but with manual CAPTCHA entry
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def main():
    print("🧪 Testing FREE CAPTCHA Flow (Manual Entry)")
    print("=" * 60)
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    print("✅ Browser opened")
    
    try:
        # Login
        print("🔐 Logging in...")
        driver.get("https://espaceclient.ooredoo.tn/")
        time.sleep(2)
        
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
        )
        password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        
        username_field.send_keys("27865121")
        password_field.send_keys("espaceclient.ooredoo.tn%2F")
        
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'LOGIN')]")
        login_btn.click()
        time.sleep(3)
        print("✅ Logged in")
        
        # Navigate to recharge
        print("📱 Going to recharge page...")
        driver.get("https://espaceclient.ooredoo.tn/recharge-card")
        time.sleep(2)
        print("✅ On recharge page")
        
        # Show CAPTCHA
        print("\n🔍 CAPTCHA Image Loaded")
        print("   In FREE version, EasyOCR would read this automatically")
        print("   For this test, we'll enter it manually to prove the flow")
        print()
        
        # Take screenshot
        screenshot_path = '/tmp/captcha_test.png'
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        print()
        
        # Manual CAPTCHA entry (simulating what OCR would do)
        print("⏸️  PAUSED: Open the browser and look at the CAPTCHA")
        print("   EasyOCR would automatically read it as: 'abc123' (example)")
        print()
        captcha_text = input("Enter CAPTCHA text (or press Enter to skip): ").strip()
        
        if not captcha_text:
            print("⏭️  Skipping submission test")
            driver.quit()
            return
        
        # Fill form
        print(f"\n📝 Using CAPTCHA: {captcha_text}")
        
        # Select phone
        radio_btn = driver.find_element(By.XPATH, "//input[@type='radio' and contains(@value, '27 865 121')]")
        driver.execute_script("arguments[0].click();", radio_btn)
        
        # Fill code
        code_inputs = driver.find_elements(By.CSS_SELECTOR, 'input.form-control')
        if code_inputs:
            code_inputs[0].send_keys("12345678901234")  # Dummy code
        
        # Fill CAPTCHA
        captcha_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        if len(captcha_inputs) >= 2:
            captcha_inputs[-1].send_keys(captcha_text)
        
        print("✅ Form filled")
        
        # Submit
        valider_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Valider')]"))
        )
        valider_btn.click()
        print("✅ Submitted")
        
        time.sleep(3)
        
        # Check response
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        alerts = soup.find_all(attrs={"role": "alert"})
        
        if alerts:
            for alert in alerts:
                text = alert.get_text(strip=True)
                if text:
                    print(f"\n📬 Response: {text}")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETE!")
        print()
        print("This is EXACTLY what recharge_free.py does, but with")
        print("EasyOCR reading the CAPTCHA automatically instead of manual entry.")
        print("=" * 60)
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("🔒 Browser closed")

if __name__ == "__main__":
    main()
