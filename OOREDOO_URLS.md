# Ooredoo Payment URLs - Actual Response Data

## Real Transaction URLs (from your test)

### Payment Failed
```
https://espaceclient.ooredoo.tn/public/pay-fail?orderId=3f1f7fbd-1bef-4715-9d32-770e02d3e5bd
```

**URL Structure:**
- Domain: `espaceclient.ooredoo.tn`
- Path: `/public/pay-fail`
- Parameters:
  - `orderId`: `3f1f7fbd-1bef-4715-9d32-770e02d3e5bd`

**Detected Status:**
```json
{
  "status": "failed",
  "payment_status": "failed",
  "message": "Redirected to Ooredoo failure page",
  "order_id": "3f1f7fbd-1bef-4715-9d32-770e02d3e5bd"
}
```

### Payment Success (Expected)
Based on the fail URL pattern, success should be:
```
https://espaceclient.ooredoo.tn/public/pay-success?orderId=xxx&transactionId=yyy
```

or

```
https://espaceclient.ooredoo.tn/public/payment-success?orderId=xxx&transactionId=yyy
```

**Expected Parameters:**
- `orderId` - The order/recharge ID
- `transactionId` - The payment transaction ID (probably only on success)
- Possibly: `status`, `amount`, `responseCode`

---

## Detection Logic

Our script detects payment status by checking:

### 1. URL Path
```python
if '/pay-fail' in path or '/payment-fail' in path:
    status = 'failed'
    
elif '/pay-success' in path or '/payment-success' in path:
    status = 'success'
```

### 2. URL Domain
```python
if 'espaceclient.ooredoo.tn' in domain:
    # We're on Ooredoo's result page
    # Parse path and parameters
```

### 3. URL Parameters
```python
params = parse_qs(url.query)

if 'status' in params:
    if params['status'] == 'success':
        status = 'success'
    elif params['status'] == 'failed':
        status = 'failed'

if 'orderId' in params:
    order_id = params['orderId'][0]
    
if 'transactionId' in params:
    transaction_id = params['transactionId'][0]
```

---

## API Response Format

### Success Response (After Successful Payment)
```json
{
  "success": true,
  "status": "success",
  "payment_status": "completed",
  "message": "Redirected to Ooredoo success page",
  "data": {
    "order_id": "3f1f7fbd-1bef-4715-9d32-770e02d3e5bd",
    "transaction_id": "abc123xyz",
    "amount": null,
    "redirect_url": "https://espaceclient.ooredoo.tn/public/pay-success?orderId=...",
    "detection_method": "redirect_url",
    "elapsed_seconds": 45.2
  },
  "timestamp": "2026-02-13T16:42:38",
  "log_summary": {
    "total_events": 15,
    "events": [...]
  }
}
```

### Failure Response (Your Test)
```json
{
  "success": false,
  "status": "failed",
  "payment_status": "failed",
  "message": "Redirected to Ooredoo failure page",
  "data": {
    "order_id": "3f1f7fbd-1bef-4715-9d32-770e02d3e5bd",
    "transaction_id": null,
    "amount": null,
    "redirect_url": "https://espaceclient.ooredoo.tn/public/pay-fail?orderId=3f1f7fbd-1bef-4715-9d32-770e02d3e5bd",
    "detection_method": "redirect_url",
    "elapsed_seconds": 208.0
  },
  "timestamp": "2026-02-13T16:42:38",
  "log_summary": {
    "total_events": 12,
    "events": [...]
  }
}
```

### Timeout Response (No Redirect Detected)
```json
{
  "success": false,
  "status": "timeout",
  "payment_status": "pending",
  "message": "Payment monitoring timed out after 300 seconds",
  "data": {
    "timeout_seconds": 300,
    "last_url": "https://ipay.clictopay.com/..."
  },
  "timestamp": "2026-02-13T16:47:38",
  "log_summary": {
    "total_events": 8,
    "events": [...]
  }
}
```

---

## Integration Example

### Check Payment Result
```python
from payment_api import monitor_payment_api

# After creating recharge
payment_url = "https://ipay.clictopay.com/..."
result = monitor_payment_api(payment_url)

if result['success']:
    print("✅ Payment successful!")
    order_id = result['data']['order_id']
    transaction_id = result['data']['transaction_id']
    
    # Update database
    # db.update_payment(order_id, 'completed', transaction_id)
    
    # Send notification
    # send_sms(user, f"Recharge completed. Transaction: {transaction_id}")
    
else:
    if result['status'] == 'failed':
        print("❌ Payment failed")
        # Handle failure
        
    elif result['status'] == 'timeout':
        print("⏱️ Timeout - check manually")
        # Handle timeout
```

### As REST API Response
```python
@app.route('/api/recharge', methods=['POST'])
def recharge():
    # ... create recharge, get payment URL ...
    
    result = monitor_payment_api(payment_url)
    
    # Clean response (remove log_summary for API)
    api_response = {
        'success': result['success'],
        'status': result['status'],
        'message': result['message'],
        'data': {
            'order_id': result['data'].get('order_id'),
            'transaction_id': result['data'].get('transaction_id'),
            'elapsed_seconds': result['data'].get('elapsed_seconds')
        }
    }
    
    return jsonify(api_response), 200 if result['success'] else 400
```

---

## Next Test: Successful Payment

We need to test with a **successful payment** to see:
1. What URL Ooredoo uses for success (`/pay-success` or `/payment-success`?)
2. What parameters are included (`transactionId`, `status`, others?)
3. How fast the redirect happens
4. Whether `transactionId` is provided

**To test:**
```bash
# Use real credentials and complete payment successfully
python payment_api.py "PAYMENT_URL" 300 success_test.log

# Check the logs
cat success_test.log | grep -E "(OOREDOO_PAGE|REDIRECT_PARAMS|PAYMENT_COMPLETED)"
```

---

## Summary

**What we know:**
- ✅ Failure URL: `espaceclient.ooredoo.tn/public/pay-fail?orderId=xxx`
- ✅ Detection: Works via URL path matching
- ✅ Response format: Clean JSON with order_id
- ✅ Timing: ~208 seconds (including 3DS completion)

**What we need to confirm:**
- ❓ Success URL format
- ❓ Transaction ID parameter name
- ❓ Any additional parameters on success
- ❓ Response speed on successful payment

**Once we have a successful payment log, we'll know:**
- Exact success URL pattern
- All available parameters
- Complete API response format
- Any edge cases to handle
