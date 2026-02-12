#!/bin/bash
# Quick test script for Ooredoo recharge bot

echo "🧪 Ooredoo Recharge Bot - Test Mode"
echo "======================================"
echo ""

# Check dependencies
echo "📦 Checking dependencies..."
python3 -c "import selenium" 2>/dev/null || {
    echo "❌ Selenium not installed"
    echo "   Run: pip3 install -r requirements.txt"
    exit 1
}

python3 -c "import requests" 2>/dev/null || {
    echo "❌ Requests not installed"
    echo "   Run: pip3 install -r requirements.txt"
    exit 1
}

python3 -c "import bs4" 2>/dev/null || {
    echo "❌ BeautifulSoup not installed"
    echo "   Run: pip3 install -r requirements.txt"
    exit 1
}

echo "✅ All dependencies installed"
echo ""

# Check ChromeDriver
which chromedriver >/dev/null 2>&1 || {
    echo "⚠️  ChromeDriver not found in PATH"
    echo "   Install: brew install chromedriver (macOS)"
    echo "          apt install chromium-chromedriver (Linux)"
    echo ""
}

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo "   For AI CAPTCHA solving, run:"
    echo "   export OPENAI_API_KEY='sk-...'"
    echo ""
fi

# Test with dummy code (will fail but shows flow)
echo "🚀 Running test with dummy 14-char code..."
echo ""
python3 recharge.py 12345678901234

echo ""
echo "📝 Check /tmp/ooredoo_response.html for full response"
