# Quick Start - Ooredoo Payment API

## 🎯 What We Built

✅ **Comprehensive logging** - Every event during payment is recorded  
✅ **API response format** - Clean JSON instead of Ooredoo redirect pages  
✅ **Payment detection explained** - You'll see exactly how we know success/failure

## 🚀 Usage

### 1. Simple Command Line

```bash
python recharge_api.py 27865121 "password" 27865121 20
```

**What happens:**
1. Creates recharge → gets ICPay URL
2. Opens browser for you to enter card details
3. Monitors for payment completion
4. Returns JSON response
5. Saves detailed logs to `recharge_api.log`

### 2. As Python Module

```python
from recharge_api import api_recharge

result = api_recharge(
    phone='27865121',
    password='mypassword',
    beneficiary='27865121',
    amount=20
)

if result['success']:
    print("Payment successful!")
    print(f"Transaction ID: {result['payment']['data']['transaction_id']}")
else:
    print(f"Failed: {result['message']}")
```

### 3. As REST API

```bash
# Start the server
python api_server_example.py

# Make request
curl -X POST http://localhost:5000/api/v1/recharge \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "27865121",
    "password": "mypassword",
    "beneficiary": "27865121",
    "amount": 20
  }'
```

## 📊 How Payment Success is Detected

### Method 1: URL Parameters (Primary) ✅

When payment completes, ICPay redirects to:
```
https://espaceclient.ooredoo.tn/payment-success?status=success&orderId=xxx&transactionId=yyy
```

We parse these parameters:
- `status=success` → Payment successful
- `status=failed` → Payment failed
- `orderId` → Order ID
- `transactionId` → Transaction ID

### Method 2: Redirect Path (Backup) ✅

Check the redirect URL:
- `/payment-success` → Success
- `/payment-fail` → Failure
- `/payment-error` → Error

### Method 3: Page Content (Fallback) ⚠️

Search page HTML for:
- Success: "payment successful", "paiement réussi"
- Failure: "payment failed", "paiement échoué"

## 📝 Understanding the Logs

Open `recharge_api.log` and you'll see:

```json
{
  "timestamp": "2025-02-13T16:30:00",
  "event_type": "PAYMENT_INITIATED",
  "data": {"payment_url": "https://ipay..."}
}

{
  "event_type": "REDIRECT_DETECTED",
  "data": {
    "to_url": "https://espaceclient.ooredoo.tn/payment-success?status=success",
    "elapsed_seconds": 45.2
  }
}

{
  "event_type": "REDIRECT_PARAMS",
  "data": {
    "status": "success",
    "orderId": "12345",
    "transactionId": "67890"
  }
}

{
  "event_type": "PAYMENT_COMPLETED",
  "data": {
    "success": true,
    "order_id": "12345",
    "transaction_id": "67890"
  }
}
```

## 📤 API Response Format

### Success
```json
{
  "success": true,
  "message": "Recharge completed successfully",
  "stage": "completed",
  "payment": {
    "status": "success",
    "payment_status": "completed",
    "data": {
      "order_id": "12345",
      "transaction_id": "67890",
      "amount": "20",
      "elapsed_seconds": 45.2,
      "detection_method": "redirect_url"
    }
  }
}
```

### Failure
```json
{
  "success": false,
  "message": "Payment failed",
  "stage": "payment_failed",
  "payment": {
    "status": "failed",
    "payment_status": "failed",
    "message": "Payment declined"
  }
}
```

## 🔍 Next Steps

### 1. Test It

```bash
# Run a real recharge
python recharge_api.py <phone> <password> <beneficiary> 20

# Check the logs
cat recharge_api.log | grep "event_type"
```

### 2. Send Me the Logs

After a **successful** payment, send me:
```bash
cat recharge_api.log
```

I'll show you:
- What exact URL parameters Ooredoo sends
- Which detection method worked best
- How to optimize for your use case

### 3. Integrate

Choose your integration:
- **CLI**: Use `python recharge_api.py ...`
- **Python Module**: Import and use `api_recharge()`
- **REST API**: Run `api_server_example.py` and make HTTP requests

## 📚 Files

- `payment_api.py` - Payment monitoring with logging
- `recharge_api.py` - Complete recharge flow
- `api_server_example.py` - Flask REST API example
- `API_USAGE.md` - Full documentation
- `QUICK_START_API.md` - This file

## ❓ Questions?

- How do I avoid showing Ooredoo's page? → See `API_USAGE.md` section "Avoiding Ooredoo Redirect Pages"
- What if timeout happens? → Response includes `status: "timeout"` and `last_url`
- How to get transaction ID? → In response: `payment.data.transaction_id`
- Where are logs saved? → Default: `recharge_api.log` (customizable)

---

**Ready to test?**
```bash
python recharge_api.py <phone> <password> <beneficiary> 20
```
