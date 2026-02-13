# Orange Tunisia - Test Results

## Error Message (from your screenshot)

**✕ Le numéro de carte de recharge saisi n'est pas valide.**  
*Translation:* "The recharge card number entered is not valid."

---

## Test Attempt

**Test Data:**
- Phone: `53028939`
- Confirmation: `53028939`
- Code: `98765432109876` (14 random digits)
- Math CAPTCHA: `1 + 4 = 5`

**Issue:** Form validation in browser prevented backend submission. Need to properly fill fields using Selenium for accurate testing.

---

## Expected Flow

### 1. Client-Side Validation
Before backend submission, the form validates:
- ✅ Phone number matches confirmation
- ✅ Code is exactly 14 characters
- ✅ CAPTCHA is filled

### 2. Backend GraphQL Request

**If validation passes, sends to GraphQL endpoint:**

```
POST https://www.orange.tn/graphql (or similar endpoint)
```

**Expected Payload (GraphQL mutation):**
```graphql
mutation {
  topupWithScratchCard(
    phoneNumber: "53028939",
    scratchCode: "98765432109876",
    captchaAnswer: "5"
  ) {
    success
    message
    balance
  }
}
```

### 3. Backend Response - Invalid Code

**GraphQL Error Response:**
```json
{
  "errors": [
    {
      "message": "errors.topupWithScratch.invalidScratch",
      "locations": [{"line": 2, "column": 3}],
      "path": ["topupWithScratchCard"],
      "extensions": {
        "code": "BAD_USER_INPUT",
        "exception": {
          "stacktrace": [
            "UserInputError: errors.topupWithScratch.invalidScratch",
            " at /opt/app/dist/index.js:1:916637",
            ...
          ]
        }
      }
    }
  ],
  "data": null
}
```

**UI Error Message:**
```
✕ Le numéro de carte de recharge saisi n'est pas valide.
```

---

## Success Response (Expected)

**GraphQL Success Response:**
```json
{
  "data": {
    "topupWithScratchCard": {
      "success": true,
      "message": "Recharge effectuée avec succès",
      "balance": "XX.XXX DT"
    }
  },
  "errors": null
}
```

**UI Success Message:**
```
✓ Recharge effectuée avec succès
```

---

## Detection Logic

```python
def parse_orange_response(response_json):
    """Parse Orange GraphQL response"""
    
    # Check for GraphQL errors
    if response_json.get('errors'):
        error = response_json['errors'][0]
        error_message = error.get('message', '')
        
        if 'invalidScratch' in error_message:
            return {
                'status': 'invalid_code',
                'message': 'Le numéro de carte de recharge saisi n\'est pas valide.'
            }
        
        return {
            'status': 'error',
            'message': error_message
        }
    
    # Check for success
    data = response_json.get('data', {})
    if data.get('topupWithScratchCard', {}).get('success'):
        return {
            'status': 'success',
            'message': 'Recharge effectuée avec succès',
            'balance': data['topupWithScratchCard'].get('balance')
        }
    
    return {'status': 'unknown', 'raw': response_json}
```

---

## Math CAPTCHA Examples

| Equation | Answer |
|----------|--------|
| 1 + 4 | 5 |
| 10 + 7 | 17 |
| 5 + 3 | 8 |
| 20 - 5 | 15 |
| 6 * 2 | 12 |

**Solver:**
```python
def solve_math_captcha(equation):
    """Parse and solve simple math equations"""
    # Remove whitespace and equals sign
    clean = equation.replace('=', '').replace('?', '').strip()
    # Safely evaluate (only contains numbers and operators)
    return str(eval(clean))
```

---

## Status

- ✅ Form structure analyzed
- ✅ Error message documented (from screenshot)
- ✅ GraphQL error format documented (from your previous test)
- ⏳ **Need Selenium test** to properly capture backend response
- ⏳ **Need valid code** to capture success response

---

## Next Steps

1. Build proper Selenium script to fill form correctly
2. Test with random 14-digit code → Capture GraphQL error
3. Test with valid code (when provided) → Capture GraphQL success
4. Build full automation tool
