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
            
            # Step 3: Select beneficiary number (checkbox)
            print(f"📞 Selecting beneficiary: {beneficiary_number}")
            
            try:
                # The beneficiary checkbox has a value like "21627865121" (country code + number)
                # Try multiple possible formats
                possible_values = [
                    f"216{beneficiary_number}",  # With Tunisia country code
                    beneficiary_number,          # Just the number
                ]
                
                checkbox_found = False
                for phone_value in possible_values:
                    try:
                        # Find checkbox by value attribute
                        checkbox = self.driver.find_element(
                            By.CSS_SELECTOR, 
                            f'input[type="checkbox"][name*="phones"][value="{phone_value}"]'
                        )
                        
                        if checkbox:
                            # Check if already checked
                            if not checkbox.is_selected():
                                self.driver.execute_script("arguments[0].click();", checkbox)
                                print(f"   ✅ Checked beneficiary: {beneficiary_number}")
                            else:
                                print(f"   ℹ️  Beneficiary already checked: {beneficiary_number}")
                            checkbox_found = True
                            break
                    except:
                        continue
                
                if not checkbox_found:
                    # Fallback: find any checkbox for phones and check the first one
                    checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"][name*="phones"]')
                    if checkboxes:
                        self.driver.execute_script("arguments[0].click();", checkboxes[0])
                        print(f"   ✅ Checked first available number")
                    else:
                        print(f"   ℹ️  No checkbox found, number may be pre-selected")
                        
            except Exception as e:
                print(f"   ⚠️  Checkbox selection error: {str(e)[:80]}")
            
            time.sleep(1)
            
            # Step 4: Select amount from <select> dropdown
            print(f"💰 Selecting amount: {amount} TND")
            
            # Predefined amounts available: 5, 10, 15, 20, 30, 40, 50, other
            predefined_amounts = [5, 10, 15, 20, 30, 40, 50]
            use_custom = amount not in predefined_amounts
            
            try:
                from selenium.webdriver.support.select import Select
                
                # Find the select element by name or id
                print("   Finding price select dropdown...")
                select_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name*="price"]'))
                )
                
                # Create Select object
                select = Select(select_element)
                
                if use_custom:
                    # Select "Autre montant" (value="other")
                    print(f"   Selecting 'Autre montant' for custom amount: {amount} DT")
                    select.select_by_value('other')
                    time.sleep(1)  # Wait for custom input field to appear
                    
                    # Find and fill the custom amount input field
                    print("   Entering custom amount...")
                    custom_input = self.wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name*="price_other"], input[id*="price_other"]'))
                    )
                    custom_input.clear()
                    custom_input.send_keys(str(amount))
                    print(f"   ✅ Entered custom amount: {amount} DT")
                else:
                    # Select predefined amount by value
                    print(f"   Selecting predefined amount: {amount} DT")
                    select.select_by_value(str(amount))
                    print(f"   ✅ Selected {amount} DT")
                    
            except Exception as amount_error:
                print(f"   ❌ Amount selection error: {str(amount_error)[:200]}")
                print("   Taking screenshot for debugging...")
                try:
                    self.driver.save_screenshot('/tmp/ooredoo_amount_error.png')
                    print(f"   Screenshot saved: /tmp/ooredoo_amount_error.png")
                except:
                    pass
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
