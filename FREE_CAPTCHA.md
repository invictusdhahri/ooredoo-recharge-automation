# FREE CAPTCHA Solving Options 🆓

**No API costs! No subscriptions!** Use completely free OCR libraries instead of OpenAI Vision API.

## 🏆 Recommended: EasyOCR

**Best balance of accuracy and ease of use.**

### Install

```bash
pip install easyocr Pillow
```

### Usage

```bash
python3 recharge_free.py <14-DIGIT-CODE>
```

### Pros
- ✅ **Completely free**
- ✅ Best accuracy (80-90% on simple CAPTCHAs)
- ✅ No system dependencies
- ✅ Works on CPU (no GPU needed)
- ✅ Easy to install

### Cons
- ⚠️ First run downloads model files (~100MB)
- ⚠️ Slightly slower than OpenAI Vision

---

## 🔧 Alternative: Tesseract OCR

**System-level OCR, lightweight and fast.**

### Install

```bash
# Install system package
sudo apt install tesseract-ocr  # Ubuntu/Debian
brew install tesseract          # macOS

# Install Python wrapper
pip install pytesseract Pillow
```

### Usage

```bash
python3 recharge_tesseract.py <14-DIGIT-CODE>
```

### Pros
- ✅ **Completely free**
- ✅ Very lightweight
- ✅ Fast processing
- ✅ No downloads after install

### Cons
- ⚠️ Lower accuracy (60-70% on distorted text)
- ⚠️ Requires system package installation
- ⚠️ May need image preprocessing tuning

---

## 📊 Accuracy Comparison

| Solution | Accuracy | Speed | Setup | Cost |
|----------|----------|-------|-------|------|
| **OpenAI Vision** | 95-99% | Fast | Easy | $$ |
| **EasyOCR** ⭐ | 80-90% | Medium | Easy | FREE |
| **Tesseract** | 60-70% | Fast | Medium | FREE |

---

## 🎯 Which One to Use?

### Use **EasyOCR** if:
- You want the best free accuracy
- You don't mind a small download
- You have a few GB of disk space

### Use **Tesseract** if:
- You need lightweight solution
- You already have Tesseract installed
- Speed is more important than perfect accuracy

### Use **OpenAI Vision** if:
- You need near-perfect accuracy
- You already have an API key
- Cost is not a concern

---

## 🔄 Retry Logic for Free OCR

Since free OCR isn't 100% accurate, implement retry logic:

```python
from recharge_free import OoredooRecharge

bot = OoredooRecharge(headless=False)
bot.login()
bot.navigate_to_recharge()

max_attempts = 3
for attempt in range(max_attempts):
    try:
        response = bot.submit_recharge("27865121", "12345678901234")
        
        if response['status'] == 'success':
            print("✅ Success!")
            break
        elif 'Captcha incorrect' in str(response['messages']):
            print(f"❌ Wrong CAPTCHA (attempt {attempt + 1}/{max_attempts})")
            bot.navigate_to_recharge()  # Reload for new CAPTCHA
        else:
            print("Response:", response)
            break
    except Exception as e:
        print(f"Error: {e}")

bot.close()
```

---

## 🔍 Improving Accuracy

### For EasyOCR:

1. **Use GPU (if available):**
   ```python
   import easyocr
   READER = easyocr.Reader(['en'], gpu=True)
   ```

2. **Add allowlist:**
   ```python
   result = READER.readtext(
       image, 
       detail=0,
       allowlist='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
   )
   ```

### For Tesseract:

1. **Better preprocessing:**
   ```python
   # Increase contrast more
   enhancer = ImageEnhance.Contrast(img)
   img = enhancer.enhance(3.0)
   
   # Sharpen image
   img = img.filter(ImageFilter.SHARPEN)
   ```

2. **Custom config:**
   ```python
   config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
   ```

---

## 💰 Cost Comparison

### OpenAI Vision API
- **Cost:** ~$0.01 per image
- **100 recharges:** ~$1.00
- **1000 recharges:** ~$10.00

### EasyOCR / Tesseract
- **Cost:** $0.00
- **100 recharges:** FREE
- **1000 recharges:** FREE
- **∞ recharges:** FREE

---

## ✅ Recommendation

**Start with EasyOCR (`recharge_free.py`)** - it's the best free option!

If it doesn't work well, you can always switch to OpenAI Vision later.

```bash
# Install
pip install easyocr Pillow

# Test
python3 recharge_free.py 12345678901234
```
