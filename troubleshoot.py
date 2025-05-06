#!/usr/bin/env python3
"""
Troubleshooting script for Instagram API
This script checks if Chrome and ChromeDriver are properly installed and configured
"""

import os
import sys
import subprocess
import logging
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_chrome():
    """Check if Chrome is installed and get its version"""
    logger.info("Checking Chrome installation...")
    
    try:
        # Try to run Chrome with --version flag
        result = subprocess.run(
            ["google-chrome", "--version"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Chrome is installed: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"Chrome check failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"Error checking Chrome: {e}")
        return False

def find_chromedriver():
    """Find ChromeDriver in various locations"""
    logger.info("Looking for ChromeDriver...")
    
    # Define possible locations for ChromeDriver
    possible_locations = [
        # In the project directory
        os.path.join(os.getcwd(), "chromedriver", "chromedriver"),
        
        # In the parent directory (for EC2 setup)
        os.path.join(os.path.dirname(os.getcwd()), "chromedriver"),
        
        # In standard system locations
        "/usr/local/bin/chromedriver",
        "/usr/bin/chromedriver",
        
        # In the current directory
        os.path.join(os.getcwd(), "chromedriver")
    ]
    
    found_drivers = []
    
    # Check each location
    for location in possible_locations:
        if os.path.exists(location):
            if os.access(location, os.X_OK):
                logger.info(f"ChromeDriver found at {location} (executable)")
                found_drivers.append(location)
            else:
                logger.warning(f"ChromeDriver found at {location} but it's not executable")
    
    return found_drivers

def test_selenium():
    """Test if Selenium can start Chrome and navigate to a page"""
    logger.info("Testing Selenium with Chrome...")
    
    # Find ChromeDriver
    chromedriver_paths = find_chromedriver()
    if not chromedriver_paths:
        logger.error("No ChromeDriver found. Cannot test Selenium.")
        return False
    
    # Use the first found ChromeDriver
    chromedriver_path = chromedriver_paths[0]
    
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Create and start WebDriver
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to a test page
        logger.info("Navigating to google.com...")
        driver.get("https://www.google.com")
        
        # Get the page title
        title = driver.title
        logger.info(f"Page title: {title}")
        
        # Take a screenshot
        screenshot_path = "selenium_test.png"
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")
        
        # Close the driver
        driver.quit()
        
        logger.info("Selenium test successful!")
        return True
    except Exception as e:
        logger.error(f"Selenium test failed: {e}")
        return False

def check_display():
    """Check if DISPLAY environment variable is set"""
    logger.info("Checking DISPLAY environment variable...")
    
    display = os.environ.get("DISPLAY")
    if display:
        logger.info(f"DISPLAY is set to: {display}")
        return True
    else:
        logger.warning("DISPLAY is not set. This may cause issues with Chrome in headless mode.")
        return False

def check_xvfb():
    """Check if Xvfb is installed"""
    logger.info("Checking Xvfb installation...")
    
    try:
        result = subprocess.run(
            ["which", "Xvfb"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Xvfb is installed at: {result.stdout.strip()}")
            return True
        else:
            logger.warning("Xvfb is not installed. This may cause issues with Chrome in headless mode.")
            return False
    except Exception as e:
        logger.error(f"Error checking Xvfb: {e}")
        return False

def main():
    """Run all checks"""
    logger.info("=== Instagram API Troubleshooting ===")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info("")
    
    # Run checks
    chrome_ok = check_chrome()
    chromedriver_paths = find_chromedriver()
    display_ok = check_display()
    xvfb_ok = check_xvfb()
    selenium_ok = test_selenium()
    
    # Print summary
    logger.info("")
    logger.info("=== Troubleshooting Summary ===")
    logger.info(f"Chrome installed: {'✓' if chrome_ok else '✗'}")
    logger.info(f"ChromeDriver found: {'✓' if chromedriver_paths else '✗'}")
    if chromedriver_paths:
        for path in chromedriver_paths:
            logger.info(f"  - {path}")
    logger.info(f"DISPLAY set: {'✓' if display_ok else '✗'}")
    logger.info(f"Xvfb installed: {'✓' if xvfb_ok else '✗'}")
    logger.info(f"Selenium test: {'✓' if selenium_ok else '✗'}")
    
    # Overall status
    if chrome_ok and chromedriver_paths and selenium_ok:
        logger.info("")
        logger.info("✅ All critical checks passed! The Instagram API should work correctly.")
        return 0
    else:
        logger.info("")
        logger.info("❌ Some checks failed. Please fix the issues before running the Instagram API.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
