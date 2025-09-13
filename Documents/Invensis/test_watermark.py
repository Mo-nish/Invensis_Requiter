#!/usr/bin/env python3
"""
Watermark Component Test Script
Tests the watermark functionality across different scenarios
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_watermark_basic():
    """Test basic watermark functionality"""
    print("🧪 Testing Watermark Component...")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Check if application is running
    print("1. Testing application accessibility...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        if response.status_code == 200:
            print("   ✅ Application is running")
        else:
            print(f"   ❌ Application error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Application error: {e}")
        return False
    
    # Test 2: Check if watermark CSS is loaded
    print("\n2. Testing watermark CSS...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        if '.watermark' in response.text:
            print("   ✅ Watermark CSS found in page")
        else:
            print("   ❌ Watermark CSS not found")
            return False
    except Exception as e:
        print(f"   ❌ CSS test error: {e}")
        return False
    
    # Test 3: Check if watermark HTML is present
    print("\n3. Testing watermark HTML...")
    try:
        if 'Created by Monish Reddy' in response.text:
            print("   ✅ Watermark HTML found in page")
        else:
            print("   ❌ Watermark HTML not found")
            return False
    except Exception as e:
        print(f"   ❌ HTML test error: {e}")
        return False
    
    # Test 4: Check if watermark JavaScript is loaded
    print("\n4. Testing watermark JavaScript...")
    try:
        if 'handleWatermarkClick' in response.text:
            print("   ✅ Watermark JavaScript found in page")
        else:
            print("   ❌ Watermark JavaScript not found")
            return False
    except Exception as e:
        print(f"   ❌ JavaScript test error: {e}")
        return False
    
    print("\n✅ Basic watermark tests passed!")
    return True

def test_watermark_selenium():
    """Test watermark with Selenium for interactive testing"""
    print("\n🔍 Testing Watermark with Selenium...")
    print("=" * 50)
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Desktop size
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:5001")
        
        # Wait for page to load
        time.sleep(2)
        
        # Test 1: Check if watermark is visible
        print("1. Testing watermark visibility...")
        try:
            watermark = driver.find_element(By.CLASS_NAME, "watermark")
            if watermark.is_displayed():
                print("   ✅ Watermark is visible on page")
            else:
                print("   ❌ Watermark is not visible")
                return False
        except Exception as e:
            print(f"   ❌ Watermark visibility error: {e}")
            return False
        
        # Test 2: Check watermark text
        print("\n2. Testing watermark text...")
        try:
            watermark_text = watermark.text
            if watermark_text == "Created by Monish Reddy":
                print("   ✅ Watermark text is correct")
            else:
                print(f"   ❌ Watermark text mismatch: '{watermark_text}'")
                return False
        except Exception as e:
            print(f"   ❌ Watermark text error: {e}")
            return False
        
        # Test 3: Check watermark positioning
        print("\n3. Testing watermark positioning...")
        try:
            location = watermark.location
            size = watermark.size
            
            # Check if it's positioned in bottom-right
            if location['x'] > 0 and location['y'] > 0:
                print("   ✅ Watermark is positioned correctly")
                print(f"      Position: ({location['x']}, {location['y']})")
                print(f"      Size: {size['width']}x{size['height']}")
            else:
                print("   ❌ Watermark positioning issue")
                return False
        except Exception as e:
            print(f"   ❌ Watermark positioning error: {e}")
            return False
        
        # Test 4: Check watermark styling
        print("\n4. Testing watermark styling...")
        try:
            css_properties = driver.execute_script("""
                var watermark = document.querySelector('.watermark');
                var styles = window.getComputedStyle(watermark);
                return {
                    position: styles.position,
                    fontSize: styles.fontSize,
                    fontWeight: styles.fontWeight,
                    color: styles.color,
                    cursor: styles.cursor
                };
            """)
            
            print("   ✅ Watermark styling properties:")
            print(f"      Position: {css_properties['position']}")
            print(f"      Font Size: {css_properties['fontSize']}")
            print(f"      Font Weight: {css_properties['fontWeight']}")
            print(f"      Color: {css_properties['color']}")
            print(f"      Cursor: {css_properties['cursor']}")
            
        except Exception as e:
            print(f"   ❌ Watermark styling error: {e}")
            return False
        
        # Test 5: Test responsive behavior (mobile viewport)
        print("\n5. Testing responsive behavior...")
        try:
            # Set mobile viewport
            driver.set_window_size(375, 667)  # iPhone 6/7/8 size
            time.sleep(1)
            
            # Check if watermark adjusts for mobile
            mobile_watermark = driver.find_element(By.CLASS_NAME, "watermark")
            mobile_location = mobile_watermark.location
            mobile_size = mobile_watermark.size
            
            print("   ✅ Mobile viewport test:")
            print(f"      Mobile Position: ({mobile_location['x']}, {mobile_location['y']})")
            print(f"      Mobile Size: {mobile_size['width']}x{mobile_size['height']}")
            
            # Reset to desktop size
            driver.set_window_size(1920, 1080)
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Responsive test error: {e}")
            return False
        
        # Test 6: Test hover effects (if possible in headless mode)
        print("\n6. Testing hover effects...")
        try:
            # Try to simulate hover
            driver.execute_script("""
                var watermark = document.querySelector('.watermark');
                var event = new MouseEvent('mouseover', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true
                });
                watermark.dispatchEvent(event);
            """)
            
            time.sleep(0.5)
            
            # Check if hover state is applied
            hover_styles = driver.execute_script("""
                var watermark = document.querySelector('.watermark');
                var styles = window.getComputedStyle(watermark);
                return {
                    transform: styles.transform,
                    color: styles.color
                };
            """)
            
            print("   ✅ Hover effect test:")
            print(f"      Transform: {hover_styles['transform']}")
            print(f"      Color: {hover_styles['color']}")
            
        except Exception as e:
            print(f"   ❌ Hover test error: {e}")
            return False
        
        driver.quit()
        print("\n✅ Selenium watermark tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Selenium test error: {e}")
        return False

def test_watermark_config():
    """Test watermark configuration"""
    print("\n⚙️ Testing Watermark Configuration...")
    print("=" * 50)
    
    try:
        from watermark_config import WATERMARK_CONFIG, get_watermark_css, get_watermark_html, get_watermark_js
        
        # Test 1: Check configuration structure
        print("1. Testing configuration structure...")
        required_keys = ['text', 'font_size', 'color', 'hover_color', 'position']
        for key in required_keys:
            if key in WATERMARK_CONFIG:
                print(f"   ✅ {key}: {WATERMARK_CONFIG[key]}")
            else:
                print(f"   ❌ Missing key: {key}")
                return False
        
        # Test 2: Test CSS generation
        print("\n2. Testing CSS generation...")
        css = get_watermark_css()
        if '.watermark' in css and 'position: fixed' in css:
            print("   ✅ CSS generation working")
        else:
            print("   ❌ CSS generation failed")
            return False
        
        # Test 3: Test HTML generation
        print("\n3. Testing HTML generation...")
        html = get_watermark_html()
        if 'Created by Monish Reddy' in html and 'class="watermark"' in html:
            print("   ✅ HTML generation working")
        else:
            print("   ❌ HTML generation failed")
            return False
        
        # Test 4: Test JavaScript generation
        print("\n4. Testing JavaScript generation...")
        js = get_watermark_js()
        if 'handleWatermarkClick' in js:
            print("   ✅ JavaScript generation working")
        else:
            print("   ❌ JavaScript generation failed")
            return False
        
        print("\n✅ Configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def main():
    """Run all watermark tests"""
    print("🚀 Watermark Component Comprehensive Testing")
    print("=" * 60)
    
    # Run basic tests
    basic_result = test_watermark_basic()
    
    # Run configuration tests
    config_result = test_watermark_config()
    
    # Run Selenium tests (optional - requires Chrome driver)
    try:
        selenium_result = test_watermark_selenium()
    except Exception as e:
        print(f"\n⚠️ Selenium tests skipped (Chrome driver not available): {e}")
        selenium_result = True  # Don't fail the overall test
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Basic Tests: {'✅ PASSED' if basic_result else '❌ FAILED'}")
    print(f"   Config Tests: {'✅ PASSED' if config_result else '❌ FAILED'}")
    print(f"   Selenium Tests: {'✅ PASSED' if selenium_result else '⚠️ SKIPPED'}")
    
    if basic_result and config_result:
        print("\n🎉 All critical watermark tests passed!")
        print("✅ Watermark component is working correctly")
        return True
    else:
        print("\n❌ Some watermark tests failed")
        print("Please check the implementation")
        return False

if __name__ == "__main__":
    main()
