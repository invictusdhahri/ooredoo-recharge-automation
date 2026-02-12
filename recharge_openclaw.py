#!/usr/bin/env python3
"""
Ooredoo Recharge Bot - OpenClaw Integration
Uses OpenClaw browser tool + vision model for full automation
"""

import json
import subprocess
import time

class OoredooRecharge:
    def __init__(self):
        self.target_id = None
        
    def run_browser_action(self, action_json):
        """Execute browser action via OpenClaw CLI"""
        cmd = ['openclaw', 'browser', '--json', json.dumps(action_json)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
        
    def analyze_image(self, image_path, prompt="Read the text shown in this CAPTCHA image. Return ONLY the characters you see, nothing else."):
        """Analyze image using OpenClaw image tool"""
        cmd = ['openclaw', 'image', '--image', image_path, '--prompt', prompt]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
        
    def login_and_navigate(self):
        """Login and navigate to recharge page"""
        print("🔐 Opening Ooredoo...")
        
        # Open page
        result = self.run_browser_action({
            'action': 'open',
            'profile': 'openclaw',
            'targetUrl': 'https://espaceclient.ooredoo.tn/'
        })
        self.target_id = result['targetId']
        time.sleep(2)
        
        print("📝 Filling login...")
        
        # Get snapshot to find refs
        snapshot = self.run_browser_action({
            'action': 'snapshot',
            'targetId': self.target_id,
            'refs': 'aria'
        })
        
        # Type username
        self.run_browser_action({
            'action': 'act',
            'targetId': self.target_id,
            'request': {
                'kind': 'type',
                'ref': 'e10',  # Username field
                'text': '27865121'
            }
        })
        
        # Type password
        self.run_browser_action({
            'action': 'act',
            'targetId': self.target_id,
            'request': {
                'kind': 'type',
                'ref': 'e13',  # Password field
                'text': 'espaceclient.ooredoo.tn%2F'
            }
        })
        
        # Click login
        self.run_browser_action({
            'action': 'act',
            'targetId': self.target_id,
            'request': {
                'kind': 'click',
                'ref': 'e18'  # LOGIN button
            }
        })
        
        time.sleep(3)
        print("✅ Logged in")
        
        # Navigate to recharge
        print("📱 Going to recharge page...")
        self.run_browser_action({
            'action': 'navigate',
            'targetId': self.target_id,
            'targetUrl': 'https://espaceclient.ooredoo.tn/recharge-card'
        })
        
        time.sleep(2)
        print("✅ On recharge page")
        
    def solve_captcha(self):
        """Screenshot and solve CAPTCHA"""
        print("🔍 Getting CAPTCHA...")
        
        # Take screenshot
        result = self.run_browser_action({
            'action': 'screenshot',
            'targetId': self.target_id
        })
        
        screenshot_path = result.get('path', '/tmp/screenshot.jpg')
        print(f"📸 Screenshot: {screenshot_path}")
        
        # Analyze with vision
        print("🤖 Analyzing CAPTCHA with AI...")
        captcha_text = self.analyze_image(screenshot_path)
        
        print(f"✅ CAPTCHA solved: {captcha_text}")
        return captcha_text
        
    def submit_recharge(self, recharge_code, captcha_text):
        """Submit recharge form"""
        print(f"\n📝 Submitting recharge...")
        print(f"   Code: {recharge_code}")
        print(f"   CAPTCHA: {captcha_text}")
        
        # Get current snapshot for refs
        snapshot = self.run_browser_action({
            'action': 'snapshot',
            'targetId': self.target_id,
            'refs': 'aria'
        })
        
        # Select first phone number option (27 865 121)
        self.run_browser_action({
            'action': 'act',
            'targetId': self.target_id,
            'request': {
                'kind': 'click',
                'ref': 'e67'  # Radio button for 27 865 121
            }
        })
        
        time.sleep(0.5)
        
        # Fill recharge code
        self.run_browser_action({
            'action': 'act',
            'targetId': self.target_id,
            'request': {
                'kind': 'type',
                'ref': 'e96',  # CODE DE RECHARGE field
                'text': recharge_code
            }
        })
        
        # Fill captcha
        self.run_browser_action({
            'action': 'act',
            'targetId': self.target_id,
            'request': {
                'kind': 'type',
                'ref': 'e103',  # CAPTCHA field
                'text': captcha_text
            }
        })
        
        # Click Valider
        self.run_browser_action({
            'action': 'act',
            'targetId': self.target_id,
            'request': {
                'kind': 'click',
                'ref': 'e110'  # Valider button
            }
        })
        
        time.sleep(3)
        print("✅ Submitted!")
        
        # Get response
        return self.get_response()
        
    def get_response(self):
        """Get page response HTML"""
        # Take snapshot to see result
        snapshot = self.run_browser_action({
            'action': 'snapshot',
            'targetId': self.target_id,
            'refs': 'aria'
        })
        
        # Also take screenshot
        result = self.run_browser_action({
            'action': 'screenshot',
            'targetId': self.target_id
        })
        
        print(f"📸 Response screenshot: {result.get('path')}")
        
        return {
            'snapshot': snapshot,
            'screenshot': result.get('path')
        }

def main():
    """Test the bot"""
    bot = OoredooRecharge()
    
    try:
        # Login and navigate
        bot.login_and_navigate()
        
        # Solve captcha
        captcha_text = bot.solve_captcha()
        
        # Get recharge code from user
        recharge_code = input("\nEnter recharge code: ")
        
        # Submit
        response = bot.submit_recharge(recharge_code, captcha_text)
        
        print("\n" + "="*50)
        print("RESPONSE:")
        print("="*50)
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
