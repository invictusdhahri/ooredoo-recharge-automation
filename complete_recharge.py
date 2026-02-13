#!/usr/bin/env python3
"""
Complete Ooredoo recharge with payment monitoring
Combines recharge creation + payment tracking in one flow
"""

from ooredoo_creditcard import OoredooCreditCardRecharge
from payment_monitor import monitor_payment
import sys


def complete_recharge_with_monitoring(phone, password, beneficiary, amount):
    """
    Full recharge flow with payment monitoring
    
    Args:
        phone (str): Login phone number
        password (str): Login password
        beneficiary (str): Number to recharge
        amount (int): Amount in TND
    
    Returns:
        dict: Complete result with recharge and payment status
    """
    
    # Step 1: Create recharge and get payment URL
    print("=" * 60)
    print("STEP 1: Creating Recharge")
    print("=" * 60)
    
    recharger = OoredooCreditCardRecharge()
    result = recharger.recharge(
        username=phone,
        password=password,
        beneficiary_number=beneficiary,
        amount=amount
    )
    
    if result['status'] != 'success':
        print(f"\n❌ Recharge creation failed: {result.get('message')}")
        return {
            'success': False,
            'stage': 'recharge_creation',
            'error': result.get('message'),
            'recharge_result': result
        }
    
    payment_url = result['payment_url']
    print(f"\n✅ Payment URL obtained!")
    print(f"   URL: {payment_url[:80]}...")
    
    # Step 2: Monitor payment completion
    print("\n" + "=" * 60)
    print("STEP 2: Monitoring Payment Completion")
    print("=" * 60)
    print("💳 Opening payment page for user to complete...")
    print("   The browser will open automatically")
    print("   User should enter card details and confirm")
    print()
    
    payment_result = monitor_payment(payment_url, timeout_seconds=300)
    
    # Step 3: Process final result
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    
    if payment_result['status'] == 'success':
        print("🎉 RECHARGE COMPLETED SUCCESSFULLY!")
        print()
        print(f"   Beneficiary: {beneficiary}")
        print(f"   Amount: {amount} TND")
        if 'order_id' in payment_result:
            print(f"   Order ID: {payment_result['order_id']}")
        if 'transaction_id' in payment_result:
            print(f"   Transaction ID: {payment_result['transaction_id']}")
        print()
        
        # TODO: Add your custom actions here
        # Examples:
        # - Send SMS confirmation: send_sms(beneficiary, f"Recharge of {amount} TND successful!")
        # - Update database: db.mark_payment_complete(order_id, transaction_id)
        # - Send webhook: requests.post('https://your-api.com/webhook', json=payment_result)
        # - Log to file: log_payment(payment_result)
        
        return {
            'success': True,
            'beneficiary': beneficiary,
            'amount': amount,
            'order_id': payment_result.get('order_id'),
            'transaction_id': payment_result.get('transaction_id'),
            'payment_url': payment_url,
            'redirect_url': payment_result.get('url'),
            'recharge_result': result,
            'payment_result': payment_result
        }
        
    elif payment_result['status'] == 'failed':
        print("❌ PAYMENT FAILED!")
        print()
        print(f"   Reason: {payment_result.get('message', 'Unknown')}")
        print()
        
        return {
            'success': False,
            'stage': 'payment',
            'error': payment_result.get('message', 'Payment failed'),
            'beneficiary': beneficiary,
            'amount': amount,
            'payment_url': payment_url,
            'recharge_result': result,
            'payment_result': payment_result
        }
        
    elif payment_result['status'] == 'timeout':
        print("⏱️  PAYMENT TIMEOUT!")
        print()
        print("   The payment was not completed within the timeout period")
        print("   Please check the payment status manually")
        print()
        
        return {
            'success': False,
            'stage': 'payment',
            'error': 'Timeout waiting for payment completion',
            'beneficiary': beneficiary,
            'amount': amount,
            'payment_url': payment_url,
            'recharge_result': result,
            'payment_result': payment_result
        }
    
    else:
        print("⚠️  UNKNOWN STATUS!")
        print()
        print(f"   Status: {payment_result.get('status', 'unknown')}")
        print()
        
        return {
            'success': False,
            'stage': 'payment',
            'error': 'Unknown payment status',
            'beneficiary': beneficiary,
            'amount': amount,
            'payment_url': payment_url,
            'recharge_result': result,
            'payment_result': payment_result
        }
    
    print("=" * 60)


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Complete Ooredoo Recharge with Payment Monitoring")
        print()
        print("Usage: python complete_recharge.py <login_phone> <password> <beneficiary> <amount>")
        print()
        print("Example:")
        print('  python complete_recharge.py 27865121 "mypassword" 27865121 20')
        print()
        print("This will:")
        print("  1. Create the recharge and get payment URL")
        print("  2. Open payment page in browser")
        print("  3. Wait for user to complete payment")
        print("  4. Detect payment completion and show result")
        print()
        sys.exit(1)
    
    phone = sys.argv[1]
    password = sys.argv[2]
    beneficiary = sys.argv[3]
    amount = int(sys.argv[4])
    
    print()
    print("🚀 Starting Complete Recharge Flow...")
    print()
    print(f"   Login: {phone}")
    print(f"   Beneficiary: {beneficiary}")
    print(f"   Amount: {amount} TND")
    print()
    
    result = complete_recharge_with_monitoring(phone, password, beneficiary, amount)
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)
