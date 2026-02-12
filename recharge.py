#!/usr/bin/env python3
"""
Ooredoo Recharge Automation
Fully automated recharge with AI CAPTCHA solving
"""

import os
import sys
import time
import base64
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class OoredooRecharge:
    def __init__(self, headless=True, vision_api_key=None):
        self.headless = headless
        self.vision_api_key = vision_api_key or os.getenv('OPENAI_API_KEY')
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
        
    def solve_captcha_vision(self):
        """Solve CAPTCHA using OpenAI Vision API"""
        print("🔍 Solving CAPTCHA...")
        
        # Find and screenshot captcha
        captcha_img = self.driver.find_element(By.CSS_SELECTOR, 'img[alt="captcha"]')
        captcha_png = captcha_img.screenshot_as_png
        captcha_b64 = base64.b64encode(captcha_png).decode('utf-8')
        
        # Call OpenAI Vision
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.vision_api_key}'
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Read the text shown in this CAPTCHA image. Return ONLY the characters you see, no explanation, no quotes, just the text."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{captcha_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 50
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            captcha_text = result['choices'][0]['message']['content'].strip()
            print(f"✅ CAPTCHA solved: {captcha_text}")
            return captcha_text
        else:
            raise Exception(f"Vision API error: {response.text}")
            
    def submit_recharge(self, phone_number, recharge_code, captcha_text=None):
        """Submit recharge form"""
        print(f"\n📝 Submitting recharge...")
        print(f"   Phone: {phone_number}")
        print(f"   Code: {recharge_code}")
        
        wait = WebDriverWait(self.driver, 10)
        
        # Auto-solve captcha if not provided
        if not captcha_text:
            captcha_text = self.solve_captcha_vision()
        
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
        
        # Find the CODE DE RECHARGE input (first one in the recharge section)
        for inp in code_inputs:
            parent_text = inp.find_element(By.XPATH, './..').text
            if 'CODE' in parent_text or inp.get_attribute('placeholder') == '':
                inp.clear()
                inp.send_keys(recharge_code)
                print("   ✅ Filled recharge code")
                break
        
        # Fill captcha (second input)
        time.sleep(0.5)
        captcha_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        if len(captcha_inputs) >= 2:
            captcha_input = captcha_inputs[-1]  # Last text input
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
        
        # Get response
        return self.parse_response()
        
    def parse_response(self):
        """Parse page response (success or error)"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Look for alert/error messages
        alerts = soup.find_all(['div'], class_=lambda x: x and ('alert' in x or 'error' in x or 'message' in x))
        
        # Also check for role="alert"
        alerts += soup.find_all(attrs={"role": "alert"})
        
        # Parse text content
        messages = []
        for alert in alerts:
            text = alert.get_text(strip=True)
            if text and len(text) > 5:  # Filter noise
                messages.append(text)
        
        # Check for success indicators
        success_keywords = ['success', 'réussi', 'confirmé', 'validé']
        error_keywords = ['error', 'erreur', 'invalide', 'incorrecte', 'exactement']
        
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
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python3 recharge.py <RECHARGE_CODE>")
        print("Example: python3 recharge.py 12345678901234")
        sys.exit(1)
    
    recharge_code = sys.argv[1]
    
    # Validate code length
    if len(recharge_code) != 14:
        print(f"❌ Error: Recharge code must be exactly 14 characters")
        print(f"   You provided: {len(recharge_code)} characters")
        sys.exit(1)
    
    bot = OoredooRecharge(headless=False)
    
    try:
        # Login
        bot.login()
        
        # Navigate to recharge
        bot.navigate_to_recharge()
        
        # Submit recharge (auto-solves captcha)
        response = bot.submit_recharge("27865121", recharge_code)
        
        # Print response
        print("\n" + "="*60)
        print("RESPONSE:")
        print("="*60)
        print(f"Status: {response['status']}")
        if response['messages']:
            print("\nMessages:")
            for msg in response['messages']:
                print(f"  • {msg}")
        
        # Save HTML
        html_path = '/tmp/ooredoo_response.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(response['html'])
        print(f"\n💾 Full HTML saved to: {html_path}")
        
        # Exit code
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
