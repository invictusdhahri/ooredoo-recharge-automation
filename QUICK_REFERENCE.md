# Ooredoo Recharge - Quick Reference

## Response Types at a Glance

### ✅ Success
```
Votre recharge a été effectuée avec succès
```
- **Color:** Green
- **Status:** Success
- **Action:** Recharge completed

---

### ❌ Invalid Code
```
Recharge non aboutie. Essayez de nouveau
```
- **Color:** Red/Pink
- **Status:** Error
- **Reason:** Invalid, expired, or already used code

---

### ⚠️ Wrong Length
```
Cette chaîne doit avoir exactement 14 caractères.
```
- **Color:** Red/Pink
- **Status:** Validation Error
- **Reason:** Code must be exactly 14 digits

---

## Detection Pattern

All responses use the same HTML element:
```html
<div role="alert">
  <span></span>
  [MESSAGE TEXT HERE]
</div>
```

**Differentiate by:**
1. Text content keywords
2. CSS class (success vs error)
3. Background color

## Python Detection

```python
def get_response_status(driver):
    alert = driver.find_element(By.CSS_SELECTOR, '[role="alert"]')
    text = alert.text.strip()
    
    # Success
    if 'succès' in text or 'effectuée' in text:
        return 'success'
    
    # Validation error
    if 'exactement 14 caractères' in text:
        return 'validation_error'
    
    # Invalid code
    if 'non aboutie' in text:
        return 'invalid_code'
    
    return 'unknown'
```

## Tested Codes

| Code | Length | Result |
|------|--------|--------|
| `1234567890123456` | 16 | ❌ Validation error (wrong length) |
| `98765432109876` | 14 | ❌ Invalid code |
| `00641977131038` | 14 | ✅ Success |

## Key Observations

1. **No Redirects:** All responses stay on `/recharge-card`
2. **CAPTCHA Refresh:** New CAPTCHA generated after each submit
3. **Form Persistence:** Code remains in field after submit
4. **Same Alert Element:** Success and errors use same `role="alert"` div
5. **Color Coding:** Green = success, Red/Pink = error
