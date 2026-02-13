# Payment Monitoring & Redirect Control 🔔

Complete guide to monitoring ipay/ClicToPay payment completion and controlling redirects.

## 📋 Table of Contents

1. [Understanding the Flow](#understanding-the-flow)
2. [Solution 1: Monitor Redirect URL](#solution-1-monitor-redirect-url)
3. [Solution 2: Intercept Redirect](#solution-2-intercept-redirect)
4. [Solution 3: Webhook/IPN (Advanced)](#solution-3-webhookipn-advanced)
5. [Complete Integration Example](#complete-integration-example)

---

## Understanding the Flow

### Normal ipay Payment Flow

```
1. Your script creates recharge
   ↓
2. Gets payment URL: https://ipay.clictopay.com/...?mdOrder=xxx
   ↓
3. User opens URL, enters card details
   ↓
4. ipay processes payment
   ↓
5. ipay redirects to: https://espaceclient.ooredoo.tn/payment-success?orderId=xxx&status=success
   ↓
6. Your application needs to detect this!
```

### What You Need

1. **Detect when payment is complete** (success or failure)
2. **Get payment details** (transaction ID, status, amount)
3. **Prevent default redirect** (optional - show your own page)
4. **Trigger actions** (webhook, notification, database update)

---

## Solution 1: Monitor Redirect URL ✅

**Best for:** Simple integration, works immediately

### How It Works

Open the payment URL in a browser and monitor the URL for changes. When ipay redirects back, parse the URL parameters to get payment status.

### Usage

```bash
# After getting payment URL from recharge script:
python3 payment_monitor.py "https://ipay.clictopay.com/payment/merchants/CLICTOPAY/payment.html?mdOrder=xxx&language=fr"
```

### What It Does

```
🌐 Opening payment page...
⏳ Waiting for user to complete payment (timeout: 300s)...
   User should enter card details and confirm payment
   Still waiting... (30s elapsed)
   Still waiting... (60s elapsed)

✅ Redirect detected!
   New URL: https://espaceclient.ooredoo.tn/payment-success?orderId=xxx&status=success

============================================================
PAYMENT RESULT
============================================================
Status: success
Message: Payment successful
Order ID: xxx
Transaction ID: yyy
============================================================
```

### Integration Example

```python
from payment_monitor import monitor_payment

# After creating recharge
payment_url = "https://ipay.clictopay.com/..."
result = monitor_payment(payment_url, timeout_seconds=300)

if result['status'] == 'success':
    print("✅ Payment successful!")
    # Update database, send notification, etc.
    transaction_id = result.get('transaction_id')
    order_id = result.get('order_id')
    
elif result['status'] == 'failed':
    print("❌ Payment failed!")
    # Handle failure
    
elif result['status'] == 'timeout':
    print("⏱️  Payment timeout - check manually")
```

### Pros & Cons

**Pros ✅**
- Simple to implement
- Works immediately
- No server setup needed
- Can see user's payment process

**Cons ❌**
- Requires browser to stay open
- User must complete payment while script runs
- Not suitable for background/async processing

---

## Solution 2: Intercept Redirect 🔒

**Best for:** Preventing default redirect, custom UI

### How It Works

Inject JavaScript to intercept the redirect before it happens. Show your own page instead of Ooredoo's success page.

### Usage

```bash
python3 payment_intercept.py "https://ipay.clictopay.com/..."
```

### What It Does

```
🌐 Opening payment page...
🔒 Injecting redirect interceptor...
⏳ Waiting for payment completion...

✅ Redirect intercepted!
   Target URL: https://espaceclient.ooredoo.tn/payment-success?status=success

============================================================
REDIRECT INTERCEPTED!
============================================================
Original redirect: https://espaceclient.ooredoo.tn/payment-success?status=success
Payment status: success
Message: Payment successful
============================================================
```

Instead of redirecting, the page shows:
```
Payment Completed!
Redirect URL: https://espaceclient.ooredoo.tn/payment-success?status=success
```

### Custom Handler

```python
from payment_intercept import intercept_payment_redirect

def my_payment_handler(redirect_url, payment_result):
    """Called when payment completes"""
    
    if payment_result['status'] == 'success':
        # Send webhook to your server
        import requests
        requests.post('https://your-api.com/webhook/payment', json={
            'order_id': payment_result.get('order_id'),
            'transaction_id': payment_result.get('transaction_id'),
            'status': 'completed',
            'timestamp': time.time()
        })
        
        # Update local database
        # db.update_payment_status(order_id, 'completed')
        
        # Send notification
        # send_sms(user_phone, "Your payment was successful!")

# Run with custom handler
result = intercept_payment_redirect(payment_url, on_redirect_callback=my_payment_handler)
```

### Pros & Cons

**Pros ✅**
- Full control over redirect behavior
- Can show custom UI
- Webhook integration easy
- Cleaner user experience

**Cons ❌**
- More complex than simple monitoring
- JavaScript injection might not work if ipay changes structure
- Still requires browser to stay open

---

## Solution 3: Webhook/IPN (Advanced) 🌐

**Best for:** Production systems, async processing

### How It Works

Set up a public-facing server endpoint that ipay calls when payment completes. This is server-to-server, no browser needed.

### Requirements

1. **Public server** with HTTPS
2. **Webhook endpoint** that ipay can call
3. **Configure callback URL** in ipay/Ooredoo merchant settings

### Setup

#### 1. Create Webhook Endpoint

```python
# webhook_server.py
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

# Secret key from ipay merchant dashboard
WEBHOOK_SECRET = "your_secret_key_here"

@app.route('/webhook/ipay', methods=['POST'])
def ipay_webhook():
    """
    Receives payment notifications from ipay
    """
    
    # Verify webhook signature (if ipay provides one)
    signature = request.headers.get('X-Signature')
    if signature:
        # Verify signature
        calculated = hmac.new(
            WEBHOOK_SECRET.encode(),
            request.data,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, calculated):
            return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse webhook data
    data = request.json
    
    order_id = data.get('orderId')
    status = data.get('status')
    transaction_id = data.get('transactionId')
    amount = data.get('amount')
    
    print(f"Payment webhook received:")
    print(f"  Order ID: {order_id}")
    print(f"  Status: {status}")
    print(f"  Transaction ID: {transaction_id}")
    print(f"  Amount: {amount}")
    
    # Update your database
    # db.update_payment(order_id, status, transaction_id)
    
    # Send notification
    # send_notification(user_id, f"Payment {status}")
    
    # Return success
    return jsonify({'received': True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### 2. Configure Callback URL

In your ipay/Ooredoo merchant settings, set:
```
Callback URL: https://your-server.com/webhook/ipay
```

#### 3. Handle Asynchronously

```python
# Your recharge script
result = recharger.recharge(phone, password, beneficiary, amount)

if result['status'] == 'success':
    payment_url = result['payment_url']
    order_id = extract_order_id(payment_url)  # Parse mdOrder parameter
    
    # Save to database as "pending"
    db.create_payment_record(
        order_id=order_id,
        payment_url=payment_url,
        status='pending',
        created_at=time.time()
    )
    
    # Send payment URL to user
    send_sms(user_phone, f"Complete payment: {payment_url}")
    
    # Webhook will update status when payment completes
```

### Pros & Cons

**Pros ✅**
- Production-ready
- Asynchronous (no browser needed)
- Reliable (server-to-server)
- Scales well

**Cons ❌**
- Requires public server with HTTPS
- Needs ipay merchant account configuration
- More complex setup
- May require ipay support to enable webhooks

---

## Complete Integration Example

### Combined Approach (Recommended)

Use **Solution 1** (monitoring) for immediate feedback + **Solution 3** (webhook) for reliability.

```python
#!/usr/bin/env python3
"""
Complete recharge with payment monitoring
"""

from ooredoo_creditcard import OoredooCreditCardRecharge
from payment_monitor import monitor_payment
import time

def complete_recharge_with_monitoring(phone, password, beneficiary, amount):
    """
    Full recharge flow with payment monitoring
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
        print(f"❌ Recharge creation failed: {result.get('message')}")
        return result
    
    payment_url = result['payment_url']
    print(f"\n✅ Payment URL obtained!")
    print(f"   {payment_url}\n")
    
    # Step 2: Monitor payment completion
    print("=" * 60)
    print("STEP 2: Monitoring Payment")
    print("=" * 60)
    
    payment_result = monitor_payment(payment_url, timeout_seconds=300)
    
    # Step 3: Handle result
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    
    if payment_result['status'] == 'success':
        print("✅ Payment completed successfully!")
        print(f"   Order ID: {payment_result.get('order_id', 'N/A')}")
        print(f"   Transaction ID: {payment_result.get('transaction_id', 'N/A')}")
        
        # TODO: Send confirmation
        # send_sms(beneficiary, f"Recharge of {amount} TND successful!")
        
    elif payment_result['status'] == 'failed':
        print("❌ Payment failed!")
        print(f"   Reason: {payment_result.get('message')}")
        
    elif payment_result['status'] == 'timeout':
        print("⏱️  Payment timeout!")
        print("   Please check payment status manually")
        
    print("=" * 60)
    
    return {
        'recharge': result,
        'payment': payment_result
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: python complete_recharge.py <phone> <password> <beneficiary> <amount>")
        sys.exit(1)
    
    phone = sys.argv[1]
    password = sys.argv[2]
    beneficiary = sys.argv[3]
    amount = int(sys.argv[4])
    
    result = complete_recharge_with_monitoring(phone, password, beneficiary, amount)
```

---

## 🎯 Recommendations

### For Your Use Case

Based on your requirements (webhook/signal when done, control redirect):

**Immediate Implementation (Today):**
- Use **Solution 1** (Monitor Redirect URL)
- Simple, works now, no server setup needed
- Good for testing and small-scale use

**Production Implementation (Later):**
- Set up **Solution 3** (Webhook/IPN)
- Contact ipay/Ooredoo support to enable webhooks
- More reliable for production

**Hybrid Approach (Best):**
- Use monitoring for immediate feedback
- Also log to database
- Add webhook when available
- Best of both worlds

### Next Steps

1. ✅ Test `payment_monitor.py` with a real payment
2. ✅ See what redirect URL parameters you get
3. 📞 Contact ipay/Ooredoo to ask about webhook/IPN support
4. 🔧 Build webhook endpoint when confirmed
5. 🚀 Deploy to production

---

## 📚 Files Created

- `payment_monitor.py` - Simple URL monitoring
- `payment_intercept.py` - JavaScript redirect interception  
- `PAYMENT_MONITORING.md` - This documentation

---

**Questions?** Test the scripts and let me know what redirect URL parameters you see after a real payment!
