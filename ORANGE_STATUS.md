# Orange Tunisia - Current Status

## ✅ What We've Documented

### Error Response (Invalid Code)
```
✕ Le numéro de carte de recharge saisi n'est pas valide.
```

**GraphQL Error:**
```json
{
  "errors": [{
    "message": "errors.topupWithScratch.invalidScratch",
    "extensions": {"code": "BAD_USER_INPUT"}
  }],
  "data": null
}
```

### Form Structure
- **Phone:** `53 028 939`
- **Confirmation:** `53 028 939`
- **Code:** 14 digits exactly
- **Math CAPTCHA:** Simple equations (2+1, 10-4, etc.)

---

## ⏳ What's Pending

### Success Response (Need Proper Automation)

**Valid Code Provided:** `69036492639014`

**Challenge:** The form uses reactive JavaScript validation (likely Vue.js/React) that makes browser automation difficult. Client-side validation blocks submission when fields aren't properly triggered.

**Error Encountered:**
```
⚠ La vérification de la captcha a échoué, veuillez réessayer.
```
(CAPTCHA verification failed, please try again)

---

## 🔧 Solution: Build Proper Selenium Script

The OpenClaw browser tool has limitations with reactive forms. We need a dedicated Selenium script that can:

1. ✅ Properly interact with form fields
2. ✅ Trigger all necessary events (focus, input, change, blur)
3. ✅ Handle dynamic CAPTCHA changes
4. ✅ Wait for validation states
5. ✅ Capture network requests (GraphQL)

### Selenium Script Requirements

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def recharge_orange(phone, code):
    driver = webdriver.Chrome()
    
    try:
        # Navigate
        driver.get('https://www.orange.tn/recharge-par-carte-de-recharge')
        time.sleep(2)
        
        # Fill phone
        phone_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="55 555"]'))
        )
        phone_input.clear()
        phone_input.send_keys(phone)
        
        # Fill confirmation
        conf_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        if len(conf_inputs) >= 2:
            conf_inputs[1].clear()
            conf_inputs[1].send_keys(phone)
        
        # Fill code
        code_input = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')[2]
        code_input.clear()
        code_input.send_keys(code)
        
        # Get math equation
        captcha_img = driver.find_element(By.CSS_SELECTOR, 'img[alt*="captcha"], img[src*="captcha"]')
        # OR parse from visible text near the image
        
        # Solve math (simple eval for CAPTCHA math)
        equation = "2 + 1"  # Extract from page
        answer = eval(equation)
        
        # Fill CAPTCHA
        num_input = driver.find_element(By.CSS_SELECTOR, 'input[type="number"]')
        num_input.clear()
        num_input.send_keys(str(answer))
        
        # Submit
        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Recharger')]"))
        )
        submit_btn.click()
        
        # Wait for response
        time.sleep(5)
        
        # Check for success/error
        page_source = driver.page_source
        
        if "Recharge effectuée avec succès" in page_source:
            return {'status': 'success'}
        elif "n'est pas valide" in page_source:
            return {'status': 'invalid_code'}
        
        return {'status': 'unknown', 'html': page_source}
        
    finally:
        driver.quit()
```

---

## 📋 Next Steps

1. **Option A:** Build dedicated Selenium script (recommended)
   - Full control over form interaction
   - Can capture network requests
   - Can handle all validation states
   
2. **Option B:** Manual test with browser DevTools
   - Open page in Chrome with DevTools (Network tab)
   - Fill form manually with valid code
   - Capture the GraphQL request/response
   - Document success response format

3. **Option C:** Use requests library (if we can reverse-engineer the API)
   - Analyze network traffic
   - Build direct GraphQL client
   - Bypass form entirely

---

## 🎯 Priority

**High Priority:** We need the success response format to complete Orange automation.

**Recommended Approach:** Manual test with browser DevTools (fastest way to get the data)

Steps:
1. Open https://www.orange.tn/recharge-par-carte-de-recharge in Chrome
2. Open DevTools → Network tab
3. Filter by "graphql" or "fetch/XHR"
4. Fill form with code `69036492639014`
5. Submit
6. Copy the GraphQL request/response
7. Document success format

---

## Summary

✅ **Error format:** Documented  
✅ **Form structure:** Analyzed  
✅ **Math CAPTCHA:** Understood  
⏳ **Success format:** Need proper test  
⏳ **Automation script:** Ready to build once we have success response
