#!/usr/bin/env python3
"""
Intercept payment redirect and prevent default behavior
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def intercept_payment_redirect(payment_url, on_redirect_callback=None):
    """
    Open payment and intercept the redirect before it happens
    
    Args:
        payment_url (str): The ipay payment URL
        on_redirect_callback (callable): Function to call when redirect is detected
                                         Receives (redirect_url, payment_result)
    
    Returns:
        dict: Payment result
    """
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🌐 Opening payment page...")
        driver.get(payment_url)
        
        # Inject JavaScript to intercept redirects
        print("🔒 Injecting redirect interceptor...")
        driver.execute_script("""
            // Store original location.href setter
            var originalHref = Object.getOwnPropertyDescriptor(Location.prototype, 'href').set;
            
            // Override location.href setter
            Object.defineProperty(Location.prototype, 'href', {
                set: function(value) {
                    console.log('Redirect intercepted:', value);
                    window.__interceptedRedirect = value;
                    
                    // Prevent the actual redirect by not calling originalHref
                    // Instead, show a custom message
                    document.body.innerHTML = '<h1>Payment Completed!</h1><p>Redirect URL: ' + value + '</p>';
                    
                    return true;
                }
            });
            
            // Also intercept window.location.replace()
            var originalReplace = window.location.replace;
            window.location.replace = function(url) {
                console.log('Redirect (replace) intercepted:', url);
                window.__interceptedRedirect = url;
                document.body.innerHTML = '<h1>Payment Completed!</h1><p>Redirect URL: ' + url + '</p>';
            };
            
            // Intercept form submissions that cause redirects
            window.addEventListener('beforeunload', function(e) {
                console.log('Page unload intercepted');
            });
            
            console.log('Redirect interceptor installed');
        """)
        
        print("⏳ Waiting for payment completion...")
        
        start_time = time.time()
        timeout = 300  # 5 minutes
        
        while time.time() - start_time < timeout:
            time.sleep(2)
            
            # Check if redirect was intercepted
            intercepted_url = driver.execute_script("return window.__interceptedRedirect;")
            
            if intercepted_url:
                print(f"\n✅ Redirect intercepted!")
                print(f"   Target URL: {intercepted_url}")
                
                # Parse the redirect URL
                from payment_monitor import parse_redirect_url
                result = parse_redirect_url(intercepted_url)
                
                # Call the callback if provided
                if on_redirect_callback:
                    on_redirect_callback(intercepted_url, result)
                
                return result
            
            # Check page for completion indicators
            page_source = driver.page_source.lower()
            
            if 'payment completed' in page_source or 'paiement effectué' in page_source:
                print("✅ Payment completion detected in page!")
                current_url = driver.current_url
                from payment_monitor import parse_redirect_url
                return parse_redirect_url(current_url)
            
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0:
                print(f"   Still waiting... ({elapsed}s elapsed)")
        
        print(f"\n⏱️  Timeout after {timeout} seconds")
        return {
            'status': 'timeout',
            'url': driver.current_url,
            'message': 'Payment not completed within timeout'
        }
        
    finally:
        print("\n🔍 Keeping browser open for inspection...")
        time.sleep(10)
        driver.quit()


def custom_redirect_handler(redirect_url, payment_result):
    """
    Example callback function that handles the redirect
    """
    print("\n" + "="*60)
    print("REDIRECT INTERCEPTED!")
    print("="*60)
    print(f"Original redirect: {redirect_url}")
    print(f"Payment status: {payment_result.get('status')}")
    print(f"Message: {payment_result.get('message')}")
    print("="*60)
    
    # Here you could:
    # - Send a webhook to your own server
    # - Update a database
    # - Send a notification
    # - Log to a file
    # - etc.
    
    # Example: Send webhook
    # import requests
    # requests.post('https://your-server.com/webhook', json=payment_result)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python payment_intercept.py <payment_url>")
        sys.exit(1)
    
    payment_url = sys.argv[1]
    result = intercept_payment_redirect(payment_url, on_redirect_callback=custom_redirect_handler)
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(f"Status: {result['status']}")
    if 'message' in result:
        print(f"Message: {result['message']}")
    print("="*60)
