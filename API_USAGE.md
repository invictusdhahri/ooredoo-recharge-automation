# Ooredoo Recharge API - Complete Guide

## 🎯 What You Asked For

You wanted:
1. ✅ **Comprehensive logging** - Record everything during payment flow
2. ✅ **API response format** - Return structured JSON instead of Ooredoo redirect pages
3. ✅ **Understand payment detection** - See exactly how we know payment succeeded/failed

## 📦 New Files Created

### `payment_api.py`
Enhanced payment monitoring with **detailed logging**
- Logs every event (redirect, page change, status detection)
- Records all URL parameters
- Captures page content analysis
- Returns structured API response

### `recharge_api.py`
Complete recharge flow as a single API call
- Creates recharge + monitors payment
- Returns clean JSON response
- Combines all logs in one place

---

## 🚀 Quick Start

### Basic Usage

```bash
# Complete recharge with API response
python recharge_api.py 27865121 "password" 27865121 20
```

This will:
1. Create the recharge
2. Open payment page for user to complete
3. Monitor for completion
4. Return JSON API response
5. Save detailed logs to `recharge_api.log`

### With Custom Settings

```bash
# Custom timeout and log file
python recharge_api.py 27865121 "password" 27865121 20 600 custom.log
```

---

## 📊 How Payment Success is Detected

The system uses **multiple detection methods** (ranked by reliability):

### Method 1: Redirect URL Parameters ✅ (Most Reliable)

When ICPay/ClicToPay completes payment, it redirects to:
```
https://espaceclient.ooredoo.tn/payment-success?orderId=xxx&status=success&transactionId=yyy
```

We check for these parameters:
- `status` → "success", "approved", "completed", "ok"
- `paymentStatus` → Similar values
- `responseCode` → "00" or "0" (success codes)

**Logged as:**
```json
{
  "event_type": "REDIRECT_PARAMS",
  "data": {
    "domain": "espaceclient.ooredoo.tn",
    "path": "/payment-success",
    "params": {
      "status": "success",
      "orderId": "12345",
      "transactionId": "67890"
    }
  }
}
```

### Method 2: Redirect Domain/Path ✅ (Reliable)

Check if redirected to Ooredoo's success/fail pages:
- `espaceclient.ooredoo.tn/payment-success` → Success
- `espaceclient.ooredoo.tn/payment-fail` → Failure
- `espaceclient.ooredoo.tn/payment-error` → Error

**Logged as:**
```json
{
  "event_type": "REDIRECT_DETECTED",
  "data": {
    "to_url": "https://espaceclient.ooredoo.tn/payment-success",
    "elapsed_seconds": 45.2
  }
}
```

### Method 3: Page Content Analysis ⚠️ (Fallback)

Search page HTML for success/failure phrases:
- Success: "payment successful", "paiement réussi", "opération effectuée"
- Failure: "payment failed", "paiement échoué", "transaction refusée"

**Logged as:**
```json
{
  "event_type": "SUCCESS_MESSAGE_DETECTED",
  "data": {
    "phrase": "payment successful",
    "url": "https://..."
  }
}
```

---

## 🔍 Understanding the Logs

### Log Structure

Every event is logged with:
- **Timestamp** - When it happened
- **Event type** - What happened
- **Data** - Details about the event

### Key Events to Look For

#### 1. Payment Initiated
```json
{
  "timestamp": "2025-02-13T16:30:00",
  "event_type": "PAYMENT_INITIATED",
  "data": {
    "payment_url": "https://ipay.clictopay.com/...",
    "timeout_seconds": 300
  }
}
```

#### 2. Browser Setup
```json
{
  "event_type": "BROWSER_SETUP",
  "data": {"status": "success"}
}
```

#### 3. Page Load
```json
{
  "event_type": "INITIAL_PAGE_LOAD",
  "data": {
    "url": "https://ipay.clictopay.com/...",
    "title": "ClicToPay Payment",
    "page_source_length": 12543
  }
}
```

#### 4. Monitoring Checks (every 30s)
```json
{
  "event_type": "MONITORING_CHECK",
  "data": {
    "check_number": 15,
    "elapsed_seconds": 30.0,
    "current_url": "https://ipay.clictopay.com/..."
  }
}
```

#### 5. Redirect Detected 🎯
```json
{
  "event_type": "REDIRECT_DETECTED",
  "data": {
    "from_url": "https://ipay.clictopay.com/...",
    "to_url": "https://espaceclient.ooredoo.tn/payment-success?...",
    "elapsed_seconds": 45.2
  }
}
```

#### 6. Redirect Parameters Parsed 🎯
```json
{
  "event_type": "REDIRECT_PARAMS",
  "data": {
    "domain": "espaceclient.ooredoo.tn",
    "path": "/payment-success",
    "params": {
      "status": "success",
      "orderId": "12345",
      "transactionId": "67890"
    }
  }
}
```

#### 7. Status Detected 🎯
```json
{
  "event_type": "STATUS_PARAM_FOUND",
  "data": {
    "key": "status",
    "value": "success"
  }
}
```

#### 8. Payment Completed ✅
```json
{
  "event_type": "PAYMENT_COMPLETED",
  "data": {
    "success": true,
    "status": "success",
    "payment_status": "completed",
    "order_id": "12345",
    "transaction_id": "67890",
    "elapsed_seconds": 45.2
  }
}
```

---

## 📤 API Response Format

### Success Response

```json
{
  "request": {
    "phone": "27865121",
    "beneficiary": "27865121",
    "amount": 20,
    "timestamp": "2025-02-13T16:30:00"
  },
  "recharge": {
    "status": "success",
    "message": "Recharge created successfully",
    "payment_url": "https://ipay.clictopay.com/..."
  },
  "payment": {
    "success": true,
    "status": "success",
    "payment_status": "completed",
    "message": "Payment completed",
    "data": {
      "order_id": "12345",
      "transaction_id": "67890",
      "amount": "20",
      "redirect_url": "https://espaceclient.ooredoo.tn/payment-success?...",
      "detection_method": "redirect_url",
      "elapsed_seconds": 45.2
    },
    "timestamp": "2025-02-13T16:30:45",
    "log_summary": {
      "total_events": 12,
      "events": [...]
    }
  },
  "success": true,
  "message": "Recharge completed successfully",
  "stage": "completed",
  "completed_at": "2025-02-13T16:30:48"
}
```

### Failure Response

```json
{
  "request": {...},
  "recharge": {...},
  "payment": {
    "success": false,
    "status": "failed",
    "payment_status": "failed",
    "message": "Payment failed: declined",
    "data": {
      "redirect_url": "https://espaceclient.ooredoo.tn/payment-fail?...",
      "detection_method": "redirect_url",
      "elapsed_seconds": 38.1
    },
    "log_summary": {...}
  },
  "success": false,
  "message": "Payment failed",
  "stage": "payment_failed",
  "completed_at": "2025-02-13T16:31:05"
}
```

### Timeout Response

```json
{
  "request": {...},
  "recharge": {...},
  "payment": {
    "success": false,
    "status": "timeout",
    "payment_status": "pending",
    "message": "Payment monitoring timed out after 300 seconds",
    "data": {
      "timeout_seconds": 300,
      "last_url": "https://ipay.clictopay.com/..."
    },
    "log_summary": {...}
  },
  "success": false,
  "message": "Payment monitoring timed out",
  "stage": "payment_timeout",
  "completed_at": "2025-02-13T16:35:00"
}
```

---

## 🔧 Integration Examples

### As a Python Module

```python
from recharge_api import api_recharge

# Execute recharge
result = api_recharge(
    phone='27865121',
    password='mypassword',
    beneficiary='27865121',
    amount=20,
    timeout_seconds=300,
    log_file='recharge.log'
)

# Check result
if result['success']:
    print("✅ Recharge successful!")
    
    # Get transaction details
    tx_id = result['payment']['data']['transaction_id']
    order_id = result['payment']['data']['order_id']
    
    # Your custom logic here
    # - Update database
    # - Send notification
    # - Trigger webhook
    
else:
    print(f"❌ Failed: {result['message']}")
    print(f"   Stage: {result['stage']}")
```

### As Flask/FastAPI Endpoint

```python
from flask import Flask, request, jsonify
from recharge_api import api_recharge

app = Flask(__name__)

@app.route('/api/recharge', methods=['POST'])
def recharge_endpoint():
    """
    POST /api/recharge
    Body: {
        "phone": "27865121",
        "password": "mypass",
        "beneficiary": "27865121",
        "amount": 20
    }
    """
    data = request.json
    
    result = api_recharge(
        phone=data['phone'],
        password=data['password'],
        beneficiary=data['beneficiary'],
        amount=data['amount'],
        timeout_seconds=300,
        log_file=f"logs/{data['phone']}.log"
    )
    
    # Return clean API response (without full log summary)
    response = {
        'success': result['success'],
        'message': result['message'],
        'stage': result.get('stage'),
        'payment': {
            'status': result['payment']['status'],
            'order_id': result['payment'].get('data', {}).get('order_id'),
            'transaction_id': result['payment'].get('data', {}).get('transaction_id')
        }
    }
    
    return jsonify(response), 200 if result['success'] else 400

if __name__ == '__main__':
    app.run(port=5000)
```

### Webhook After Payment

```python
from recharge_api import api_recharge
import requests

result = api_recharge(...)

if result['success']:
    # Send webhook to your backend
    requests.post('https://your-api.com/webhook/payment', json={
        'event': 'payment.completed',
        'order_id': result['payment']['data']['order_id'],
        'transaction_id': result['payment']['data']['transaction_id'],
        'amount': result['request']['amount'],
        'beneficiary': result['request']['beneficiary'],
        'timestamp': result['completed_at']
    })
```

---

## 🎓 What You Learn From the Logs

### 1. Redirect Flow

Send the logs to yourself and you'll see:
```
PAYMENT_INITIATED → BROWSER_SETUP → INITIAL_PAGE_LOAD
   ↓
[User enters card details - you see MONITORING_CHECK events every 30s]
   ↓
REDIRECT_DETECTED → REDIRECT_PARAMS → STATUS_PARAM_FOUND
   ↓
PAYMENT_COMPLETED
```

### 2. Success Detection Logic

You'll understand:
- **When** the redirect happens (elapsed_seconds)
- **Where** it redirects to (domain, path)
- **What parameters** are sent (status, orderId, transactionId)
- **Which method** detected success (redirect_url vs page_content)

### 3. Failure Scenarios

The logs show you:
- Payment declined → `status=declined` in redirect params
- User cancelled → Redirect to `/payment-cancel`
- Network error → Exception in MONITORING_ERROR event
- Timeout → No redirect within timeout period

---

## 🔄 Avoiding Ooredoo Redirect Pages

### Current Behavior

When payment completes, ICPay redirects to:
```
https://espaceclient.ooredoo.tn/payment-success
```

This shows Ooredoo's success page with "Back to merchant" button.

### What We Do Now

1. **Detect the redirect** before page fully loads
2. **Parse the URL parameters** to get payment status
3. **Return API response** with that info
4. Browser still shows Ooredoo page briefly, then closes

### Future: Intercept Before Redirect

To **completely avoid** Ooredoo's page, use JavaScript injection:

```python
# payment_intercept.py (already created in earlier work)
from payment_intercept import intercept_payment_redirect

result = intercept_payment_redirect(payment_url)
# This prevents the redirect from happening
# Shows custom page instead
```

This requires:
- JavaScript injection into the payment page
- Intercepting `window.location` changes
- More fragile (ICPay might block it)

**Recommendation:** Use current approach (parse redirect) for production reliability.

---

## 📝 Next Steps

### 1. Test the API

```bash
# Run a real recharge
python recharge_api.py <phone> <password> <beneficiary> 20

# Check the logs
cat recharge_api.log
```

### 2. Send Me the Logs

After running a **successful** and a **failed** payment:
```bash
# Copy the logs
cat recharge_api.log > success_payment.log
# Run another test that fails
cat recharge_api.log > failed_payment.log
```

Send me both logs and I'll show you exactly:
- What URL parameters Ooredoo sends
- Which detection method worked
- How to optimize the detection logic

### 3. Build Your API

Use `recharge_api.py` as a module in your Flask/FastAPI backend:
- Create REST endpoint
- Handle authentication
- Store results in database
- Send notifications

### 4. Avoid Redirect Page (Optional)

If you want to show your own success page instead of Ooredoo's:
- Use `payment_intercept.py`
- Test if ICPay allows JavaScript injection
- Fallback to current method if blocked

---

## 🎯 Summary

**What changed:**
- ✅ Every event is logged with details
- ✅ API response format (JSON, not web redirect)
- ✅ Clear detection methods explained

**How payment success is detected:**
1. Redirect URL parameters (`status=success`)
2. Redirect domain/path (`payment-success`)
3. Page content analysis (fallback)

**How to use it:**
```bash
python recharge_api.py <phone> <password> <beneficiary> <amount>
```

**What you get:**
- Console output with progress
- JSON API response
- Detailed logs in file
- Clear success/failure status

**Next:** Test it, send me the logs, and we'll refine based on real Ooredoo responses!
