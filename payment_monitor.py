#!/usr/bin/env python3
"""
Monitor ipay payment status by watching for redirects
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def monitor_payment(payment_url, timeout_seconds=300):
    """
    Open payment URL and monitor for completion
    
    Args:
        payment_url (str): The ipay payment URL
        timeout_seconds (int): Max time to wait for payment (default 5 minutes)
    
    Returns:
        dict: Payment result with status, transaction_id, etc.
    """
    
    # Setup browser
    chrome_options = Options()
    # Use visible browser so user can complete payment
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🌐 Opening payment page...")
        print(f"   URL: {payment_url[:80]}...")
        driver.get(payment_url)
        
        print(f"⏳ Waiting for user to complete payment (timeout: {timeout_seconds}s)...")
        print("   User should enter card details and confirm payment")
        
        start_time = time.time()
        current_url = payment_url
        
        # Poll the URL for changes
        while time.time() - start_time < timeout_seconds:
            time.sleep(2)  # Check every 2 seconds
            
            new_url = driver.current_url
            
            # Check if URL changed (redirect happened)
            if new_url != current_url:
                print(f"\n✅ Redirect detected!")
                print(f"   New URL: {new_url}")
                
                # Parse the redirect URL for payment status
                result = parse_redirect_url(new_url)
                
                if result['status'] != 'unknown':
                    return result
                
                current_url = new_url
            
            # Check for success/failure indicators in page content
            page_source = driver.page_source.lower()
            
            if 'payment successful' in page_source or 'paiement réussi' in page_source or 'opération effectuée' in page_source:
                print("✅ Success message detected in page!")
                return {
                    'status': 'success',
                    'url': driver.current_url,
                    'message': 'Payment successful'
                }
            
            if 'payment failed' in page_source or 'paiement échoué' in page_source or 'échec' in page_source:
                print("❌ Failure message detected in page!")
                return {
                    'status': 'failed',
                    'url': driver.current_url,
                    'message': 'Payment failed'
                }
            
            # Show progress
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0:  # Every 30 seconds
                print(f"   Still waiting... ({elapsed}s elapsed)")
        
        # Timeout
        print(f"\n⏱️  Timeout after {timeout_seconds} seconds")
        return {
            'status': 'timeout',
            'url': driver.current_url,
            'message': f'No payment completion detected within {timeout_seconds}s'
        }
        
    finally:
        # Keep browser open for 5 seconds so user can see final result
        print("\n🔍 Keeping browser open for 5 seconds...")
        time.sleep(5)
        driver.quit()


def parse_redirect_url(url):
    """
    Extract payment status from redirect URL parameters
    
    Common patterns:
    - ?status=success
    - ?status=approved
    - ?status=failed
    - ?orderId=xxx&status=yyy
    """
    from urllib.parse import urlparse, parse_qs
    
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    result = {
        'status': 'unknown',
        'url': url,
        'params': params
    }
    
    # Check for common status parameters
    status_keys = ['status', 'paymentStatus', 'result', 'state']
    
    for key in status_keys:
        if key in params:
            status_value = params[key][0].lower()
            
            # Success indicators
            if status_value in ['success', 'approved', 'completed', 'paid', 'ok']:
                result['status'] = 'success'
                result['message'] = 'Payment successful'
                
            # Failure indicators
            elif status_value in ['failed', 'declined', 'rejected', 'error', 'cancelled']:
                result['status'] = 'failed'
                result['message'] = f'Payment failed: {status_value}'
            
            # Pending/Processing
            elif status_value in ['pending', 'processing']:
                result['status'] = 'pending'
                result['message'] = 'Payment pending'
            
            break
    
    # Extract other useful info
    if 'orderId' in params:
        result['order_id'] = params['orderId'][0]
    if 'transactionId' in params:
        result['transaction_id'] = params['transactionId'][0]
    if 'amount' in params:
        result['amount'] = params['amount'][0]
    
    return result


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python payment_monitor.py <payment_url>")
        print("Example: python payment_monitor.py 'https://ipay.clictopay.com/...'")
        sys.exit(1)
    
    payment_url = sys.argv[1]
    result = monitor_payment(payment_url)
    
    print("\n" + "="*60)
    print("PAYMENT RESULT")
    print("="*60)
    print(f"Status: {result['status']}")
    if 'message' in result:
        print(f"Message: {result['message']}")
    if 'order_id' in result:
        print(f"Order ID: {result['order_id']}")
    if 'transaction_id' in result:
        print(f"Transaction ID: {result['transaction_id']}")
    print("="*60)
