#!/usr/bin/env python3
"""
Complete Ooredoo Recharge API
Combines recharge creation + payment monitoring into single API endpoint
Returns structured JSON response instead of redirecting to Ooredoo pages
"""

import sys
import json
from datetime import datetime
from ooredoo_creditcard import OoredooCreditCardRecharge
from payment_api import PaymentAPIMonitor


class RechargeAPI:
    """Complete recharge API with logging and structured responses"""
    
    def __init__(self, log_file='recharge_api.log'):
        self.log_file = log_file
        
    def execute_recharge(self, phone, password, beneficiary, amount, timeout_seconds=300):
        """
        Execute complete recharge flow
        
        Args:
            phone (str): Login phone number
            password (str): Account password
            beneficiary (str): Number to recharge
            amount (int): Amount in TND
            timeout_seconds (int): Payment monitoring timeout
        
        Returns:
            dict: Complete API response
        """
        
        api_response = {
            'request': {
                'phone': phone,
                'beneficiary': beneficiary,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            },
            'recharge': None,
            'payment': None,
            'success': False,
            'message': None,
            'logs': []
        }
        
        # Step 1: Create recharge
        print("\n" + "=" * 70)
        print("STEP 1: CREATING RECHARGE")
        print("=" * 70)
        
        try:
            recharger = OoredooCreditCardRecharge()
            recharge_result = recharger.recharge(
                username=phone,
                password=password,
                beneficiary_number=beneficiary,
                amount=amount
            )
            
            api_response['recharge'] = {
                'status': recharge_result.get('status'),
                'message': recharge_result.get('message'),
                'payment_url': recharge_result.get('payment_url')
            }
            
            if recharge_result['status'] != 'success':
                api_response['success'] = False
                api_response['message'] = f"Recharge creation failed: {recharge_result.get('message')}"
                api_response['stage'] = 'recharge_creation'
                
                print(f"\n❌ Failed: {api_response['message']}")
                return api_response
            
            payment_url = recharge_result['payment_url']
            
            print(f"✅ Recharge created successfully")
            print(f"   Payment URL: {payment_url[:70]}...")
            
        except Exception as e:
            api_response['success'] = False
            api_response['message'] = f"Recharge creation error: {str(e)}"
            api_response['stage'] = 'recharge_creation'
            
            print(f"\n❌ Exception: {str(e)}")
            return api_response
        
        # Step 2: Monitor payment
        print("\n" + "=" * 70)
        print("STEP 2: MONITORING PAYMENT")
        print("=" * 70)
        print(f"Opening payment page (timeout: {timeout_seconds}s)...")
        print("User will enter card details and complete payment")
        print()
        
        try:
            monitor = PaymentAPIMonitor(log_file=self.log_file)
            payment_result = monitor.monitor_payment(payment_url, timeout_seconds)
            
            api_response['payment'] = payment_result
            
            # Determine overall success
            if payment_result.get('status') == 'success':
                api_response['success'] = True
                api_response['message'] = 'Recharge completed successfully'
                api_response['stage'] = 'completed'
                
                print("\n🎉 PAYMENT SUCCESSFUL!")
                
            elif payment_result.get('status') == 'failed':
                api_response['success'] = False
                api_response['message'] = 'Payment failed'
                api_response['stage'] = 'payment_failed'
                
                print("\n❌ PAYMENT FAILED!")
                
            elif payment_result.get('status') == 'timeout':
                api_response['success'] = False
                api_response['message'] = 'Payment monitoring timed out'
                api_response['stage'] = 'payment_timeout'
                
                print("\n⏱️  PAYMENT TIMEOUT!")
                
            else:
                api_response['success'] = False
                api_response['message'] = f"Unknown payment status: {payment_result.get('status')}"
                api_response['stage'] = 'payment_unknown'
                
                print(f"\n⚠️  UNKNOWN STATUS: {payment_result.get('status')}")
            
        except Exception as e:
            api_response['success'] = False
            api_response['message'] = f"Payment monitoring error: {str(e)}"
            api_response['stage'] = 'payment_monitoring'
            api_response['payment'] = {'error': str(e)}
            
            print(f"\n❌ Exception during payment monitoring: {str(e)}")
        
        # Add timestamp
        api_response['completed_at'] = datetime.now().isoformat()
        
        return api_response


def api_recharge(phone, password, beneficiary, amount, timeout_seconds=300, log_file='recharge_api.log'):
    """
    Convenience function for API recharge
    
    Returns:
        dict: Structured API response
    """
    api = RechargeAPI(log_file=log_file)
    return api.execute_recharge(phone, password, beneficiary, amount, timeout_seconds)


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print()
        print("=" * 70)
        print("OOREDOO RECHARGE API")
        print("=" * 70)
        print()
        print("Complete recharge with structured API response")
        print()
        print("Usage:")
        print("  python recharge_api.py <phone> <password> <beneficiary> <amount> [timeout] [log_file]")
        print()
        print("Arguments:")
        print("  phone       - Login phone number")
        print("  password    - Account password")
        print("  beneficiary - Number to recharge")
        print("  amount      - Amount in TND")
        print("  timeout     - Payment timeout in seconds (default: 300)")
        print("  log_file    - Log file path (default: recharge_api.log)")
        print()
        print("Example:")
        print('  python recharge_api.py 27865121 "mypass" 27865121 20 300 payment.log')
        print()
        print("Output:")
        print("  - Prints progress to console")
        print("  - Returns JSON API response")
        print("  - Saves detailed logs to file")
        print()
        print("=" * 70)
        print()
        sys.exit(1)
    
    phone = sys.argv[1]
    password = sys.argv[2]
    beneficiary = sys.argv[3]
    amount = int(sys.argv[4])
    timeout_seconds = int(sys.argv[5]) if len(sys.argv) > 5 else 300
    log_file = sys.argv[6] if len(sys.argv) > 6 else 'recharge_api.log'
    
    print()
    print("=" * 70)
    print("OOREDOO RECHARGE API")
    print("=" * 70)
    print(f"Login: {phone}")
    print(f"Beneficiary: {beneficiary}")
    print(f"Amount: {amount} TND")
    print(f"Timeout: {timeout_seconds}s")
    print(f"Log file: {log_file}")
    print("=" * 70)
    
    result = api_recharge(phone, password, beneficiary, amount, timeout_seconds, log_file)
    
    print()
    print("=" * 70)
    print("API RESPONSE")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("=" * 70)
    print()
    
    if result['success']:
        print("✅ SUCCESS")
        if result.get('payment', {}).get('data', {}).get('transaction_id'):
            print(f"   Transaction ID: {result['payment']['data']['transaction_id']}")
    else:
        print("❌ FAILED")
        print(f"   Stage: {result.get('stage', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
    
    print()
    print(f"📝 Full logs: {log_file}")
    print()
    
    sys.exit(0 if result['success'] else 1)
