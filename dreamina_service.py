import json
import os
import time
import glob
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class DreaminaService:
    def __init__(self):
        self.base_url = "https://dreamina.capcut.com"
        self.home_url = "https://dreamina.capcut.com/ai-tool/home/"
        self.cookies = self.load_cookies()
        self.driver = None
        
    def load_cookies(self):
        # Try to load from file first
        cookie_file = 'account.json'
        if os.path.exists(cookie_file):
            with open(cookie_file, 'r') as f:
                data = json.load(f)
        # If file doesn't exist, try environment variables (for Fly.io deployment)
        elif os.environ.get('ACCOUNT_JSON'):
            data = json.loads(os.environ.get('ACCOUNT_JSON'))
        elif os.environ.get('ACCOUNT_JSON_BASE64'):
            import base64
            decoded = base64.b64decode(os.environ.get('ACCOUNT_JSON_BASE64')).decode('utf-8')
            data = json.loads(decoded)
        else:
            raise FileNotFoundError(
                f"{cookie_file} not found and ACCOUNT_JSON environment variable not set. "
                "Please create account.json using account.json.example as template or set ACCOUNT_JSON secret."
            )
        
        # Handle both formats: direct array or object with 'cookies' property
        if isinstance(data, list):
            cookies = data
        elif isinstance(data, dict):
            cookies = data.get('cookies', [])
        else:
            raise ValueError("Invalid account.json format")
        
        if not cookies:
            raise ValueError("No cookies found in account data")
        
        for cookie in cookies:
            if 'name' not in cookie or 'value' not in cookie:
                raise ValueError("Invalid cookie format: each cookie must have 'name' and 'value' fields")
        
        return cookies
    
    def init_driver(self):
        if self.driver is not None:
            return self.driver
            
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280,720')  # Smaller window for less memory
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Safe memory optimization flags
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-hang-monitor')
        chrome_options.add_argument('--disable-prompt-on-repost')
        chrome_options.add_argument('--disable-domain-reliability')
        chrome_options.add_argument('--disable-client-side-phishing-detection')
        
        # Set preferences to block actual image loading while keeping img elements in DOM
        prefs = {
            "profile.managed_default_content_settings.images": 2  # Block images from loading
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Try to find Chrome/Chromium binary in multiple locations
        chrome_found = False
        
        # 1. Try Nix store (Replit environment)
        chromium_paths = sorted(glob.glob('/nix/store/*-chromium-*/bin/chromium'))
        if chromium_paths:
            chrome_options.binary_location = chromium_paths[-1]
            print(f"Using Chromium from Nix: {chromium_paths[-1]}")
            chrome_found = True
        else:
            # 2. Try standard Linux locations (Render/production)
            standard_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/opt/google/chrome/chrome',
                '/opt/google/chrome/google-chrome'
            ]
            for path in standard_paths:
                if os.path.exists(path):
                    chrome_options.binary_location = path
                    print(f"Using Chrome from standard location: {path}")
                    chrome_found = True
                    break
        
        if not chrome_found:
            print("Chrome/Chromium binary not found in standard locations, using default")
            
        # Find chromedriver binary
        chromedriver_path = None
        
        # 1. Check environment variable (Docker/Render)
        if os.environ.get('CHROMEDRIVER_PATH') and os.path.exists(os.environ.get('CHROMEDRIVER_PATH')):
            chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
            print(f"Using ChromeDriver from environment: {chromedriver_path}")
        # 2. Check Nix store (Replit)
        else:
            chromedriver_paths = sorted(glob.glob('/nix/store/*-chromedriver-*/bin/chromedriver'))
            if chromedriver_paths:
                chromedriver_path = chromedriver_paths[-1]
                print(f"Using ChromeDriver from Nix: {chromedriver_path}")
            # 3. Check standard locations
            elif os.path.exists('/usr/local/bin/chromedriver'):
                chromedriver_path = '/usr/local/bin/chromedriver'
                print(f"Using ChromeDriver from /usr/local/bin")
            elif os.path.exists('/usr/bin/chromedriver'):
                chromedriver_path = '/usr/bin/chromedriver'
                print(f"Using ChromeDriver from /usr/bin")
        
        try:
            if chromedriver_path:
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Fallback to webdriver-manager
                print("Using webdriver-manager for ChromeDriver")
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome driver: {str(e)}")
        
        return self.driver
    
    def apply_cookies(self):
        driver = self.init_driver()
        driver.get(self.base_url)
        time.sleep(1)
        
        for cookie in self.cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Warning: Failed to add cookie {cookie.get('name')}: {str(e)}")
        
        driver.refresh()
        time.sleep(2)
    
    def check_authentication(self):
        try:
            driver = self.init_driver()
            self.apply_cookies()
            driver.get(f"{self.base_url}/ai-tool/generate")
            time.sleep(5)
            
            page_source = driver.page_source.lower()
            if 'sign in' in page_source or 'log in' in page_source or 'login' in page_source:
                return False
            return True
        except Exception as e:
            print(f"Authentication check failed: {str(e)}")
            return False
    
    def _retry_on_stale(self, func, max_retries=3):
        """Retry function on stale element exception"""
        for attempt in range(max_retries):
            try:
                return func()
            except StaleElementReferenceException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
        return None
    
    def generate_image(self, prompt, aspect_ratio='1:1', quality='high', model='image_4.0'):
        try:
            driver = self.init_driver()
            self.apply_cookies()
            
            # Navigate to home page first
            driver.get(self.home_url)
            time.sleep(3)
            
            print(f"Navigated to: {driver.current_url}")
            print(f"Page title: {driver.title}")
            
            # Find and fill prompt input with retry logic - try multiple selectors
            max_retries = 3
            prompt_entered = False
            
            # List of input selectors to try
            input_selectors = [
                (By.CSS_SELECTOR, "textarea[placeholder*='prompt' i]"),
                (By.CSS_SELECTOR, "textarea[placeholder*='Prompt' i]"),
                (By.CSS_SELECTOR, "textarea"),
                (By.CSS_SELECTOR, "input[type='text'][placeholder*='prompt' i]"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.XPATH, "//textarea[contains(@placeholder, 'prompt') or contains(@placeholder, 'Prompt')]"),
                (By.XPATH, "//input[@type='text' and (contains(@placeholder, 'prompt') or contains(@placeholder, 'Prompt'))]"),
            ]
            
            for attempt in range(max_retries):
                for selector_type, selector_value in input_selectors:
                    try:
                        # Refetch element on each attempt to avoid stale element
                        def enter_prompt():
                            prompt_input = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            time.sleep(0.3)
                            prompt_input.click()
                            time.sleep(0.2)
                            prompt_input.clear()
                            time.sleep(0.2)
                            prompt_input.send_keys(prompt)
                            time.sleep(0.3)
                            return True
                        
                        self._retry_on_stale(enter_prompt)
                        prompt_entered = True
                        print(f"Successfully entered prompt using selector: {selector_value}")
                        break
                    except (StaleElementReferenceException, TimeoutException):
                        continue
                    except Exception as e:
                        continue
                
                if prompt_entered:
                    break
                    
                if attempt < max_retries - 1:
                    print(f"Prompt input attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
            
            if not prompt_entered:
                return {
                    'status': 'error',
                    'message': 'Failed to enter prompt. Please check if authentication is valid.'
                }
            
            # Click generate button with retry logic - try multiple selectors
            time.sleep(1)
            button_clicked = False
            
            # List of button selectors to try (in order of preference)
            # Based on Dreamina's actual page structure
            button_selectors = [
                # Look for "See results" or similar result/generate buttons
                (By.XPATH, "//button[contains(., 'See results')]"),
                (By.XPATH, "//button[contains(., 'results')]"),
                (By.XPATH, "//button[contains(., 'Generate')]"),
                (By.XPATH, "//button[contains(., 'generate')]"),
                (By.XPATH, "//button[contains(translate(., 'GENERATE', 'generate'), 'generate')]"),
                (By.XPATH, "//button[contains(translate(., 'CREATE', 'create'), 'create')]"),
                # Try by common class patterns
                (By.CSS_SELECTOR, "button[class*='generate']"),
                (By.CSS_SELECTOR, "button[class*='submit']"),
                (By.CSS_SELECTOR, "button[class*='create']"),
                (By.CSS_SELECTOR, "button[class*='result']"),
                # Try by type
                (By.XPATH, "//button[@type='submit']"),
                # Try any button with generate-related attributes
                (By.XPATH, "//button[contains(@class, 'generate') or contains(@id, 'generate')]"),
                # Fallback: any visible primary-looking button
                (By.CSS_SELECTOR, "button[class*='primary']"),
            ]
            
            for attempt in range(max_retries):
                for selector_type, selector_value in button_selectors:
                    try:
                        def click_button():
                            generate_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((selector_type, selector_value))
                            )
                            time.sleep(0.3)
                            # Try clicking with JavaScript as backup
                            try:
                                generate_button.click()
                            except:
                                driver.execute_script("arguments[0].click();", generate_button)
                            return True
                        
                        self._retry_on_stale(click_button)
                        button_clicked = True
                        print(f"Successfully clicked button using selector: {selector_value}")
                        break
                    except (StaleElementReferenceException, TimeoutException):
                        continue
                    except Exception as e:
                        print(f"Selector {selector_value} failed: {str(e)[:100]}")
                        continue
                
                if button_clicked:
                    break
                    
                if attempt < max_retries - 1:
                    print(f"Button click attempt {attempt + 1} failed, retrying...")
                    time.sleep(3)
            
            if not button_clicked:
                # Debug: Try to find all buttons and log them
                try:
                    all_buttons = driver.find_elements(By.TAG_NAME, "button")
                    button_info = []
                    for btn in all_buttons[:10]:  # Limit to first 10
                        try:
                            text = btn.text[:50] if btn.text else "No text"
                            classes = btn.get_attribute('class')[:50] if btn.get_attribute('class') else "No class"
                            button_info.append(f"Button: '{text}' | Class: '{classes}'")
                        except:
                            continue
                    debug_msg = " | ".join(button_info) if button_info else "No buttons found"
                    print(f"Available buttons: {debug_msg}")
                except:
                    pass
                
                return {
                    'status': 'error',
                    'message': 'Failed to click generate button after trying multiple selectors. The page structure may have changed or authentication failed.'
                }
            
            # Capture existing images BEFORE generation to filter them out later
            print("Capturing existing images before generation...")
            existing_image_urls = set()
            try:
                existing_images = driver.find_elements(By.TAG_NAME, "img")
                for img in existing_images:
                    try:
                        src = img.get_attribute('src')
                        if src and ('ibyteimg.com' in src or 'bytedance' in src or 'capcut' in src):
                            existing_image_urls.add(src)
                    except:
                        continue
                print(f"Found {len(existing_image_urls)} existing images on page")
            except Exception as e:
                print(f"Warning: Could not capture existing images: {str(e)}")
            
            # Wait for image generation with incremental checks
            print("Waiting for image generation...")
            max_wait_time = 45  # Increased timeout
            wait_interval = 4  # Check every 4 seconds
            total_waited = 0
            new_images_found = False
            
            # Initial longer wait for generation to start
            time.sleep(5)
            total_waited += 5
            
            while total_waited < max_wait_time and not new_images_found:
                # Check if new images have appeared
                try:
                    current_images = driver.find_elements(By.TAG_NAME, "img")
                    all_image_urls = []
                    current_count = 0
                    
                    for img in current_images:
                        try:
                            src = img.get_attribute('src')
                            if src and ('ibyteimg.com' in src or 'bytedance' in src or 'capcut' in src):
                                all_image_urls.append(src)
                                if src not in existing_image_urls:
                                    current_count += 1
                        except:
                            continue
                    
                    print(f"Check at {total_waited}s: Found {len(all_image_urls)} total images, {current_count} new images")
                    
                    if current_count >= 4:
                        new_images_found = True
                        print(f"✓ Found {current_count} new images after {total_waited} seconds")
                        break
                    elif total_waited < max_wait_time:
                        print(f"Waiting for more images... ({total_waited}s)")
                        time.sleep(wait_interval)
                        total_waited += wait_interval
                    else:
                        break
                except Exception as e:
                    print(f"Check failed: {str(e)}")
                    time.sleep(wait_interval)
                    total_waited += wait_interval
            
            # Extract only NEW generated images
            for attempt in range(max_retries):
                try:
                    images = driver.find_elements(By.TAG_NAME, "img")
                    new_image_urls = []
                    for img in images:
                        try:
                            src = img.get_attribute('src')
                            if src and ('ibyteimg.com' in src or 'bytedance' in src or 'capcut' in src):
                                # Only include images that weren't there before
                                if src not in existing_image_urls and src not in new_image_urls:
                                    new_image_urls.append(src)
                        except StaleElementReferenceException:
                            continue
                    
                    if new_image_urls:
                        # Dreamina typically generates 4 images
                        expected_count = 4
                        if len(new_image_urls) < expected_count and attempt < max_retries - 1:
                            print(f"Found only {len(new_image_urls)} images, waiting for more...")
                            time.sleep(3)
                            continue
                        
                        print(f"Successfully extracted {len(new_image_urls)} newly generated images")
                        return {
                            'status': 'success',
                            'prompt': prompt,
                            'model': model,
                            'aspect_ratio': aspect_ratio,
                            'quality': quality,
                            'images': new_image_urls,
                            'count': len(new_image_urls)
                        }
                    elif attempt < max_retries - 1:
                        print(f"No new images found yet, retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(3)
                    else:
                        return {
                            'status': 'error',
                            'message': 'No new generated images found. Generation may have failed or timed out.'
                        }
                except Exception as e:
                    if attempt == max_retries - 1:
                        return {
                            'status': 'error',
                            'message': f'Failed to retrieve generated images: {str(e)}'
                        }
                    time.sleep(3)
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Image generation error: {str(e)}'
            }
    
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def __del__(self):
        self.close()
