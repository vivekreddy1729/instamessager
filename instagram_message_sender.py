import os
import time
import logging
import requests
import zipfile
import io
import sys
import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
def setup_logging():
    """Set up logging with file and console handlers"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create a timestamp for the log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join("logs", f"instagram_message_sender_{timestamp}.log")

    # Configure the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent log propagation to avoid duplicate logs
    logger.propagate = False

    return logger, log_file

# Set up the logger
logger, current_log_file = setup_logging()
logger.info(f"Logging initialized. Log file: {current_log_file}")

class InstagramMessageSender:
    def __init__(self, headless=True):
        """
        Initialize the Instagram Message Sender

        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.base_url = "https://www.instagram.com/"
        self.current_username = None  # Will store the current recipient username
        self.screenshot_folder = None  # Will store the path to the screenshot folder
        self.log_file = current_log_file  # Store the current log file path
        self.driver = self._setup_driver(headless)

    def _create_screenshot_folder(self):
        """
        Create a folder for storing screenshots for the current session

        Returns:
            str: Path to the screenshot folder
        """
        # Create a screenshots directory if it doesn't exist
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

        # Create a timestamp for the folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create a folder name with username and timestamp
        folder_name = f"{self.current_username}_{timestamp}" if self.current_username else f"session_{timestamp}"
        folder_path = os.path.join("screenshots", folder_name)

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.info(f"Created screenshot folder: {folder_path}")

            # Create a session-specific log file in the same folder
            session_log_file = os.path.join(folder_path, f"session_{timestamp}.log")

            # Add a file handler for this session
            file_handler = logging.FileHandler(session_log_file)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Update the log file path
            self.log_file = session_log_file
            logger.info(f"Session log file created: {session_log_file}")

        return folder_path

    def _get_screenshot_filename(self, base_name):
        """
        Generate a screenshot filename and ensure it's saved in the user's folder

        Args:
            base_name (str): The base name of the screenshot

        Returns:
            str: The full path to the screenshot file
        """
        # Create the screenshot folder if it doesn't exist yet
        if not self.screenshot_folder:
            self.screenshot_folder = self._create_screenshot_folder()

        # Generate the filename (just the base name with timestamp, no need for username prefix since it's in the folder)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}.png"

        # Return the full path
        return os.path.join(self.screenshot_folder, filename)

    def _setup_driver(self, headless):
        """
        Set up the Chrome WebDriver

        Args:
            headless (bool): Whether to run the browser in headless mode

        Returns:
            WebDriver: Configured Chrome WebDriver
        """
        logger.info("Setting up Chrome WebDriver...")

        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

        # Download ChromeDriver if it doesn't exist
        chromedriver_path = self._download_chromedriver()

        # Create and return the WebDriver
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _download_chromedriver(self):
        """
        Download the appropriate ChromeDriver for the current system

        Returns:
            str: Path to the ChromeDriver executable
        """
        logger.info("Checking for ChromeDriver...")

        # Define the ChromeDriver path
        chromedriver_dir = os.path.join(os.getcwd(), "chromedriver")
        chromedriver_path = os.path.join(chromedriver_dir, "chromedriver.exe")

        # Check if ChromeDriver already exists
        if os.path.exists(chromedriver_path):
            logger.info(f"ChromeDriver found at {chromedriver_path}")
            return chromedriver_path

        # Create directory if it doesn't exist
        if not os.path.exists(chromedriver_dir):
            os.makedirs(chromedriver_dir)

        # Download the latest stable ChromeDriver for Windows
        logger.info("Downloading ChromeDriver for Windows...")
        chromedriver_url = "https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.49/win32/chromedriver-win32.zip"

        try:
            # Download the zip file
            response = requests.get(chromedriver_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Extract the zip file
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                zip_file.extractall(chromedriver_dir)

            # The extracted path will be in a subdirectory
            extracted_driver_path = os.path.join(chromedriver_dir, "chromedriver-win32", "chromedriver.exe")

            # Move the chromedriver.exe to the main directory
            if os.path.exists(extracted_driver_path):
                import shutil
                shutil.copy(extracted_driver_path, chromedriver_path)
                logger.info(f"ChromeDriver downloaded and extracted to {chromedriver_path}")
                return chromedriver_path
            else:
                logger.error(f"ChromeDriver not found in extracted files at {extracted_driver_path}")
                raise FileNotFoundError(f"ChromeDriver not found in extracted files")

        except Exception as e:
            logger.error(f"Error downloading ChromeDriver: {e}")
            raise

    def login(self, username, password):
        """
        Log in to Instagram

        Args:
            username (str): Instagram username
            password (str): Instagram password

        Returns:
            bool: True if login successful, False otherwise
        """
        logger.info(f"Attempting to log in as {username}...")
        # Reset the screenshot folder for this login session
        self.screenshot_folder = None

        try:
            # Navigate to Instagram login page
            self.driver.get(self.base_url)

            # Add a delay to avoid detection
            time.sleep(2)

            # Wait for the login form to appear
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )

            # Enter username and password with random delays to mimic human behavior
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")

            # Clear fields first
            username_field.clear()
            password_field.clear()

            # Type like a human with delays
            self._type_like_human(username_field, username)
            time.sleep(0.5)
            self._type_like_human(password_field, password)

            # Wait a bit before clicking login
            time.sleep(1)

            # Click login button using JavaScript to avoid interception issues
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            self.driver.execute_script("arguments[0].click();", login_button)

            # Wait for login to complete - check for multiple possible outcomes
            try:
                # Check for "Save Your Login Info" dialog
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and contains(., 'Save Your Login Info')]//button[contains(., 'Not Now')]"))
                )
                save_info_button = self.driver.find_element(By.XPATH, "//div[@role='dialog' and contains(., 'Save Your Login Info')]//button[contains(., 'Not Now')]")
                self.driver.execute_script("arguments[0].click();", save_info_button)
                logger.info("Handled 'Save Your Login Info' dialog")
            except TimeoutException:
                # Check if we're already logged in (home feed is visible)
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and contains(., 'Turn on Notifications')]//button[contains(., 'Not Now')]"))
                    )
                    notifications_button = self.driver.find_element(By.XPATH, "//div[@role='dialog' and contains(., 'Turn on Notifications')]//button[contains(., 'Not Now')]")
                    self.driver.execute_script("arguments[0].click();", notifications_button)
                    logger.info("Handled 'Turn on Notifications' dialog")
                except TimeoutException:
                    # Check if we're on the home feed
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]"))
                        )
                        logger.info("Already on home feed")
                    except TimeoutException:
                        # Check for security verification
                        try:
                            WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//input[@name='verificationCode']"))
                            )
                            logger.error("Security verification required. Please login manually.")
                            return False
                        except TimeoutException:
                            # Check for incorrect password
                            try:
                                error_message = self.driver.find_element(By.ID, "slfErrorAlert").text
                                logger.error(f"Login failed: {error_message}")
                                return False
                            except NoSuchElementException:
                                logger.warning("Could not determine login status. Proceeding anyway...")

            # Take a screenshot to verify login status
            screenshot_filename = self._get_screenshot_filename("login_status")
            self.driver.save_screenshot(screenshot_filename)
            logger.info(f"Login process completed. Screenshot saved as '{screenshot_filename}'")

            # Check if we're actually logged in by looking for common elements on the home page
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]"))
                )
                logger.info("Login successful! Verified by finding inbox link.")
                return True
            except TimeoutException:
                logger.error("Login may have failed. Could not find inbox link.")
                return False

        except TimeoutException as e:
            logger.error(f"Timeout during login: {e}")
            return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    def _type_like_human(self, element, text):
        """
        Type text into an element with random delays to mimic human typing

        Args:
            element: The web element to type into
            text (str): The text to type
        """
        import random

        for char in text:
            element.send_keys(char)
            # Random delay between 0.05 and 0.2 seconds
            time.sleep(random.uniform(0.05, 0.2))

    def send_message(self, recipient_username, message):
        """
        Send a direct message to a specific Instagram user

        Args:
            recipient_username (str): Username of the recipient
            message (str): Message to send

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        logger.info(f"Attempting to send message to {recipient_username}...")
        # Set the current username for screenshot naming
        self.current_username = recipient_username
        # Reset the screenshot folder for this new message request
        self.screenshot_folder = None

        try:
            # First, try to navigate to the user's profile to check if we need to follow them
            self.driver.get(f"{self.base_url}{recipient_username}/")

            # Add a delay to avoid detection
            time.sleep(2)

            # Take a screenshot of the user's profile
            screenshot_filename = self._get_screenshot_filename("user_profile")
            self.driver.save_screenshot(screenshot_filename)
            logger.info(f"Screenshot of user profile saved as '{screenshot_filename}'")

            # Check if we need to follow the user first - this is critical
            try:
                logger.info("Looking for follow button with multiple strategies...")
                screenshot_filename = self._get_screenshot_filename("before_follow_attempt")
                self.driver.save_screenshot(screenshot_filename)

                # Based on the exact HTML structure provided
                logger.info("Looking for follow button with exact structure provided...")

                # Exact selectors based on the HTML structure provided
                precise_follow_button_xpaths = [
                    # Exact match for the provided HTML structure
                    "//button[contains(@class, '_acan _acap _acaq _acas _aj1- _ap30')][.//div[contains(@class, '_ap3a _aaco _aacw _aad6 _aade') and contains(text(), 'Follow')]]",

                    # Slightly more general but still specific to the structure
                    "//button[contains(@class, '_acan')][.//div[contains(text(), 'Follow')]]",

                    # Even more general but still looking for the nested structure
                    "//button[.//div[.//div[contains(text(), 'Follow')]]]"
                ]

                # Try the precise selectors first
                follow_button = None
                for xpath in precise_follow_button_xpaths:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed():
                                follow_button = element
                                logger.info(f"Found follow button with precise selector: {xpath}")
                                break
                        if follow_button:
                            break
                    except Exception as e:
                        logger.debug(f"Error with precise xpath {xpath}: {e}")
                        continue

                # If precise selectors didn't work, try more general approaches
                if not follow_button:
                    logger.info("Precise selectors didn't find the follow button, trying more general approaches...")

                    # More general selectors
                    general_follow_button_xpaths = [
                        "//button[contains(text(), 'Follow')]",
                        "//button[.//div[contains(text(), 'Follow')]]",
                        "//button[.//span[contains(text(), 'Follow')]]",
                        "//button[contains(@class, 'follow')]",
                        "//button[contains(@class, '_acan')]" # Common class for Instagram buttons
                    ]

                    for xpath in general_follow_button_xpaths:
                        try:
                            elements = self.driver.find_elements(By.XPATH, xpath)
                            for element in elements:
                                # Check if this element is visible and contains 'Follow'
                                if element.is_displayed():
                                    # Try to get the text from the button or its children
                                    button_text = element.text.lower()
                                    if "follow" in button_text and "following" not in button_text:
                                        follow_button = element
                                        logger.info(f"Found follow button with text: '{element.text}'")
                                        break
                            if follow_button:
                                break
                        except Exception as e:
                            logger.debug(f"Error with general xpath {xpath}: {e}")
                            continue

                # Last resort: scan all buttons on the page
                if not follow_button:
                    logger.info("Still couldn't find follow button, scanning all buttons...")
                    try:
                        # Get all buttons on the page
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for button in buttons:
                            try:
                                if button.is_displayed():
                                    # Try to get the text content
                                    button_text = button.text.lower()
                                    if "follow" in button_text and "following" not in button_text:
                                        follow_button = button
                                        logger.info(f"Found follow button with text: '{button.text}'")
                                        break

                                    # If no text directly on button, check for nested elements with text
                                    if not button_text:
                                        inner_elements = button.find_elements(By.XPATH, ".//div") + button.find_elements(By.XPATH, ".//span")
                                        for inner in inner_elements:
                                            inner_text = inner.text.lower()
                                            if "follow" in inner_text and "following" not in inner_text:
                                                follow_button = button
                                                logger.info(f"Found follow button with inner text: '{inner.text}'")
                                                break
                            except:
                                continue
                    except Exception as e:
                        logger.warning(f"Error scanning all buttons: {e}")

                # If we still can't find it, try using JavaScript to find it
                if not follow_button:
                    logger.info("Trying JavaScript approach to find follow button...")
                    try:
                        # Use JavaScript to find buttons with "Follow" text
                        js_result = self.driver.execute_script("""
                            const buttons = Array.from(document.querySelectorAll('button'));
                            for (const button of buttons) {
                                if (button.innerText.includes('Follow') && !button.innerText.includes('Following')) {
                                    return button;
                                }
                            }
                            return null;
                        """)

                        if js_result:
                            follow_button = js_result
                            logger.info("Found follow button using JavaScript")
                    except Exception as e:
                        logger.warning(f"Error using JavaScript to find follow button: {e}")

                if follow_button:
                    logger.info(f"Following user {recipient_username} first...")
                    # Take a screenshot of the follow button before clicking
                    screenshot_filename = self._get_screenshot_filename("follow_button_found")
                    self.driver.save_screenshot(screenshot_filename)

                    # Try multiple click methods with retries
                    max_attempts = 3
                    for attempt in range(max_attempts):
                        try:
                            logger.info(f"Attempt {attempt+1} to click follow button")

                            # Try different click methods
                            if attempt == 0:
                                # First try regular click
                                logger.info("Trying regular click")
                                follow_button.click()
                            elif attempt == 1:
                                # Then try JavaScript click
                                logger.info("Trying JavaScript click")
                                self.driver.execute_script("arguments[0].click();", follow_button)
                            else:
                                # Last resort: try to simulate a more complex interaction
                                logger.info("Trying advanced click method")
                                # Move to the element first
                                from selenium.webdriver.common.action_chains import ActionChains
                                actions = ActionChains(self.driver)
                                actions.move_to_element(follow_button).pause(0.5).click().perform()

                            # Wait a moment to see if the click worked
                            time.sleep(2)

                            # Take a screenshot after the click attempt
                            screenshot_filename = self._get_screenshot_filename(f"follow_click_attempt_{attempt+1}")
                            self.driver.save_screenshot(screenshot_filename)

                            # Check if the button text changed to "Following" or "Requested"
                            success_indicators = ["Following", "Requested", "Unfollow"]
                            follow_success = False

                            # Try to get updated text from the button
                            try:
                                updated_text = follow_button.text
                                logger.info(f"Button text after click: '{updated_text}'")
                                if any(indicator.lower() in updated_text.lower() for indicator in success_indicators):
                                    logger.info("Follow successful based on button text change!")
                                    follow_success = True
                                    break
                            except:
                                pass

                            # If button text didn't change, look for other indicators
                            if not follow_success:
                                # Check if any button now says "Following" or "Requested"
                                for indicator in success_indicators:
                                    try:
                                        success_elements = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{indicator}')]")
                                        success_elements.extend(self.driver.find_elements(By.XPATH, f"//div[contains(@role, 'button') and contains(text(), '{indicator}')]"))

                                        for element in success_elements:
                                            if element.is_displayed():
                                                logger.info(f"Follow successful! Found '{indicator}' button.")
                                                follow_success = True
                                                break

                                        if follow_success:
                                            break
                                    except:
                                        continue

                            if follow_success:
                                break

                            logger.info(f"Follow attempt {attempt+1} may not have succeeded, trying again...")

                        except Exception as e:
                            logger.warning(f"Error during follow attempt {attempt+1}: {e}")
                            if attempt < max_attempts - 1:  # Don't sleep after the last attempt
                                time.sleep(1)  # Wait before next attempt

                    # Wait for follow action to complete
                    time.sleep(3)  # Increased wait time to ensure follow completes

                    # Take screenshot after follow attempt
                    screenshot_filename = self._get_screenshot_filename("after_follow_attempt")
                    self.driver.save_screenshot(screenshot_filename)

                    # Check for and handle any popups that might appear after following
                    try:
                        # Common popup buttons to look for
                        popup_button_texts = ["Not Now", "Cancel", "Close", "Skip", "OK"]

                        for button_text in popup_button_texts:
                            try:
                                popup_buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                                popup_buttons.extend(self.driver.find_elements(By.XPATH, f"//div[contains(@role, 'button') and contains(text(), '{button_text}')]"))

                                for button in popup_buttons:
                                    if button.is_displayed():
                                        logger.info(f"Found popup with '{button_text}' button, dismissing it")
                                        self.driver.execute_script("arguments[0].click();", button)
                                        time.sleep(1)
                                        screenshot_filename = self._get_screenshot_filename("popup_dismissed")
                                        self.driver.save_screenshot(screenshot_filename)
                                        break
                            except:
                                continue
                    except Exception as popup_error:
                        logger.warning(f"Error handling popups: {popup_error}")

                    # Final verification of follow status
                    logger.info("Performing final verification of follow status...")
                    screenshot_filename = self._get_screenshot_filename("before_final_verification")
                    self.driver.save_screenshot(screenshot_filename)

                    # Check if we need to refresh the page for a clean state
                    try:
                        # Refresh the page to get the current state
                        self.driver.refresh()
                        time.sleep(3)
                        self.driver.save_screenshot("after_refresh_for_verification.png")

                        # Look for indicators that we're following the user
                        success_indicators = ["Following", "Requested", "Unfollow", "Message"]
                        follow_verified = False

                        # Check for success indicators in buttons
                        for indicator in success_indicators:
                            try:
                                # Use a more comprehensive set of XPath expressions
                                indicator_xpaths = [
                                    f"//button[contains(text(), '{indicator}')]",
                                    f"//div[contains(@role, 'button') and contains(text(), '{indicator}')]",
                                    f"//button[.//div[contains(text(), '{indicator}')]]",
                                    f"//button[.//span[contains(text(), '{indicator}')]]"
                                ]

                                for xpath in indicator_xpaths:
                                    elements = self.driver.find_elements(By.XPATH, xpath)
                                    for element in elements:
                                        if element.is_displayed():
                                            logger.info(f"Follow verified! Found '{indicator}' indicator.")
                                            follow_verified = True
                                            self.driver.save_screenshot(f"follow_verified_{indicator}.png")
                                            break

                                    if follow_verified:
                                        break

                                if follow_verified:
                                    break
                            except Exception as e:
                                logger.debug(f"Error checking for indicator '{indicator}': {e}")

                        # If we still can't verify, try one last approach with JavaScript
                        if not follow_verified:
                            logger.info("Trying JavaScript to verify follow status...")
                            try:
                                # Use JavaScript to check for follow indicators
                                js_result = self.driver.execute_script("""
                                    const indicators = ['Following', 'Requested', 'Unfollow', 'Message'];
                                    const allElements = document.querySelectorAll('button, div[role="button"]');

                                    for (const element of allElements) {
                                        const text = element.innerText;
                                        for (const indicator of indicators) {
                                            if (text.includes(indicator)) {
                                                return {found: true, indicator: indicator, text: text};
                                            }
                                        }
                                    }
                                    return {found: false};
                                """)

                                if js_result and js_result.get('found'):
                                    logger.info(f"Follow verified via JavaScript! Found '{js_result.get('indicator')}' with text '{js_result.get('text')}'")
                                    follow_verified = True
                                    self.driver.save_screenshot("follow_verified_js.png")
                            except Exception as js_error:
                                logger.warning(f"Error using JavaScript to verify follow: {js_error}")

                        # Final decision on follow status
                        if follow_verified:
                            logger.info(f"Successfully verified that we are following {recipient_username}")
                            self.driver.save_screenshot("follow_success_final.png")
                        else:
                            # One last attempt to follow if verification failed
                            logger.warning("Could not verify follow status, making one final attempt to follow")

                            # Try to find and click the follow button one more time
                            try:
                                # Use the most precise selector based on the HTML structure provided
                                final_attempt_xpath = "//button[contains(@class, '_acan _acap _acaq _acas _aj1- _ap30')][.//div[contains(@class, '_ap3a _aaco _aacw _aad6 _aade') and contains(text(), 'Follow')]]"
                                final_buttons = self.driver.find_elements(By.XPATH, final_attempt_xpath)

                                if final_buttons:
                                    for button in final_buttons:
                                        if button.is_displayed():
                                            logger.info("Found follow button in final attempt, clicking it")
                                            # Try both click methods
                                            try:
                                                button.click()
                                            except:
                                                self.driver.execute_script("arguments[0].click();", button)

                                            time.sleep(3)
                                            screenshot_filename = self._get_screenshot_filename("final_follow_attempt")
                                            self.driver.save_screenshot(screenshot_filename)
                                            break
                                else:
                                    logger.warning("No follow button found in final attempt")
                            except Exception as final_error:
                                logger.warning(f"Error in final follow attempt: {final_error}")
                    except Exception as verify_error:
                        logger.warning(f"Error during follow verification: {verify_error}")
                else:
                    logger.info(f"Already following user {recipient_username} or follow button not found")
                    screenshot_filename = self._get_screenshot_filename("no_follow_button_found")
                    self.driver.save_screenshot(screenshot_filename)
            except Exception as e:
                logger.warning(f"Error during follow process: {e}")
                screenshot_filename = self._get_screenshot_filename("follow_error")
                self.driver.save_screenshot(screenshot_filename)

            # Now look for the message button on the profile
            try:
                logger.info("Looking for message button...")
                self.driver.save_screenshot("before_message_button.png")

                # More comprehensive list of message button selectors
                message_button_xpaths = [
                    "//div[contains(@role, 'button') and contains(text(), 'Message')]",
                    "//button[contains(text(), 'Message')]",
                    "//a[contains(@href, '/direct/') and contains(text(), 'Message')]",
                    "//span[contains(text(), 'Message')]/parent::button",
                    "//span[contains(text(), 'Message')]/parent::div",
                    "//header//button[contains(text(), 'Message')]",
                    "//section//button[contains(text(), 'Message')]",
                    "//div[contains(@class, 'message')]",
                    "//button[contains(@class, 'message')]"
                ]

                # Try to find any message button
                message_button = None
                for xpath in message_button_xpaths:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            # Check if this element is visible and contains 'Message'
                            if element.is_displayed() and "message" in element.text.lower():
                                message_button = element
                                logger.info(f"Found message button with text: '{element.text}'")
                                break
                        if message_button:
                            break
                    except Exception as e:
                        logger.debug(f"Error with xpath {xpath}: {e}")
                        continue

                # If we still haven't found it, try a more aggressive approach
                if not message_button:
                    logger.info("Trying alternative approach to find message button...")
                    # Get all buttons on the page
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        try:
                            if button.is_displayed() and "message" in button.text.lower():
                                message_button = button
                                logger.info(f"Found message button with text: '{button.text}'")
                                break
                        except:
                            continue

                if message_button:
                    logger.info("Found message button on profile, clicking it...")
                    # Try multiple click methods
                    try:
                        # First try regular click
                        message_button.click()
                    except Exception as e:
                        logger.info(f"Regular click failed: {e}, trying JavaScript click")
                        self.driver.execute_script("arguments[0].click();", message_button)

                    # Wait for 3 seconds as requested
                    time.sleep(3)

                    # Take a screenshot after clicking message button
                    screenshot_filename = self._get_screenshot_filename("after_message_button")
                    self.driver.save_screenshot(screenshot_filename)

                    # Check for any confirmation dialogs that might appear when clicking message
                    try:
                        # Look for common confirmation buttons
                        confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Send Message')]")
                        confirm_buttons.extend(self.driver.find_elements(By.XPATH, "//div[contains(@role, 'button') and contains(text(), 'Send Message')]"))
                        confirm_buttons.extend(self.driver.find_elements(By.XPATH, "//button[contains(text(), 'OK')]"))
                        confirm_buttons.extend(self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue')]"))

                        for button in confirm_buttons:
                            if button.is_displayed():
                                logger.info("Found confirmation dialog, clicking to proceed")
                                self.driver.execute_script("arguments[0].click();", button)
                                time.sleep(2)
                                self.driver.save_screenshot("confirmation_clicked.png")
                                break
                    except Exception as confirm_error:
                        logger.warning(f"Error handling confirmation dialog: {confirm_error}")

                    # Wait for message input to appear
                    try:
                        message_input = WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
                        )

                        # Enter message with human-like typing
                        self._type_like_human(message_input, message)
                        logger.info("Entered message text")

                        # Take a screenshot before sending
                        screenshot_filename = self._get_screenshot_filename("before_send")
                        self.driver.save_screenshot(screenshot_filename)

                        # Find and click the send button using the exact structure provided
                        logger.info("Looking for send button with exact structure provided...")
                        screenshot_filename = self._get_screenshot_filename("looking_for_send_button")
                        self.driver.save_screenshot(screenshot_filename)

                        # Try multiple approaches to find the send button
                        send_button = None

                        # 1. First try the exact class structure provided
                        try:
                            # Based on the HTML structure: <div class="x1i10hfl xjqpnuy xa49m3k ... x7fd4wk x1sfzahb xfs2ol5" role="button" tabindex="0">Send</div>
                            send_button_xpath = "//div[contains(@class, 'x1i10hfl') and contains(@role, 'button') and contains(text(), 'Send')]"
                            send_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, send_button_xpath))
                            )
                            logger.info("Found send button using exact class structure")
                        except Exception as e:
                            logger.debug(f"Could not find send button with exact class structure: {e}")

                        # 2. Try with partial class matching
                        if not send_button:
                            try:
                                send_button_xpath = "//div[contains(@class, 'x1i10hfl') and contains(@class, 'xjqpnuy') and contains(@role, 'button')]"
                                elements = self.driver.find_elements(By.XPATH, send_button_xpath)
                                for element in elements:
                                    if element.is_displayed() and "send" in element.text.lower():
                                        send_button = element
                                        logger.info(f"Found send button with partial class matching: {element.text}")
                                        break
                            except Exception as e:
                                logger.debug(f"Could not find send button with partial class matching: {e}")

                        # 3. Try a more general approach with role and text
                        if not send_button:
                            try:
                                send_button_xpath = "//div[@role='button' and contains(text(), 'Send')]"
                                send_button = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, send_button_xpath))
                                )
                                logger.info("Found send button using role and text")
                            except Exception as e:
                                logger.debug(f"Could not find send button with role and text: {e}")

                        # 4. Try with button element
                        if not send_button:
                            try:
                                send_button_xpath = "//button[contains(text(), 'Send')]"
                                send_button = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, send_button_xpath))
                                )
                                logger.info("Found send button using button element")
                            except Exception as e:
                                logger.debug(f"Could not find send button with button element: {e}")

                        # 5. Try with any element containing Send text
                        if not send_button:
                            try:
                                send_button_xpath = "//*[contains(text(), 'Send')]"
                                elements = self.driver.find_elements(By.XPATH, send_button_xpath)
                                for element in elements:
                                    if element.is_displayed() and element.is_enabled():
                                        send_button = element
                                        logger.info(f"Found send button with generic text search: {element.tag_name}")
                                        break
                            except Exception as e:
                                logger.debug(f"Could not find send button with generic text search: {e}")

                        # 6. Last resort: use JavaScript to find the button
                        if not send_button:
                            logger.info("Trying JavaScript to find send button...")
                            try:
                                send_button = self.driver.execute_script("""
                                    // Try to find elements with 'Send' text
                                    const elements = Array.from(document.querySelectorAll('*'));
                                    for (const element of elements) {
                                        if (element.textContent.includes('Send') &&
                                            (element.tagName === 'BUTTON' || element.getAttribute('role') === 'button') &&
                                            element.offsetWidth > 0 &&
                                            element.offsetHeight > 0) {
                                            return element;
                                        }
                                    }
                                    return null;
                                """)
                                if send_button:
                                    logger.info("Found send button using JavaScript")
                            except Exception as e:
                                logger.debug(f"Could not find send button with JavaScript: {e}")

                        # Take a screenshot of the current state
                        screenshot_filename = self._get_screenshot_filename("before_send_button_click")
                        self.driver.save_screenshot(screenshot_filename)

                        # Click the send button if found
                        if send_button:
                            logger.info("Clicking send button...")
                            try:
                                # Try multiple click methods
                                try:
                                    # First try regular click
                                    send_button.click()
                                    logger.info("Regular click on send button successful")
                                except Exception as click_error:
                                    logger.info(f"Regular click failed: {click_error}, trying JavaScript click")
                                    self.driver.execute_script("arguments[0].click();", send_button)
                                    logger.info("JavaScript click on send button successful")
                            except Exception as e:
                                logger.error(f"Failed to click send button: {e}")
                                raise

                            # Wait a moment to ensure the message is sent
                            time.sleep(2)

                            # Take a screenshot after sending
                            screenshot_filename = self._get_screenshot_filename("after_send")
                            self.driver.save_screenshot(screenshot_filename)

                            logger.info(f"Message sent to {recipient_username} successfully!")
                            return True
                        else:
                            logger.error("Could not find send button")
                            screenshot_filename = self._get_screenshot_filename("send_button_not_found")
                            self.driver.save_screenshot(screenshot_filename)
                            return False
                    except TimeoutException:
                        logger.error("Could not find message input field")
                        screenshot_filename = self._get_screenshot_filename("message_input_not_found")
                        self.driver.save_screenshot(screenshot_filename)
                        return False
                else:
                    logger.warning("Message button not found on profile, trying alternative method...")
            except Exception as e:
                logger.warning(f"Error finding message button on profile: {e}")

            # If direct messaging from profile didn't work, try the inbox method
            logger.info("Trying to message via inbox...")
            self.driver.get(f"{self.base_url}direct/inbox/")

            # Add a delay to avoid detection
            time.sleep(2)

            # Take a screenshot of the inbox page
            screenshot_filename = self._get_screenshot_filename("inbox_page")
            self.driver.save_screenshot(screenshot_filename)
            logger.info(f"Screenshot of inbox page saved as '{screenshot_filename}'")

            # Wait for the page to load and look for the "Send message" button
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send message')]"))
                )

                # Click on "Send message" button using JavaScript
                send_message_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Send message')]")
                self.driver.execute_script("arguments[0].click();", send_message_button)
                logger.info("Clicked 'Send message' button")
            except TimeoutException:
                # Try alternative selectors for the "New message" button
                try:
                    new_message_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'New message')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", new_message_button)
                    logger.info("Clicked 'New message' button")
                except TimeoutException:
                    logger.error("Could not find 'Send message' or 'New message' button")
                    self.driver.save_screenshot("message_button_not_found.png")
                    return False

            # Wait for the search input to appear
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search...']"))
            )

            # Enter recipient username with human-like typing
            search_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Search...']")
            self._type_like_human(search_input, recipient_username)

            # Wait for search results
            time.sleep(2)  # Give time for search results to appear

            # Take a screenshot of search results
            screenshot_filename = self._get_screenshot_filename("search_results")
            self.driver.save_screenshot(screenshot_filename)
            logger.info(f"Screenshot of search results saved as '{screenshot_filename}'")

            # Try different XPath patterns to find the recipient
            recipient_xpath_patterns = [
                f"//div[contains(@aria-label, '{recipient_username}')]",
                f"//div[contains(text(), '{recipient_username}')]",
                f"//span[contains(text(), '{recipient_username}')]/ancestor::div[contains(@role, 'button')]"
            ]

            recipient = None
            for xpath in recipient_xpath_patterns:
                try:
                    recipient = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    break
                except TimeoutException:
                    continue

            if recipient is None:
                logger.error(f"Could not find recipient: {recipient_username}")
                return False

            # Select the recipient using JavaScript
            self.driver.execute_script("arguments[0].click();", recipient)
            logger.info(f"Selected recipient: {recipient_username}")

            # Wait and click "Next" button
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
                )
                self.driver.execute_script("arguments[0].click();", next_button)
                logger.info("Clicked 'Next' button")
            except TimeoutException:
                logger.error("Could not find 'Next' button")
                self.driver.save_screenshot("next_button_not_found.png")
                return False

            # Wait for message input to appear
            try:
                message_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
                )

                # Enter message with human-like typing
                self._type_like_human(message_input, message)
                logger.info("Entered message text")

                # Take a screenshot before sending
                screenshot_filename = self._get_screenshot_filename("before_send")
                self.driver.save_screenshot(screenshot_filename)

                # Find and click the send button using the exact structure provided
                logger.info("Looking for send button with exact structure provided...")
                screenshot_filename = self._get_screenshot_filename("looking_for_send_button_inbox")
                self.driver.save_screenshot(screenshot_filename)

                # Try multiple approaches to find the send button
                send_button = None

                # 1. First try the exact class structure provided
                try:
                    # Based on the HTML structure: <div class="x1i10hfl xjqpnuy xa49m3k ... x7fd4wk x1sfzahb xfs2ol5" role="button" tabindex="0">Send</div>
                    send_button_xpath = "//div[contains(@class, 'x1i10hfl') and contains(@role, 'button') and contains(text(), 'Send')]"
                    send_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, send_button_xpath))
                    )
                    logger.info("Found send button using exact class structure")
                except Exception as e:
                    logger.debug(f"Could not find send button with exact class structure: {e}")

                # 2. Try with partial class matching
                if not send_button:
                    try:
                        send_button_xpath = "//div[contains(@class, 'x1i10hfl') and contains(@class, 'xjqpnuy') and contains(@role, 'button')]"
                        elements = self.driver.find_elements(By.XPATH, send_button_xpath)
                        for element in elements:
                            if element.is_displayed() and "send" in element.text.lower():
                                send_button = element
                                logger.info(f"Found send button with partial class matching: {element.text}")
                                break
                    except Exception as e:
                        logger.debug(f"Could not find send button with partial class matching: {e}")

                # 3. Try a more general approach with role and text
                if not send_button:
                    try:
                        send_button_xpath = "//div[@role='button' and contains(text(), 'Send')]"
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, send_button_xpath))
                        )
                        logger.info("Found send button using role and text")
                    except Exception as e:
                        logger.debug(f"Could not find send button with role and text: {e}")

                # 4. Try with button element
                if not send_button:
                    try:
                        send_button_xpath = "//button[contains(text(), 'Send')]"
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, send_button_xpath))
                        )
                        logger.info("Found send button using button element")
                    except Exception as e:
                        logger.debug(f"Could not find send button with button element: {e}")

                # 5. Try with any element containing Send text
                if not send_button:
                    try:
                        send_button_xpath = "//*[contains(text(), 'Send')]"
                        elements = self.driver.find_elements(By.XPATH, send_button_xpath)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                send_button = element
                                logger.info(f"Found send button with generic text search: {element.tag_name}")
                                break
                    except Exception as e:
                        logger.debug(f"Could not find send button with generic text search: {e}")

                # 6. Last resort: use JavaScript to find the button
                if not send_button:
                    logger.info("Trying JavaScript to find send button...")
                    try:
                        send_button = self.driver.execute_script("""
                            // Try to find elements with 'Send' text
                            const elements = Array.from(document.querySelectorAll('*'));
                            for (const element of elements) {
                                if (element.textContent.includes('Send') &&
                                    (element.tagName === 'BUTTON' || element.getAttribute('role') === 'button') &&
                                    element.offsetWidth > 0 &&
                                    element.offsetHeight > 0) {
                                    return element;
                                }
                            }
                            return null;
                        """)
                        if send_button:
                            logger.info("Found send button using JavaScript")
                    except Exception as e:
                        logger.debug(f"Could not find send button with JavaScript: {e}")

                # Take a screenshot of the current state
                self.driver.save_screenshot("before_send_button_click_inbox.png")

                # Click the send button if found
                if send_button:
                    logger.info("Clicking send button...")
                    try:
                        # Try multiple click methods
                        try:
                            # First try regular click
                            send_button.click()
                            logger.info("Regular click on send button successful")
                        except Exception as click_error:
                            logger.info(f"Regular click failed: {click_error}, trying JavaScript click")
                            self.driver.execute_script("arguments[0].click();", send_button)
                            logger.info("JavaScript click on send button successful")
                    except Exception as e:
                        logger.error(f"Failed to click send button: {e}")
                        raise
                else:
                    logger.error("Could not find send button with any method")
                    screenshot_filename = self._get_screenshot_filename("send_button_not_found_inbox")
                    self.driver.save_screenshot(screenshot_filename)
                    raise Exception("Send button not found")

                # Wait a moment to ensure the message is sent
                time.sleep(2)

                # Take a screenshot after sending
                screenshot_filename = self._get_screenshot_filename("after_send")
                self.driver.save_screenshot(screenshot_filename)

                logger.info(f"Message sent to {recipient_username} successfully!")
                return True
            except TimeoutException:
                logger.error("Could not find message input field")
                screenshot_filename = self._get_screenshot_filename("message_input_not_found")
                self.driver.save_screenshot(screenshot_filename)
                return False

        except TimeoutException as e:
            logger.error(f"Timeout during message sending: {e}")
            screenshot_filename = self._get_screenshot_filename("timeout_error")
            self.driver.save_screenshot(screenshot_filename)
            return False
        except Exception as e:
            logger.error(f"Error during message sending: {e}")
            screenshot_filename = self._get_screenshot_filename("general_error")
            self.driver.save_screenshot(screenshot_filename)
            return False

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            if self.screenshot_folder:
                logger.info(f"WebDriver closed. Screenshots saved in: {self.screenshot_folder}")
                logger.info(f"Session logs saved in: {self.log_file}")
            else:
                logger.info("WebDriver closed.")
                logger.info(f"Main log file: {self.log_file}")

def load_env_file():
    """Load environment variables from .env file"""
    # Try to load .env file
    env_loaded = load_dotenv()

    if not env_loaded:
        print("Warning: .env file not found or could not be loaded.")
        print("Creating .env file from .env.example...")

        # Check if .env.example exists
        if os.path.exists(".env.example"):
            # Copy .env.example to .env
            with open(".env.example", "r") as example_file:
                example_content = example_file.read()

            with open(".env", "w") as env_file:
                env_file.write(example_content)

            print(".env file created. Please edit it with your credentials and run the script again.")
            return False
        else:
            print("Error: .env.example file not found.")
            print("Please create a .env file with the following variables:")
            print("INSTAGRAM_USERNAME=your_username")
            print("INSTAGRAM_PASSWORD=your_password")
            print("DEFAULT_RECIPIENT=recipient_username (optional)")
            print("DEFAULT_MESSAGE=your_message (optional)")
            print("HEADLESS=true/false (optional)")
            return False

    return True

def main():
    """Main function to run the Instagram Message Sender"""
    print("\n===== Instagram Message Sender =====\n")
    print("This tool allows you to send direct messages to Instagram users.")
    print("Note: Using automation tools with Instagram may violate their terms of service.")
    print("Use at your own risk and responsibility.\n")

    # Load environment variables
    if not load_env_file():
        print("\nPlease set up your .env file and run the script again.")
        sys.exit(1)

    # Get Instagram credentials from environment variables
    instagram_username = os.getenv("INSTAGRAM_USERNAME")
    instagram_password = os.getenv("INSTAGRAM_PASSWORD")

    # Check if credentials are provided
    if not instagram_username or not instagram_password:
        print("Error: Instagram credentials not found in .env file.")
        print("Please make sure INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD are set in your .env file.")
        sys.exit(1)

    # Get recipient username from environment variables or user input
    recipient_username = os.getenv("DEFAULT_RECIPIENT")
    if not recipient_username:
        recipient_username = input("Enter recipient's Instagram username: ")
    else:
        print(f"Using default recipient: {recipient_username}")
        change_recipient = input("Do you want to use a different recipient? (y/n, default: n): ").lower()
        if change_recipient == 'y':
            recipient_username = input("Enter recipient's Instagram username: ")

    # Get message from environment variables or user input
    default_message = os.getenv("DEFAULT_MESSAGE")
    if not default_message:
        # Get message with support for multi-line input
        print("\nEnter your message (type 'END' on a new line when finished):")
        message_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            message_lines.append(line)
        message = "\n".join(message_lines)
    else:
        print(f"\nUsing default message: {default_message}")
        change_message = input("Do you want to use a different message? (y/n, default: n): ").lower()
        if change_message == 'y':
            print("\nEnter your message (type 'END' on a new line when finished):")
            message_lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                message_lines.append(line)
            message = "\n".join(message_lines)
        else:
            message = default_message

    # Get headless mode from environment variables or user input
    headless_env = os.getenv("HEADLESS", "false").lower()
    headless = headless_env in ("true", "yes", "1", "t", "y")

    print(f"\nRunning in {'headless' if headless else 'visible'} mode")
    change_headless = input("Do you want to change this? (y/n, default: n): ").lower()
    if change_headless == 'y':
        headless_input = input("Run in headless mode? (y/n): ").lower()
        headless = headless_input == 'y'

    print("\nInitializing Instagram Message Sender...")

    # Create Instagram Message Sender instance
    sender = InstagramMessageSender(headless=headless)

    try:
        # Login to Instagram
        print("\nAttempting to log in to Instagram...")
        if sender.login(instagram_username, instagram_password):
            print("\nLogin successful!")

            # Send message
            print(f"\nAttempting to send message to {recipient_username}...")
            if sender.send_message(recipient_username, message):
                print(f"\nMessage sent to {recipient_username} successfully!")
                if sender.screenshot_folder:
                    print(f"\nScreenshots have been saved to: {sender.screenshot_folder}")
                    print(f"Session logs have been saved to: {sender.log_file}")
                else:
                    print("\nScreenshots have been saved to the screenshots directory.")
                    print(f"Logs have been saved to: {sender.log_file}")
            else:
                print(f"\nFailed to send message to {recipient_username}.")
                if sender.screenshot_folder:
                    print(f"Check the logs and screenshots in: {sender.screenshot_folder}")
                    print(f"Session log file: {sender.log_file}")
                else:
                    print("Check the logs and screenshots for more details.")
                    print(f"Main log file: {sender.log_file}")
        else:
            print("\nLogin failed. Please check your credentials and try again.")
            print("If you're seeing security verification requests, you may need to log in manually first.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Close the WebDriver
        print("\nClosing the browser...")
        sender.close()
        print("\nDone! Thank you for using Instagram Message Sender.")

if __name__ == "__main__":
    main()
