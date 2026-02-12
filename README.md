# Ooredoo Recharge Automation 🇹🇳

[![GitHub](https://img.shields.io/badge/GitHub-invictusdhahri%2Fooredoo--recharge--automation-blue?logo=github)](https://github.com/invictusdhahri/ooredoo-recharge-automation)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automated recharge system for Ooredoo Tunisia with AI CAPTCHA solving.

Fully automates the login → CAPTCHA solving → recharge submission flow for [espaceclient.ooredoo.tn](https://espaceclient.ooredoo.tn/).

## Features

- ✅ Automatic login to espaceclient.ooredoo.tn
- ✅ **AI-powered CAPTCHA solving** - FREE options available! (EasyOCR / Tesseract)
- ✅ Form submission with recharge codes
- ✅ Response parsing (success/error detection)
- ✅ Multiple implementation methods (Selenium + FREE OCR or OpenAI Vision)
- 🆓 **No API costs** - use completely free OCR libraries!

## Files

### 🆓 FREE Versions (No API costs!)
- **`recharge_free.py`** - ⭐ **RECOMMENDED** - Uses FREE EasyOCR (best free accuracy)
- **`recharge_tesseract.py`** - Uses FREE Tesseract OCR (lightweight & fast)

### 💰 Paid Version (Better accuracy)
- **`recharge.py`** - Uses OpenAI Vision API (~$0.01 per recharge)

### Other
- **`recharge_openclaw.py`** - OpenClaw browser tool integration
- **`FREE_CAPTCHA.md`** - Complete guide to free CAPTCHA solving

## Requirements

### Python Dependencies

#### 🆓 FREE Version (Recommended)
```bash
pip install selenium beautifulsoup4 easyocr Pillow
```

#### 💰 Paid Version (OpenAI)
```bash
pip install selenium beautifulsoup4 requests
export OPENAI_API_KEY="sk-..."
```

### Chrome Driver

All versions require ChromeDriver:

```bash
# Ubuntu/Debian
apt install chromium-chromedriver

# macOS
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

### CAPTCHA Solving Options

**Choose one:**

1. **FREE - EasyOCR** ⭐ (Recommended)
   ```bash
   pip install easyocr
   python3 recharge_free.py <CODE>
   ```

2. **FREE - Tesseract**
   ```bash
   sudo apt install tesseract-ocr  # Linux
   brew install tesseract          # macOS
   pip install pytesseract
   python3 recharge_tesseract.py <CODE>
   ```

3. **PAID - OpenAI Vision** (Most accurate)
   ```bash
   export OPENAI_API_KEY="sk-..."
   python3 recharge.py <CODE>
   ```

See **[FREE_CAPTCHA.md](FREE_CAPTCHA.md)** for detailed comparison!

## Usage

### 🆓 FREE Version (Recommended)

```bash
python3 recharge_free.py <14-DIGIT-RECHARGE-CODE>
```

**Example:**
```bash
python3 recharge_free.py 00641977131038
```

### 💰 OpenAI Version (Better Accuracy)

```bash
export OPENAI_API_KEY="sk-..."
python3 recharge.py <14-DIGIT-RECHARGE-CODE>
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
