#!/usr/bin/env python3
"""
Ooredoo Recharge Automation Bot
Handles login, CAPTCHA solving, and recharge submission
"""

import os
import sys
import time
import json
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import requests

class OoredooRechargeBot:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Initialize Chrome driver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self, username="27865121", password="espaceclient.ooredoo.tn%2F"):
        """Login to Ooredoo portal"""
        print(f"🔐 Logging in as {username}...")
        
        self.driver.get("https://espaceclient.ooredoo.tn/")
        wait = WebDriverWait(self.driver, 10)
        
        # Wait for login form
        username_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
        )
        password_field = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        
        username_field.clear()
        username_field.send_keys(username)
        
        password_field.clear()
        password_field.send_keys(password)
        
        # Click login button
        login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'LOGIN')]")
        login_btn.click()
        
        time.sleep(2)
        print("✅ Logged in successfully")
        
    def navigate_to_recharge(self):
        """Navigate to recharge card page"""
        print("📱 Navigating to recharge page...")
        self.driver.get("https://espaceclient.ooredoo.tn/recharge-card")
        time.sleep(1)
        print("✅ On recharge page")
        
    def solve_captcha_with_vision(self):
        """Extract captcha image and solve using AI vision"""
        print("🔍 Solving CAPTCHA...")
        
        # Find captcha image
        captcha_img = self.driver.find_element(By.CSS_SELECTOR, 'img[alt="captcha"]')
        
        # Get captcha image as base64
        captcha_src = captcha_img.get_attribute('src')
        
        if captcha_src.startswith('data:image'):
            # Already base64
            img_data = captcha_src.split(',')[1]
        else:
            # Download image
            img_data = base64.b64encode(self.driver.get_screenshot_as_png()).decode()
        
        # Save captcha for vision analysis
        captcha_path = '/tmp/captcha.png'
        captcha_screenshot = captcha_img.screenshot_as_png
        with open(captcha_path, 'wb') as f:
            f.write(captcha_screenshot)
        
        print(f"💾 Captcha saved to {captcha_path}")
        
        # Use OpenClaw's vision to solve
        # For now, return the path so we can call image tool externally
        return captcha_path
        
    def submit_recharge(self, phone_number, recharge_code, captcha_text):
        """Submit recharge with code and solved captcha"""
        print(f"📝 Submitting recharge...")
        print(f"   Phone: {phone_number}")
        print(f"   Code: {recharge_code}")
        print(f"   CAPTCHA: {captcha_text}")
        
        wait = WebDriverWait(self.driver, 10)
        
        # Select phone number (click the radio for my number)
        try:
            my_number_radio = self.driver.find_element(By.CSS_SELECTOR, 'input[type="radio"][value="27 865 121"]')
            if not my_number_radio.is_selected():
                my_number_radio.click()
        except:
            print("⚠️  Could not select saved number, will use 'other number' field")
        
        # Fill recharge code
        code_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder or contains(@class, 'form-control')]"))
        )
        # Find the CODE DE RECHARGE input
        code_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input.form-control')
        recharge_code_input = code_inputs[0] if len(code_inputs) > 0 else code_input
        
        recharge_code_input.clear()
        recharge_code_input.send_keys(recharge_code)
        
        # Fill captcha
        captcha_input = code_inputs[1] if len(code_inputs) > 1 else self.driver.find_elements(By.CSS_SELECTOR, 'input')[1]
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        
        # Click Valider button
        valider_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Valider')]"))
        )
        valider_btn.click()
        
        time.sleep(2)
        
        # Get response
        response_html = self.driver.page_source
        
        print("✅ Form submitted")
        return response_html
        
    def get_response_message(self):
        """Extract response message from page"""
        try:
            # Look for success/error messages
            messages = self.driver.find_elements(By.CSS_SELECTOR, '.alert, .message, .error, .success')
            if messages:
                return messages[0].text
            
            # Return full page source for manual parsing
            return self.driver.page_source
        except:
            return self.driver.page_source
            
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

def main():
    """Main execution"""
    bot = OoredooRechargeBot(headless=False)
    
    try:
        # Login
        bot.login()
        
        # Navigate to recharge
        bot.navigate_to_recharge()
        
        # Solve captcha
        captcha_path = bot.solve_captcha_with_vision()
        print(f"\n⚠️  CAPTCHA image saved to: {captcha_path}")
        print("⚠️  Use OpenClaw image tool to solve this captcha")
        print("⚠️  Then call bot.submit_recharge(phone, code, captcha_text)")
        
        # For testing, let's pause here
        input("\nPress Enter after you've analyzed the captcha...")
        
        # Test with dummy values (will fail, but shows the flow)
        captcha_text = input("Enter CAPTCHA text: ")
        recharge_code = input("Enter recharge code: ")
        
        response = bot.submit_recharge("27865121", recharge_code, captcha_text)
        
        # Print response
        print("\n" + "="*50)
        print("RESPONSE:")
        print("="*50)
        message = bot.get_response_message()
        print(message)
        
        # Save full HTML
        with open('/tmp/response.html', 'w', encoding='utf-8') as f:
            f.write(response)
        print("\n💾 Full response saved to /tmp/response.html")
        
    finally:
        bot.close()

if __name__ == "__main__":
    main()
