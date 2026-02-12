#!/usr/bin/env python3
"""
Ooredoo Recharge Automation - Tesseract OCR Version
Uses Tesseract (completely free, system package) for CAPTCHA solving
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageEnhance
import io

# Import Tesseract OCR
try:
    import pytesseract
except ImportError:
    print("❌ pytesseract not installed. Install with: pip install pytesseract")
    print("   Also install system package: apt install tesseract-ocr (Linux) or brew install tesseract (macOS)")
    sys.exit(1)

class OoredooRecharge:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Initialize Chrome driver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✅ Browser initialized")
        
    def login(self, username="27865121", password="espaceclient.ooredoo.tn%2F"):
        """Login to Ooredoo portal"""
        print(f"🔐 Logging in as {username}...")
        
        self.driver.get("https://espaceclient.ooredoo.tn/")
        wait = WebDriverWait(self.driver, 15)
        
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
        
        time.sleep(3)
        print("✅ Logged in")
        
    def navigate_to_recharge(self):
        """Navigate to recharge card page"""
        print("📱 Navigating to recharge page...")
        self.driver.get("https://espaceclient.ooredoo.tn/recharge-card")
        time.sleep(2)
        print("✅ On recharge page")
        
    def preprocess_captcha(self, image_bytes):
        """Preprocess CAPTCHA image for better OCR accuracy"""
        # Open image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Apply threshold (binarization)
        threshold = 128
        img = img.point(lambda p: p > threshold and 255)
        
        # Slight noise reduction
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        return img
        
    def solve_captcha_tesseract(self):
        """Solve CAPTCHA using FREE Tesseract OCR"""
        print("🔍 Solving CAPTCHA with Tesseract (FREE)...")
        
        # Find and screenshot captcha
        captcha_img = self.driver.find_element(By.CSS_SELECTOR, 'img[alt="captcha"]')
        captcha_png = captcha_img.screenshot_as_png
        
        # Preprocess image for better accuracy
        preprocessed = self.preprocess_captcha(captcha_png)
        
        # Use Tesseract to read text
        # Configure for single line of text, alphanumeric only
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        captcha_text = pytesseract.image_to_string(preprocessed, config=custom_config)
        
        # Clean up
        captcha_text = captcha_text.strip().replace(' ', '').replace('\n', '')
        
        if captcha_text:
            print(f"✅ CAPTCHA solved: {captcha_text}")
            return captcha_text
        else:
            raise Exception("Could not read CAPTCHA text")
            
    def submit_recharge(self, phone_number, recharge_code, captcha_text=None):
        """Submit recharge form"""
        print(f"\n📝 Submitting recharge...")
        print(f"   Phone: {phone_number}")
        print(f"   Code: {recharge_code}")
        
        wait = WebDriverWait(self.driver, 10)
        
        # Auto-solve captcha if not provided
        if not captcha_text:
            captcha_text = self.solve_captcha_tesseract()
        
        print(f"   CAPTCHA: {captcha_text}")
        
        # Select phone number radio (my number)
        try:
            radio_btn = self.driver.find_element(
                By.XPATH, 
                f"//input[@type='radio' and contains(@value, '27 865 121')]"
            )
            self.driver.execute_script("arguments[0].click();", radio_btn)
            print("   ✅ Selected phone number")
        except:
            print("   ⚠️  Using default selection")
        
        time.sleep(0.5)
        
        # Fill recharge code
        code_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input.form-control, input[type="text"]')
        
        for inp in code_inputs:
            parent_text = inp.find_element(By.XPATH, './..').text
            if 'CODE' in parent_text or inp.get_attribute('placeholder') == '':
                inp.clear()
                inp.send_keys(recharge_code)
                print("   ✅ Filled recharge code")
                break
        
        # Fill captcha
        time.sleep(0.5)
        captcha_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        if len(captcha_inputs) >= 2:
            captcha_input = captcha_inputs[-1]
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)
            print("   ✅ Filled CAPTCHA")
        
        # Click Valider
        valider_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Valider')]"))
        )
        valider_btn.click()
        print("   ✅ Submitted!")
        
        time.sleep(3)
        
        return self.parse_response()
        
    def parse_response(self):
        """Parse page response"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        alerts = soup.find_all(attrs={"role": "alert"})
        
        messages = []
        for alert in alerts:
            text = alert.get_text(strip=True)
            if text and len(text) > 5:
                messages.append(text)
        
        success_keywords = ['succès', 'effectuée', 'réussie']
        error_keywords = ['erreur', 'invalide', 'non aboutie', 'exactement']
        
        response = {
            'status': 'unknown',
            'messages': messages,
            'html': self.driver.page_source
        }
        
        for msg in messages:
            msg_lower = msg.lower()
            if any(kw in msg_lower for kw in success_keywords):
                response['status'] = 'success'
                break
            elif any(kw in msg_lower for kw in error_keywords):
                response['status'] = 'error'
                break
        
        return response
        
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 recharge_tesseract.py <RECHARGE_CODE>")
        sys.exit(1)
    
    recharge_code = sys.argv[1]
    
    if len(recharge_code) != 14:
        print(f"❌ Error: Recharge code must be exactly 14 characters")
        sys.exit(1)
    
    bot = OoredooRecharge(headless=False)
    
    try:
        bot.login()
        bot.navigate_to_recharge()
        response = bot.submit_recharge("27865121", recharge_code)
        
        print("\n" + "="*60)
        print("RESPONSE:")
        print("="*60)
        print(f"Status: {response['status']}")
        if response['messages']:
            print("\nMessages:")
            for msg in response['messages']:
                print(f"  • {msg}")
        
        sys.exit(0 if response['status'] == 'success' else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        bot.close()

if __name__ == "__main__":
    main()
