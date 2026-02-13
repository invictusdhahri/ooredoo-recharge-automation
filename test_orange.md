# Orange Test - Verifying GraphQL Error

## Test Setup

**Phone:** 53028939  
**Code:** 1234567890123 (dummy)  
**Math CAPTCHA:** 1 + 7 = 8

## Expected Error Response

```json
{
  "errors": [
    {
      "message": "errors.topupWithScratch.invalidScratch",
      "extensions": {
        "code": "BAD_USER_INPUT"
      }
    }
  ],
  "data": null
}
```

## Status
Form filled, need to submit to capture actual GraphQL response.
