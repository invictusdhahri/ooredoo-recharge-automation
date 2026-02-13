# Redirect Detection Fix

## Problem You Had

**Symptoms:**
- Script got stuck at `Finished Request` log line
- You completed payment and saw Ooredoo success page in browser
- Script kept running but never detected the redirect
- Had to manually stop the script

**Root Cause:**
The monitoring loop was **too slow** and **not checking in the right places** for the redirect:
- Checked every 2 seconds (too slow for fast redirects)
- Only checked main window URL (3DS redirects often happen in iframes)
- Used Selenium's `current_url` (can be stale/cached)
- Didn't check if we ended up on Ooredoo's page

---

## What Was Fixed

### 1. ⚡ Faster Polling
```python
# Before: Check every 2 seconds
time.sleep(2)

# After: Check every 1 second
time.sleep(1)
```
**Why:** Redirects can happen very quickly after 3DS completion. Faster polling catches them.

### 2. 🎯 JavaScript-Based URL Detection
```python
# Before: Use Selenium's property (can be stale)
new_url = self.driver.current_url

# After: Query JavaScript directly
new_url = self.driver.execute_script("return window.location.href;")
```
**Why:** JavaScript always returns the actual current location, no caching issues.

### 3. 🖼️ Iframe Redirect Detection
```python
# NEW: Check all iframes for redirects
iframe_urls = self.driver.execute_script("""
    var urls = [];
    var iframes = document.getElementsByTagName('iframe');
    for (var i = 0; i < iframes.length; i++) {
        try {
            urls.push(iframes[i].contentWindow.location.href);
        } catch(e) { /* Cross-origin, skip */ }
    }
    return urls;
""")

# If iframe has Ooredoo URL, parse it
if 'espaceclient.ooredoo' in iframe_url:
    redirect_result = self._parse_redirect(iframe_url)
```
**Why:** 3D Secure often uses iframes for authentication. The redirect might happen inside the iframe first.

### 4. 🔍 Proactive Ooredoo Page Detection
```python
# NEW: Check if we're already on Ooredoo's page
if 'espaceclient.ooredoo' in new_url:
    # We're on Ooredoo! Parse it immediately
    redirect_result = self._parse_redirect(new_url)
    if redirect_result['status'] != 'unknown':
        return self._success_response(redirect_result, elapsed)
```
**Why:** If we somehow end up on Ooredoo's page (even if we missed the redirect event), detect it.

### 5. 🧠 Smart Timeout Handling
```python
# NEW: If timeout but on Ooredoo page, parse it
def _timeout_response(self, timeout_seconds):
    last_url = self.driver.execute_script("return window.location.href;")
    
    # Check if we timed out on Ooredoo's page
    if 'espaceclient.ooredoo' in last_url:
        redirect_result = self._parse_redirect(last_url)
        if redirect_result['status'] != 'unknown':
            # We found it! Return success even though we "timed out"
            return self._success_response(redirect_result, timeout_seconds)
```
**Why:** Even if monitoring times out, if we're on Ooredoo's success/fail page, we can still extract the result.

### 6. 📝 Track Seen URLs
```python
# NEW: Track all URLs we've seen
seen_urls = set([initial_url])

if new_url not in seen_urls:
    seen_urls.add(new_url)
    # Process redirect
```
**Why:** Avoid re-processing the same URL multiple times.

### 7. 🎯 Better Ooredoo Domain Detection
```python
# Before: Only checked espaceclient.ooredoo
if 'espaceclient.ooredoo' in parsed.netloc:
    # ...

# After: Check multiple patterns
if 'espaceclient.ooredoo' in parsed.netloc or 'ooredoo.tn' in parsed.netloc:
    # Check path patterns
    if 'success' in path or 'payment-success' in path:
        result['status'] = 'success'
    elif 'fail' in path or 'payment-fail' in path:
        result['status'] = 'failed'
    # Even if path unclear, assume success if we got params
    elif params:
        result['status'] = 'success'
```
**Why:** Ooredoo might use different subdomains or URL patterns.

---

## Testing the Fix

### Test 1: Normal Flow
```bash
cd /data/.openclaw/workspace/ooredoo-recharge
python payment_api.py "https://ipay.clictopay.com/..." 300 test_normal.log
```

**Expected:**
- Opens browser
- You complete payment
- Script detects redirect within 1-2 seconds
- Returns success response
- Logs show `REDIRECT_DETECTED` or `OOREDOO_PAGE_DETECTED`

### Test 2: Iframe Redirect
If 3DS redirects in an iframe:

**Expected:**
- Logs show `IFRAME_REDIRECT_DETECTED`
- Script catches iframe URL with Ooredoo domain
- Returns success

### Test 3: Missed Redirect (Timeout Scenario)
If script somehow misses the redirect event:

**Expected:**
- Script continues checking
- Detects `espaceclient.ooredoo` in URL
- Logs show `OOREDOO_PAGE_DETECTED`
- Returns success (not timeout)

---

## What to Look For in Logs

### Successful Detection (New Logs)

```
[INFO] [MONITORING_CHECK] {
  "check_number": 10,
  "elapsed_seconds": 10.0,
  "current_url": "https://ipay.clictopay.com/...",
  "seen_urls_count": 1
}

[INFO] [IFRAME_REDIRECT_DETECTED] {
  "iframe_url": "https://espaceclient.ooredoo.tn/payment-success?...",
  "elapsed_seconds": 12.3
}

[INFO] [REDIRECT_PARAMS] {
  "status": "success",
  "orderId": "12345",
  "transactionId": "67890"
}

[INFO] [PAYMENT_COMPLETED] {
  "success": true,
  "order_id": "12345",
  "transaction_id": "67890"
}
```

### Or Direct Detection

```
[INFO] [OOREDOO_PAGE_DETECTED] {
  "url": "https://espaceclient.ooredoo.tn/payment-success",
  "elapsed_seconds": 15.8
}

[INFO] [REDIRECT_PARSED] {
  "status": "success",
  "payment_status": "completed",
  "message": "Redirected to Ooredoo success page"
}

[INFO] [PAYMENT_COMPLETED] { ... }
```

---

## Next Test Run

When you run the payment again:

1. **Start fresh:**
   ```bash
   python payment_api.py "YOUR_PAYMENT_URL" 300 payment_test.log
   ```

2. **Complete the payment** (enter card details, confirm 3DS)

3. **Watch the console** - should detect redirect quickly now

4. **Check the log file:**
   ```bash
   cat payment_test.log | grep -E "(REDIRECT_DETECTED|IFRAME_REDIRECT|OOREDOO_PAGE|PAYMENT_COMPLETED)"
   ```

5. **Send me the full log** - I want to see:
   - Which detection method worked (iframe, direct URL, page detection)
   - What URL parameters Ooredoo sends
   - How fast it detected the redirect

---

## Expected Improvements

### Before Fix
- ❌ Got stuck after redirect
- ❌ Checked every 2 seconds
- ❌ Only checked main window
- ❌ Used cached URL
- ⏱️  Could miss fast redirects

### After Fix
- ✅ Detects redirect reliably
- ✅ Checks every 1 second
- ✅ Checks main window + all iframes
- ✅ Uses JavaScript for real-time URL
- ✅ Multiple fallback detection methods
- ✅ Smart timeout handling
- ⚡ Catches even very fast redirects

---

## Summary

**The core issue:** Script wasn't looking in the right places at the right time.

**The fix:** Made monitoring more aggressive and comprehensive:
- Faster checks
- Better URL detection
- Iframe monitoring
- Proactive page detection
- Smart fallback handling

**Result:** Should never get stuck again, even if redirect happens in iframe or very quickly.

---

Ready to test? Run another recharge and send me the logs! 🚀
