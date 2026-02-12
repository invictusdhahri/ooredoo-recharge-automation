# Ooredoo Recharge Automation

Automated recharge system for Ooredoo Tunisia with AI CAPTCHA solving.

## Features

- ✅ Automatic login to espaceclient.ooredoo.tn
- ✅ AI-powered CAPTCHA solving (OpenAI Vision API)
- ✅ Form submission with recharge codes
- ✅ Response parsing (success/error detection)
- ✅ Multiple implementation methods (Selenium, Requests)

## Files

- **`recharge.py`** - Full Selenium automation (recommended for testing)
- **`recharge_requests.py`** - Faster requests-only version (TODO)
- **`recharge_openclaw.py`** - OpenClaw browser tool integration

## Requirements

### Python Dependencies

```bash
pip install selenium requests beautifulsoup4
```

### Chrome Driver

Selenium version requires ChromeDriver. Install via:

```bash
# Ubuntu/Debian
apt install chromium-chromedriver

# macOS
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

### API Keys

For AI CAPTCHA solving, you need an OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
```

## Usage

### Method 1: Selenium (Recommended)

```bash
python3 recharge.py <14-DIGIT-RECHARGE-CODE>
```

**Example:**
```bash
python3 recharge.py 12345678901234
```

### Method 2: Headless Mode

```python
from recharge import OoredooRecharge

bot = OoredooRecharge(headless=True)
bot.login()
bot.navigate_to_recharge()
response = bot.submit_recharge("27865121", "12345678901234")
print(response)
bot.close()
```

### Method 3: Manual CAPTCHA

If you don't have OpenAI API key, solve CAPTCHA manually:

```python
bot = OoredooRecharge()
bot.login()
bot.navigate_to_recharge()

# Browser stays open, solve CAPTCHA visually
captcha = input("Enter CAPTCHA text: ")
code = input("Enter recharge code: ")

response = bot.submit_recharge("27865121", code, captcha_text=captcha)
print(response)
bot.close()
```

## Response Format

```json
{
  "status": "success" | "error" | "unknown",
  "messages": [
    "Cette chaîne doit avoir exactement 14 caractères.",
    ...
  ],
  "html": "<!DOCTYPE html>..."
}
```

### Known Error Messages

| Message | Meaning |
|---------|---------|
| `Cette chaîne doit avoir exactement 14 caractères.` | Code must be 14 characters (validation error) |
| `Recharge non aboutie. Essayez de nouveau` | Invalid/expired/used recharge code (submit error) |
| `Captcha incorrect` | Wrong CAPTCHA entered |

### Success Response

**Message:**
```
✅ Votre recharge a été effectuée avec succès
```

**Behavior:**
- Stays on same page (`/recharge-card`)
- No redirect
- Green success alert
- Status: `success`

## Credentials

**Default credentials** (from your setup):
- Username: `27865121`
- Password: `espaceclient.ooredoo.tn%2F`

To use different credentials:

```python
bot.login(username="YOUR_PHONE", password="YOUR_PASSWORD")
```

## Testing

Test with a dummy 14-character code to see error response:

```bash
python3 recharge.py 12345678901234
```

Expected output:
```
❌ Error: Cette chaîne doit avoir exactement 14 caractères.
```

## Troubleshooting

### ChromeDriver not found

```bash
# Check if installed
which chromedriver

# Install if missing
brew install chromedriver  # macOS
apt install chromium-chromedriver  # Linux
```

### CAPTCHA solving fails

1. Check OpenAI API key is set:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. Use manual mode:
   ```python
   # Disable headless to see browser
   bot = OoredooRecharge(headless=False)
   ```

3. Check CAPTCHA screenshot:
   ```python
   captcha_img = bot.driver.find_element(By.CSS_SELECTOR, 'img[alt="captcha"]')
   captcha_img.screenshot('/tmp/captcha.png')
   ```

### Login fails

1. Verify credentials
2. Check if site is accessible:
   ```bash
   curl -I https://espaceclient.ooredoo.tn/
   ```
3. Try non-headless mode to debug visually

## Future Improvements

- [ ] Implement requests-only version (no browser)
- [ ] Add retry logic for failed CAPTCHAs
- [ ] Support multiple phone numbers
- [ ] Batch recharge support
- [ ] Web API wrapper
- [ ] Node.js version

## License

MIT
