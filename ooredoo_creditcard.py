#!/usr/bin/env python3
"""
Ooredoo Tunisia Credit Card Recharge Automation
No CAPTCHA needed (requires login)
"""

import os
import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class OoredooCreditCardRecharge:
    """
    Ooredoo Tunisia credit card recharge
    """
    
    def __init__(self, headless=False):
        """
        Args:
            headless (bool): Run browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        # Use headless mode on Linux servers, visible on Mac/Windows
        if self.headless or sys.platform.startswith('linux'):
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Use Chromium if available (Linux only)
        if sys.platform.startswith('linux'):
            chrome_options.binary_location = '/usr/bin/chromium'
        
        # Anti-detection measures
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        # Hide webdriver property
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        self.wait = WebDriverWait(self.driver, 20)
        
    def login(self, username, password):
        """
        Login to Ooredoo portal
        
        Args:
            username (str): Phone number (e.g., "27865121")
            password (str): Account password
        
        Returns:
            bool: True if login successful
        """
        try:
            print(f"🔐 Logging in as {username}...")
            
            self.driver.get("https://espaceclient.ooredoo.tn/")
            time.sleep(3)
            
            # Find and fill login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button (it's an input type="submit", not a button element)
            login_btn = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"].form-submit')
            self.driver.execute_script("arguments[0].click();", login_btn)
            
            time.sleep(4)
            
            # Check if login was successful
            if "espaceclient.ooredoo.tn" in self.driver.current_url and "login" not in self.driver.current_url.lower():
                print("✅ Logged in successfully!")
                return True
            else:
                print("❌ Login failed - still on login page")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def recharge(self, username, password, beneficiary_number, amount):
        """
        Perform credit card recharge
        
        Args:
            username (str): Login phone number (e.g., "27865121")
            password (str): Login password
            beneficiary_number (str): Number to recharge (can be same as username)
            amount (int): Recharge amount in TND (e.g., 10, 20, 50)
        
        Returns:
            dict: Result with payment URL
        """
        try:
            self._setup_driver()
            
            print("🚀 Starting Ooredoo credit card recharge...")
            
            # Step 1: Login
            if not self.login(username, password):
                return {
                    'status': 'error',
                    'message': 'Login failed'
                }
            
            # Step 2: Navigate to recharge online page
            print("📱 Navigating to recharge online page...")
            self.driver.get("https://espaceclient.ooredoo.tn/recharge-online")
            time.sleep(3)
            
            # Step 3: Select beneficiary number (from "Mes numéros" dropdown)
            print(f"📞 Selecting beneficiary: {beneficiary_number}")
            
            # Look for the number in the list and click it
            try:
                # The number appears as a selectable element
                number_element = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{beneficiary_number}')]"))
                )
                self.driver.execute_script("arguments[0].click();", number_element)
                print(f"✅ Selected number: {beneficiary_number}")
            except:
                print(f"⚠️  Could not find number in dropdown, assuming already selected")
            
            time.sleep(2)
            
            # Step 4: Select amount
            print(f"💰 Selecting amount: {amount} TND")
            
            # Predefined amounts available in dropdown
            predefined_amounts = [2, 5, 10, 15, 20, 30, 40, 50]
            use_custom = amount not in predefined_amounts
            
            try:
                # Click the dropdown to open it
                print("   Opening amount dropdown...")
                dropdown = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Montant de la recharge')]"))
                )
                self.driver.execute_script("arguments[0].click();", dropdown)
                time.sleep(1)
                
                if use_custom:
                    # Click "Autre montant" for custom amounts
                    print(f"   Selecting 'Autre montant' for custom amount: {amount} DT")
                    autre_montant = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Autre montant')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", autre_montant)
                    time.sleep(1)
                    
                    # Enter the custom amount in the input field
                    amount_input = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="text"], input[type="number"]'))
                    )
                    amount_input.clear()
                    time.sleep(0.5)
                    amount_input.send_keys(str(amount))
                    print(f"   ✅ Entered custom amount: {amount} DT")
                else:
                    # Click the predefined amount option
                    print(f"   Selecting predefined amount: {amount} DT")
                    amount_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{amount} DT')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", amount_option)
                    print(f"   ✅ Selected {amount} DT")
                    
            except Exception as amount_error:
                print(f"   ⚠️  Amount selection error: {amount_error}")
                raise
            
            time.sleep(1)
            
            # Step 5: Click first Valider button
            print("✅ Clicking Valider (step 1)...")
            valider_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Valider')]")
            self.driver.execute_script("arguments[0].click();", valider_btn)
            
            time.sleep(3)
            
            # Step 6: Confirm on the confirmation page
            print("✅ Clicking Valider (step 2 - confirmation)...")
            
            # Wait for confirmation page to load
            # Should show summary with beneficiary number and amount
            
            # Click the second Valider button
            valider_confirm = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Valider')]"))
            )
            
            # Set up network logging to capture the redirect
            print("🔍 Enabling network logging...")
            self.driver.execute_cdp_cmd('Network.enable', {})
            
            # Click confirm button
            print("💳 Clicking final Valider button...")
            self.driver.execute_script("arguments[0].click();", valider_confirm)
            
            # Step 7: Wait for redirect and capture URL
            print("⏳ Waiting for redirect to payment...")
            payment_url = None
            
            # Wait for navigation to complete
            time.sleep(5)
            
            # Check current URL first (might have been redirected)
            current_url = self.driver.current_url
            print(f"   Current URL after click: {current_url}")
            
            if 'ipay' in current_url or 'clictopay' in current_url:
                print("✅ Payment URL obtained from browser redirect!")
                payment_url = current_url
            else:
                # Try to find redirect URL in page source
                print("   Checking page source for payment URL...")
                page_source = self.driver.page_source
                print(f"   Page source length: {len(page_source)} chars")
                
                # Look for meta refresh tag with URL
                import re
                meta_refresh = re.search(r'<meta[^>]*http-equiv=["\']?refresh["\']?[^>]*content=["\']?\d+;\s*url=([^"\'>\s]+)', page_source, re.IGNORECASE)
                if meta_refresh:
                    payment_url = meta_refresh.group(1)
                    payment_url = payment_url.replace('&amp;', '&')
                    print("   ✅ Found payment URL in meta refresh tag!")
                    print(f"   URL: {payment_url[:80]}...")
                else:
                    # Try broader ipay search
                    ipay_match = re.search(r'https?://[^"\s<>]*ipay[^"\s<>]*', page_source, re.IGNORECASE)
                    if ipay_match:
                        payment_url = ipay_match.group(0)
                        # Clean up HTML entities
                        payment_url = payment_url.replace('&amp;', '&')
                        # Remove any trailing HTML
                        payment_url = payment_url.split('"')[0].split("'")[0].split('<')[0]
                        print("   ✅ Found payment URL in page source!")
                        print(f"   URL: {payment_url[:80]}...")
            
            # If we got the payment URL, return success
            if payment_url:
                return {
                    'status': 'success',
                    'payment_url': payment_url,
                    'beneficiary': beneficiary_number,
                    'amount': amount
                }
            
            # Fallback: try to find URL in page source
            page_source = self.driver.page_source
            if 'ipay' in page_source:
                import re
                match = re.search(r'https://[^"\s<>]*ipay[^"\s<>]*', page_source)
                if match:
                    payment_url = match.group(0)
                    # Decode HTML entities
                    payment_url = payment_url.replace('&amp;', '&')
                    print(f"✅ Payment URL found in page source!")
                    return {
                        'status': 'success',
                        'payment_url': payment_url,
                        'beneficiary': beneficiary_number,
                        'amount': amount
                    }
            
            print("⚠️  Payment initiated but URL not captured automatically")
            current_url = self.driver.current_url
            return {
                'status': 'partial_success',
                'message': 'Reached payment step - check browser for payment URL',
                'current_url': current_url
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': str(e)
            }
        
        finally:
            if self.driver:
                time.sleep(5)  # Keep browser open to see result
                # self.driver.quit()  # Uncomment in production


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python ooredoo_creditcard.py <login_username> <login_password> <beneficiary_number> <amount>")
        print("Example: python ooredoo_creditcard.py 27865121 mypassword 27865121 10")
        print()
        print("Login credentials:")
        print("  login_username: Your Ooredoo account phone number")
        print("  login_password: Your espaceclient.ooredoo.tn password")
        print()
        print("Recharge details:")
        print("  beneficiary_number: Number to recharge (can be same as login)")
        print("  amount: Amount in TND (e.g., 10, 20, 50)")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    beneficiary = sys.argv[3]
    amount = int(sys.argv[4])
    
    recharger = OoredooCreditCardRecharge()
    result = recharger.recharge(
        username=username,
        password=password,
        beneficiary_number=beneficiary,
        amount=amount
    )
    
    print("\n" + "="*60)
    print("RECHARGE RESULT")
    print("="*60)
    print(f"Status:  {result['status']}")
    if result.get('payment_url'):
        print(f"Payment URL: {result['payment_url']}")
    if result.get('message'):
        print(f"Message: {result['message']}")
    print("="*60)


if __name__ == '__main__':
    main()
