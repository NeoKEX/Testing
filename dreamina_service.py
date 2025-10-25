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
        self.cookies = self.load_cookies()
        self.driver = None
        
    def load_cookies(self):
        cookie_file = 'account.json'
        if not os.path.exists(cookie_file):
            raise FileNotFoundError(
                f"{cookie_file} not found. Please create it using account.json.example as template"
            )
        
        with open(cookie_file, 'r') as f:
            data = json.load(f)
            
            # Handle both formats: direct array or object with 'cookies' property
            if isinstance(data, list):
                cookies = data
            elif isinstance(data, dict):
                cookies = data.get('cookies', [])
            else:
                raise ValueError("Invalid account.json format")
            
        if not cookies:
            raise ValueError("No cookies found in account.json")
        
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
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
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
        time.sleep(2)
        
        for cookie in self.cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Warning: Failed to add cookie {cookie.get('name')}: {str(e)}")
        
        driver.refresh()
        time.sleep(3)
    
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
            
            driver.get(f"{self.base_url}/ai-tool/generate")
            time.sleep(5)
            
            # Find and fill prompt input with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    prompt_input = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='prompt' i], textarea, input[type='text']"))
                    )
                    time.sleep(1)
                    
                    # Clear and enter text with retry
                    def enter_prompt():
                        prompt_input.click()
                        prompt_input.clear()
                        time.sleep(0.5)
                        prompt_input.send_keys(prompt)
                        time.sleep(0.5)
                        return True
                    
                    self._retry_on_stale(enter_prompt)
                    break
                except (StaleElementReferenceException, TimeoutException) as e:
                    if attempt == max_retries - 1:
                        return {
                            'status': 'error',
                            'message': f'Failed to find prompt input after {max_retries} attempts: {str(e)}. Please check if authentication is valid.'
                        }
                    time.sleep(2)
            
            # Click generate button with retry logic
            time.sleep(2)
            for attempt in range(max_retries):
                try:
                    generate_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'GENERATE', 'generate'), 'generate') or contains(translate(text(), 'CREATE', 'create'), 'create')]"))
                    )
                    time.sleep(1)
                    
                    def click_button():
                        generate_button.click()
                        return True
                    
                    self._retry_on_stale(click_button)
                    break
                except (StaleElementReferenceException, TimeoutException) as e:
                    if attempt == max_retries - 1:
                        return {
                            'status': 'error',
                            'message': f'Failed to click generate button after {max_retries} attempts: {str(e)}'
                        }
                    time.sleep(2)
            
            # Wait for image generation
            print("Waiting for image generation...")
            time.sleep(15)
            
            # Retry finding generated images
            for attempt in range(max_retries):
                try:
                    images = driver.find_elements(By.TAG_NAME, "img")
                    image_urls = []
                    for img in images:
                        try:
                            src = img.get_attribute('src')
                            if src and ('ibyteimg.com' in src or 'bytedance' in src or 'capcut' in src):
                                if src not in image_urls:
                                    image_urls.append(src)
                        except StaleElementReferenceException:
                            continue
                    
                    if image_urls:
                        return {
                            'status': 'success',
                            'prompt': prompt,
                            'model': model,
                            'aspect_ratio': aspect_ratio,
                            'quality': quality,
                            'images': image_urls,
                            'count': len(image_urls)
                        }
                    elif attempt < max_retries - 1:
                        time.sleep(5)
                    else:
                        return {
                            'status': 'error',
                            'message': 'No generated images found. Generation may still be in progress or failed.'
                        }
                except Exception as e:
                    if attempt == max_retries - 1:
                        return {
                            'status': 'error',
                            'message': f'Failed to retrieve generated images: {str(e)}'
                        }
                    time.sleep(5)
                
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
