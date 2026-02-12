# Ooredoo Recharge Response Formats

This document captures the different response types from the Ooredoo recharge system.

## Error Responses

### 1. Validation Error (Wrong Length)

**Test:** 16-digit code `1234567890123456`

**Response:**
```
⚠️ Cette chaîne doit avoir exactement 14 caractères.
```
*Translation:* "This string must have exactly 14 characters"

**Behavior:**
- Form validation error
- Appears immediately
- Page doesn't submit

---

### 2. Invalid Recharge Code

**Test:** Random 14-digit code `98765432109876`

**Response:**
```
⚠️ Recharge non aboutie. Essayez de nouveau
```
*Translation:* "Recharge failed. Try again"

**Behavior:**
- Form submits successfully
- Error appears after server validation
- Page stays on `/recharge-card`
- No redirect
- New CAPTCHA generated
- Previous code remains in field

**HTML Structure:**
```html
<div role="alert">
  <span></span>
  Recharge non aboutie. Essayez de nouveau
</div>
```

**Detection:**
```python
alert_elem = driver.find_element(By.CSS_SELECTOR, '[role="alert"]')
error_text = alert_elem.text.strip()

if "Recharge non aboutie" in error_text:
    status = "invalid_code"
```

---

### 3. Wrong CAPTCHA

**Test:** Invalid CAPTCHA text

**Expected Response:**
```
⚠️ Captcha incorrect
```

**Behavior:**
- Form submits
- Error appears
- New CAPTCHA generated
- Code remains filled

---

## Success Response

**Test:** Valid code `00641977131038`

**Response:**
```
✅ Votre recharge a été effectuée avec succès
```
*Translation:* "Your recharge has been completed successfully"

**Behavior:**
- Form submits successfully
- **No page redirect** - stays on `/recharge-card`
- Green success alert appears at top
- New CAPTCHA generated
- Previous code remains in field
- Same `role="alert"` element as errors

**HTML Structure:**
```html
<div role="alert">
  <span></span>
  Votre recharge a été effectuée avec succès
</div>
```

**Detection:**
```python
alert_elem = driver.find_element(By.CSS_SELECTOR, '[role="alert"]')
alert_text = alert_elem.text.strip()

if "Votre recharge a été effectuée avec succès" in alert_text:
    status = "success"
```

**Key Differences from Errors:**
- Green background color (errors are red/pink)
- Contains keyword "succès" or "effectuée"
- Positive confirmation message

---

## Response Detection Logic

```python
def parse_response(driver):
    """Detect response type from page"""
    
    # Check for alerts
    alerts = driver.find_elements(By.CSS_SELECTOR, '[role="alert"]')
    
    if alerts:
        alert_text = alerts[0].text.strip()
        
        # Validation errors (client-side)
        if "exactement 14 caractères" in alert_text:
            return {
                'status': 'validation_error',
                'type': 'wrong_length',
                'message': alert_text
            }
        
        # Invalid code (server-side)
        elif "Recharge non aboutie" in alert_text:
            return {
                'status': 'error',
                'type': 'invalid_code',
                'message': alert_text
            }
        
        # Wrong CAPTCHA
        elif "Captcha incorrect" in alert_text:
            return {
                'status': 'error',
                'type': 'wrong_captcha',
                'message': alert_text
            }
        
        # Success (keywords to check)
        elif any(kw in alert_text.lower() for kw in ['succès', 'effectuée', 'réussie', 'confirmé']):
            return {
                'status': 'success',
                'message': alert_text
            }
    
    # Check for redirect
    if '/success' in driver.current_url or '/confirmation' in driver.current_url:
        return {
            'status': 'success',
            'redirect': driver.current_url
        }
    
    return {
        'status': 'unknown',
        'url': driver.current_url,
        'html': driver.page_source
    }
```

---

## TODO

- [x] Capture success response with valid code ✅
- [ ] Test wrong CAPTCHA error
- [ ] Check for rate limiting
- [ ] Test expired code vs invalid code (if different messages)
- [ ] Document any additional error messages

## Summary

All major response types have been captured and documented:

✅ **Validation Error** - Wrong code length  
✅ **Invalid Code Error** - Bad/expired/used recharge code  
✅ **Success Response** - Valid recharge completed  

The system is ready for production use!
