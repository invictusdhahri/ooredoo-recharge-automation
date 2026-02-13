#!/usr/bin/env python3
"""
Ooredoo Payment API with Comprehensive Logging
Monitors payment flow and returns structured API response
"""

import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs


class PaymentFlowLogger:
    """Comprehensive logging of payment flow"""
    
    def __init__(self, log_file='payment_flow.log'):
        self.log_file = log_file
        self.events = []
        
        # Setup structured logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_event(self, event_type, data):
        """Log a payment flow event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        self.events.append(event)
        
        # Pretty print for console
        self.logger.info(f"[{event_type}] {json.dumps(data, indent=2)}")
        
        return event
    
    def get_summary(self):
        """Get full summary of payment flow"""
        return {
            'total_events': len(self.events),
            'events': self.events
        }


class PaymentAPIMonitor:
    """Monitor ICPay payment and return API response"""
    
    def __init__(self, log_file='payment_flow.log'):
        self.logger = PaymentFlowLogger(log_file)
        self.driver = None
        
    def monitor_payment(self, payment_url, timeout_seconds=300):
        """
        Monitor payment completion and return API response
        
        Returns:
            dict: Structured API response with full payment details
        """
        
        # Log initial request
        self.logger.log_event('PAYMENT_INITIATED', {
            'payment_url': payment_url,
            'timeout_seconds': timeout_seconds
        })
        
        # Setup browser
        try:
            self._setup_browser()
            self.logger.log_event('BROWSER_SETUP', {'status': 'success'})
        except Exception as e:
            return self._error_response('BROWSER_SETUP_FAILED', str(e))
        
        # Open payment page
        try:
            self.logger.log_event('OPENING_PAYMENT_PAGE', {'url': payment_url})
            self.driver.get(payment_url)
            
            # Log initial page state
            self._log_page_state('INITIAL_PAGE_LOAD')
            
        except Exception as e:
            return self._error_response('PAGE_LOAD_FAILED', str(e))
        
        # Monitor for completion
        result = self._monitor_loop(payment_url, timeout_seconds)
        
        # Cleanup
        self._cleanup_browser()
        
        # Return API response
        return result
    
    def _setup_browser(self):
        """Setup Chrome browser"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--headless')  # Uncomment for headless mode
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
    def _monitor_loop(self, initial_url, timeout_seconds):
        """Main monitoring loop"""
        
        self.logger.log_event('MONITORING_STARTED', {
            'initial_url': initial_url,
            'timeout_seconds': timeout_seconds
        })
        
        start_time = time.time()
        current_url = initial_url
        check_count = 0
        
        # Track all seen URLs
        seen_urls = set([initial_url])
        
        while time.time() - start_time < timeout_seconds:
            check_count += 1
            time.sleep(1)  # Check every 1 second (faster polling)
            
            elapsed = time.time() - start_time
            
            try:
                # Get current URL via JavaScript (more reliable)
                new_url = self.driver.execute_script("return window.location.href;")
                
                # Log periodic check
                if check_count % 10 == 0:  # Every 10 seconds
                    self.logger.log_event('MONITORING_CHECK', {
                        'check_number': check_count,
                        'elapsed_seconds': round(elapsed, 1),
                        'current_url': new_url[:100] + '...' if len(new_url) > 100 else new_url,
                        'seen_urls_count': len(seen_urls)
                    })
                
                # Check all iframes for redirects (3DS often uses iframes)
                try:
                    iframe_urls = self.driver.execute_script("""
                        var urls = [];
                        var iframes = document.getElementsByTagName('iframe');
                        for (var i = 0; i < iframes.length; i++) {
                            try {
                                if (iframes[i].contentWindow && iframes[i].contentWindow.location) {
                                    urls.push(iframes[i].contentWindow.location.href);
                                }
                            } catch(e) {
                                // Cross-origin iframe, skip
                            }
                        }
                        return urls;
                    """)
                    
                    if iframe_urls:
                        for iframe_url in iframe_urls:
                            if iframe_url not in seen_urls and 'espaceclient.ooredoo' in iframe_url:
                                self.logger.log_event('IFRAME_REDIRECT_DETECTED', {
                                    'iframe_url': iframe_url,
                                    'elapsed_seconds': round(elapsed, 1)
                                })
                                
                                redirect_result = self._parse_redirect(iframe_url)
                                if redirect_result['status'] != 'unknown':
                                    return self._success_response(redirect_result, elapsed)
                except Exception as iframe_error:
                    pass  # Iframe check failed, continue
                
                # URL changed - redirect detected
                if new_url != current_url and new_url not in seen_urls:
                    self.logger.log_event('REDIRECT_DETECTED', {
                        'from_url': current_url[:100] + '...' if len(current_url) > 100 else current_url,
                        'to_url': new_url,
                        'elapsed_seconds': round(elapsed, 1)
                    })
                    
                    seen_urls.add(new_url)
                    
                    # Parse redirect for payment status
                    redirect_result = self._parse_redirect(new_url)
                    
                    if redirect_result['status'] != 'unknown':
                        # Payment completed!
                        return self._success_response(redirect_result, elapsed)
                    
                    current_url = new_url
                
                # Check if we're already on Ooredoo's success/fail page (in case we missed redirect)
                if 'espaceclient.ooredoo' in new_url:
                    self.logger.log_event('OOREDOO_PAGE_DETECTED', {
                        'url': new_url,
                        'elapsed_seconds': round(elapsed, 1)
                    })
                    
                    # Force parse this URL
                    redirect_result = self._parse_redirect(new_url)
                    if redirect_result['status'] != 'unknown':
                        return self._success_response(redirect_result, elapsed)
                
                # Check page content for success/failure indicators
                page_result = self._check_page_content()
                if page_result:
                    return self._success_response(page_result, elapsed)
                
            except Exception as e:
                self.logger.log_event('MONITORING_ERROR', {
                    'error': str(e),
                    'elapsed_seconds': round(elapsed, 1)
                })
        
        # Timeout
        return self._timeout_response(timeout_seconds)
    
    def _parse_redirect(self, url):
        """Parse redirect URL for payment status"""
        
        self.logger.log_event('PARSING_REDIRECT', {'url': url})
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        self.logger.log_event('REDIRECT_PARAMS', {
            'domain': parsed.netloc,
            'path': parsed.path,
            'params': {k: v[0] for k, v in params.items()}
        })
        
        result = {
            'status': 'unknown',
            'url': url,
            'domain': parsed.netloc,
            'path': parsed.path,
            'params': params
        }
        
        # Check for status parameters
        status_keys = ['status', 'paymentStatus', 'result', 'state', 'responseCode']
        
        for key in status_keys:
            if key in params:
                status_value = params[key][0].lower()
                
                self.logger.log_event('STATUS_PARAM_FOUND', {
                    'key': key,
                    'value': status_value
                })
                
                # Success indicators
                if status_value in ['success', 'approved', 'completed', 'paid', 'ok', '00', '0']:
                    result['status'] = 'success'
                    result['payment_status'] = 'completed'
                    result['message'] = 'Payment completed successfully'
                    
                # Failure indicators
                elif status_value in ['failed', 'declined', 'rejected', 'error', 'cancelled', 'failed']:
                    result['status'] = 'failed'
                    result['payment_status'] = 'failed'
                    result['message'] = f'Payment failed: {status_value}'
                
                # Pending
                elif status_value in ['pending', 'processing']:
                    result['status'] = 'pending'
                    result['payment_status'] = 'pending'
                    result['message'] = 'Payment is being processed'
                
                break
        
        # Check redirect domain for Ooredoo success/fail pages
        if 'espaceclient.ooredoo' in parsed.netloc or 'ooredoo.tn' in parsed.netloc:
            # Check path for success/fail indicators
            path_lower = parsed.path.lower()
            
            if 'success' in path_lower or 'payment-success' in path_lower:
                result['status'] = 'success'
                result['payment_status'] = 'completed'
                result['message'] = 'Redirected to Ooredoo success page'
                
            elif 'fail' in path_lower or 'error' in path_lower or 'payment-fail' in path_lower:
                result['status'] = 'failed'
                result['payment_status'] = 'failed'
                result['message'] = 'Redirected to Ooredoo failure page'
            
            # Even if path doesn't clearly indicate, check query params
            elif not result['status'] or result['status'] == 'unknown':
                # We're on Ooredoo domain but no clear path indicator
                # Check if params give us a clue
                if params:
                    result['status'] = 'success'  # Assume success if we got redirected with params
                    result['payment_status'] = 'completed'
                    result['message'] = 'Redirected to Ooredoo with transaction details'
        
        # Extract additional info
        if 'orderId' in params:
            result['order_id'] = params['orderId'][0]
        if 'transactionId' in params or 'transId' in params:
            result['transaction_id'] = params.get('transactionId', params.get('transId', [''])[0])[0]
        if 'amount' in params:
            result['amount'] = params['amount'][0]
        
        self.logger.log_event('REDIRECT_PARSED', result)
        
        return result
    
    def _check_page_content(self):
        """Check page content for success/failure messages"""
        try:
            page_source = self.driver.page_source.lower()
            
            # Success indicators
            success_phrases = [
                'payment successful',
                'paiement réussi',
                'opération effectuée',
                'transaction approuvée',
                'transaction approved'
            ]
            
            for phrase in success_phrases:
                if phrase in page_source:
                    self.logger.log_event('SUCCESS_MESSAGE_DETECTED', {
                        'phrase': phrase,
                        'url': self.driver.current_url
                    })
                    
                    return {
                        'status': 'success',
                        'payment_status': 'completed',
                        'message': f'Success detected in page content: "{phrase}"',
                        'url': self.driver.current_url,
                        'detection_method': 'page_content'
                    }
            
            # Failure indicators
            failure_phrases = [
                'payment failed',
                'paiement échoué',
                'transaction refusée',
                'transaction declined',
                'échec'
            ]
            
            for phrase in failure_phrases:
                if phrase in page_source:
                    self.logger.log_event('FAILURE_MESSAGE_DETECTED', {
                        'phrase': phrase,
                        'url': self.driver.current_url
                    })
                    
                    return {
                        'status': 'failed',
                        'payment_status': 'failed',
                        'message': f'Failure detected in page content: "{phrase}"',
                        'url': self.driver.current_url,
                        'detection_method': 'page_content'
                    }
            
        except Exception as e:
            self.logger.log_event('PAGE_CONTENT_CHECK_ERROR', {'error': str(e)})
        
        return None
    
    def _log_page_state(self, event_type):
        """Log current page state"""
        try:
            self.logger.log_event(event_type, {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_source_length': len(self.driver.page_source)
            })
        except Exception as e:
            self.logger.log_event(f'{event_type}_ERROR', {'error': str(e)})
    
    def _success_response(self, payment_data, elapsed_seconds):
        """Format successful payment response"""
        
        response = {
            'success': True,
            'status': payment_data.get('status', 'success'),
            'payment_status': payment_data.get('payment_status', 'completed'),
            'message': payment_data.get('message', 'Payment completed'),
            'data': {
                'order_id': payment_data.get('order_id'),
                'transaction_id': payment_data.get('transaction_id'),
                'amount': payment_data.get('amount'),
                'redirect_url': payment_data.get('url', self.driver.current_url),
                'detection_method': payment_data.get('detection_method', 'redirect_url'),
                'elapsed_seconds': round(elapsed_seconds, 1)
            },
            'timestamp': datetime.now().isoformat(),
            'log_summary': self.logger.get_summary()
        }
        
        self.logger.log_event('PAYMENT_COMPLETED', response)
        
        return response
    
    def _error_response(self, error_type, error_message):
        """Format error response"""
        
        response = {
            'success': False,
            'status': 'error',
            'payment_status': 'error',
            'error_type': error_type,
            'message': error_message,
            'timestamp': datetime.now().isoformat(),
            'log_summary': self.logger.get_summary()
        }
        
        self.logger.log_event('ERROR', response)
        
        return response
    
    def _timeout_response(self, timeout_seconds):
        """Format timeout response"""
        
        last_url = None
        try:
            if self.driver:
                last_url = self.driver.execute_script("return window.location.href;")
                
                # If we timed out but we're on Ooredoo's page, try to parse it
                if last_url and 'espaceclient.ooredoo' in last_url:
                    self.logger.log_event('TIMEOUT_ON_OOREDOO_PAGE', {
                        'url': last_url,
                        'attempting_parse': True
                    })
                    
                    # Try to parse the URL we ended up on
                    redirect_result = self._parse_redirect(last_url)
                    if redirect_result['status'] != 'unknown':
                        # We found the status even though we timed out!
                        return self._success_response(redirect_result, timeout_seconds)
        except Exception as e:
            self.logger.log_event('TIMEOUT_URL_CHECK_ERROR', {'error': str(e)})
        
        response = {
            'success': False,
            'status': 'timeout',
            'payment_status': 'pending',
            'message': f'Payment monitoring timed out after {timeout_seconds} seconds',
            'data': {
                'timeout_seconds': timeout_seconds,
                'last_url': last_url
            },
            'timestamp': datetime.now().isoformat(),
            'log_summary': self.logger.get_summary()
        }
        
        self.logger.log_event('TIMEOUT', response)
        
        return response
    
    def _cleanup_browser(self):
        """Cleanup browser"""
        if self.driver:
            try:
                self.logger.log_event('CLEANUP', {'status': 'closing_browser'})
                time.sleep(3)  # Keep open briefly so user can see final state
                self.driver.quit()
            except Exception as e:
                self.logger.log_event('CLEANUP_ERROR', {'error': str(e)})


def monitor_payment_api(payment_url, timeout_seconds=300, log_file='payment_flow.log'):
    """
    Convenience function to monitor payment and get API response
    
    Args:
        payment_url (str): ICPay payment URL
        timeout_seconds (int): Timeout in seconds
        log_file (str): Path to log file
    
    Returns:
        dict: Structured API response
    """
    monitor = PaymentAPIMonitor(log_file=log_file)
    return monitor.monitor_payment(payment_url, timeout_seconds)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Payment API Monitor with Comprehensive Logging")
        print()
        print("Usage: python payment_api.py <payment_url> [timeout_seconds] [log_file]")
        print()
        print("Example:")
        print('  python payment_api.py "https://ipay.clictopay.com/..." 300 payment.log')
        print()
        print("Returns: JSON API response with payment status")
        print()
        sys.exit(1)
    
    payment_url = sys.argv[1]
    timeout_seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    log_file = sys.argv[3] if len(sys.argv) > 3 else 'payment_flow.log'
    
    print()
    print("=" * 70)
    print("PAYMENT API MONITOR")
    print("=" * 70)
    print(f"Payment URL: {payment_url[:60]}...")
    print(f"Timeout: {timeout_seconds}s")
    print(f"Log file: {log_file}")
    print("=" * 70)
    print()
    
    result = monitor_payment_api(payment_url, timeout_seconds, log_file)
    
    print()
    print("=" * 70)
    print("API RESPONSE")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("=" * 70)
    print()
    print(f"📝 Full logs saved to: {log_file}")
    print()
    
    sys.exit(0 if result['success'] else 1)
