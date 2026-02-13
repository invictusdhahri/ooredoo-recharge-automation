#!/usr/bin/env python3
"""
Ooredoo Tunisia Credit Card Recharge - Auto ChromeDriver version
Uses webdriver-manager to automatically handle ChromeDriver versions
"""

import sys
import os

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ooredoo_creditcard import OoredooCreditCardRecharge
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class OoredooCreditCardRechargeAuto(OoredooCreditCardRecharge):
    """Version that auto-manages ChromeDriver"""
    
    def _setup_driver(self):
        """Setup Chrome driver with auto version management"""
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
        
        # Anti-detection measures
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to auto-download correct ChromeDriver version
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        # Hide webdriver property
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        from selenium.webdriver.support.ui import WebDriverWait
        self.wait = WebDriverWait(self.driver, 20)


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python ooredoo_creditcard_auto.py <login_username> <login_password> <beneficiary_number> <amount>")
        print("Example: python ooredoo_creditcard_auto.py 27865121 mypassword 27865121 10")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    beneficiary = sys.argv[3]
    amount = int(sys.argv[4])
    
    recharger = OoredooCreditCardRechargeAuto()
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
