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
        self.driver = None
        self.is_authenticated = False
        
        # Verify we have credentials
        self.email = os.environ.get('DREAMINA_EMAIL')
        self.password = os.environ.get('DREAMINA_PASSWORD')
        
        if not self.email or not self.password:
            raise ValueError(
                "DREAMINA_EMAIL and DREAMINA_PASSWORD environment variables are required. "
                "Please set them in your Replit Secrets."
            )
        
    def ensure_authenticated(self):
        """Ensure the user is authenticated, performing login if necessary"""
        if self.is_authenticated:
            return True
        
        print("Performing login...")
        success = self.login_with_email(self.email, self.password)
        if success:
            self.is_authenticated = True
            print("✓ Authentication successful")
        else:
            print("✗ Authentication failed")
        return success
    
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
        
        # Note: We used to block image loading to save bandwidth, but this prevents
        # Dreamina from populating generated image URLs in the src attributes.
        # Memory tradeoff is acceptable for functional image generation.
        
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
        env_chromedriver = os.environ.get('CHROMEDRIVER_PATH')
        if env_chromedriver and os.path.exists(env_chromedriver):
            chromedriver_path = env_chromedriver
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
    
    
    def login_with_email(self, email, password):
        """Perform automated login using email and password"""
        try:
            driver = self.init_driver()
            print("=" * 60)
            print("STARTING AUTOMATED EMAIL LOGIN")
            print(f"Email: {email[:3]}...{email[-10:]}")  # Show partial email for debugging
            print("=" * 60)
            
            # Navigate to Dreamina homepage
            print(f"Navigating to: {self.base_url}")
            driver.get(self.base_url)
            print(f"Current URL after navigation: {driver.current_url}")
            print(f"Page title: {driver.title}")
            
            # Save initial screenshot
            try:
                driver.save_screenshot('/tmp/login_step1_homepage.png')
                print("✓ Saved screenshot: /tmp/login_step1_homepage.png")
            except Exception as e:
                print(f"Could not save screenshot: {e}")
            
            time.sleep(3)
            
            # Look for and click the "Continue with email" button
            print("\nStep 1: Looking for 'Continue with email' button...")
            email_button_found = False
            email_button_selectors = [
                (By.XPATH, "//button[contains(text(), 'Continue with email')]"),
                (By.XPATH, "//*[contains(text(), 'Continue with email')]"),
                (By.XPATH, "//div[contains(text(), 'Continue with email')]"),
                (By.CSS_SELECTOR, "button[class*='email']"),
            ]
            
            for i, (selector_type, selector_value) in enumerate(email_button_selectors):
                try:
                    print(f"  Trying selector {i+1}/{len(email_button_selectors)}: {selector_value}")
                    email_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    driver.execute_script("arguments[0].click();", email_btn)
                    print("  ✓ Clicked 'Continue with email' button")
                    email_button_found = True
                    
                    # Save screenshot after clicking
                    try:
                        driver.save_screenshot('/tmp/login_step2_after_email_button.png')
                        print("  ✓ Saved screenshot: /tmp/login_step2_after_email_button.png")
                    except:
                        pass
                    
                    time.sleep(2)
                    break
                except (TimeoutException, Exception) as e:
                    print(f"  ✗ Selector failed: {str(e)[:50]}")
                    continue
            
            if not email_button_found:
                print("  ⚠ Could not find 'Continue with email' button")
                print("  → Trying to find email input directly...")
                # Save screenshot for debugging
                try:
                    driver.save_screenshot('/tmp/login_step2_no_email_button.png')
                    print("  ✓ Saved screenshot: /tmp/login_step2_no_email_button.png")
                except:
                    pass
            
            # Enter email
            print("\nStep 2: Entering email...")
            email_input_found = False
            email_selectors = [
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='email' i]"),
                (By.CSS_SELECTOR, "input[name='email']"),
                (By.XPATH, "//input[@type='text' and contains(@placeholder, 'email')]"),
                (By.CSS_SELECTOR, "input[type='text']"),
            ]
            
            for i, (selector_type, selector_value) in enumerate(email_selectors):
                try:
                    print(f"  Trying selector {i+1}/{len(email_selectors)}: {selector_value}")
                    email_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    email_input.clear()
                    email_input.send_keys(email)
                    print(f"  ✓ Email entered: {email[:3]}...{email[-10:]}")
                    email_input_found = True
                    
                    # Save screenshot after entering email
                    try:
                        driver.save_screenshot('/tmp/login_step3_email_entered.png')
                        print("  ✓ Saved screenshot: /tmp/login_step3_email_entered.png")
                    except:
                        pass
                    
                    time.sleep(1)
                    break
                except (TimeoutException, Exception) as e:
                    print(f"  ✗ Selector failed: {str(e)[:50]}")
                    continue
            
            if not email_input_found:
                print("  ✗ FAILED: Could not find email input field")
                driver.save_screenshot('/tmp/login_error_no_email_input.png')
                raise Exception("Could not find email input field. Screenshot saved to /tmp/login_error_no_email_input.png")
            
            # Enter password
            print("\nStep 3: Entering password...")
            password_input_found = False
            password_selectors = [
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[placeholder*='password' i]"),
                (By.CSS_SELECTOR, "input[name='password']"),
            ]
            
            for i, (selector_type, selector_value) in enumerate(password_selectors):
                try:
                    print(f"  Trying selector {i+1}/{len(password_selectors)}: {selector_value}")
                    password_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    password_input.clear()
                    password_input.send_keys(password)
                    print("  ✓ Password entered (hidden)")
                    password_input_found = True
                    
                    # Save screenshot after entering password
                    try:
                        driver.save_screenshot('/tmp/login_step4_password_entered.png')
                        print("  ✓ Saved screenshot: /tmp/login_step4_password_entered.png")
                    except:
                        pass
                    
                    time.sleep(1)
                    break
                except (TimeoutException, Exception) as e:
                    print(f"  ✗ Selector failed: {str(e)[:50]}")
                    continue
            
            if not password_input_found:
                print("  ✗ FAILED: Could not find password input field")
                driver.save_screenshot('/tmp/login_error_no_password_input.png')
                raise Exception("Could not find password input field. Screenshot saved to /tmp/login_error_no_password_input.png")
            
            # Click login/submit button
            print("\nStep 4: Clicking login button...")
            login_button_found = False
            login_button_selectors = [
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button[class*='submit']"),
                (By.CSS_SELECTOR, "button[class*='login']"),
            ]
            
            for i, (selector_type, selector_value) in enumerate(login_button_selectors):
                try:
                    print(f"  Trying selector {i+1}/{len(login_button_selectors)}: {selector_value}")
                    login_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    driver.execute_script("arguments[0].click();", login_btn)
                    print("  ✓ Login button clicked")
                    login_button_found = True
                    
                    # Save screenshot after clicking
                    try:
                        driver.save_screenshot('/tmp/login_step5_button_clicked.png')
                        print("  ✓ Saved screenshot: /tmp/login_step5_button_clicked.png")
                    except:
                        pass
                    
                    break
                except (TimeoutException, Exception) as e:
                    print(f"  ✗ Selector failed: {str(e)[:50]}")
                    continue
            
            if not login_button_found:
                print("  ✗ FAILED: Could not find or click login button")
                driver.save_screenshot('/tmp/login_error_no_login_button.png')
                raise Exception("Could not find or click login button. Screenshot saved to /tmp/login_error_no_login_button.png")
            
            # Wait for login to complete
            print("\nStep 5: Waiting for login to complete...")
            time.sleep(5)
            
            # Save screenshot after waiting
            try:
                driver.save_screenshot('/tmp/login_step6_after_wait.png')
                print("✓ Saved screenshot: /tmp/login_step6_after_wait.png")
            except:
                pass
            
            # Check if login was successful
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            print(f"Current URL after login: {current_url}")
            print(f"Page title: {driver.title}")
            
            # Check for login-related keywords
            login_keywords = ['sign in', 'log in', 'continue with google', 'continue with email']
            found_keywords = [kw for kw in login_keywords if kw in page_source]
            
            # Check if login was successful
            if not found_keywords:
                print("=" * 60)
                print("✓✓✓ LOGIN SUCCESSFUL! ✓✓✓")
                print("=" * 60)
                return True
            else:
                # Save debug screenshot
                print("=" * 60)
                print("✗✗✗ LOGIN FAILED ✗✗✗")
                print(f"Found login keywords: {found_keywords}")
                print("=" * 60)
                try:
                    driver.save_screenshot('/tmp/login_failed.png')
                    print("Debug screenshot saved to /tmp/login_failed.png")
                    # Also save HTML
                    with open('/tmp/login_failed.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print("Debug HTML saved to /tmp/login_failed.html")
                except Exception as e:
                    print(f"Could not save debug files: {e}")
                return False
                
        except Exception as e:
            print("=" * 60)
            print("✗✗✗ LOGIN EXCEPTION ✗✗✗")
            print(f"Error: {str(e)}")
            print("=" * 60)
            # Save debug screenshot on error
            try:
                if self.driver:
                    self.driver.save_screenshot('/tmp/login_exception.png')
                    print("Debug screenshot saved to /tmp/login_exception.png")
                    # Also save HTML
                    with open('/tmp/login_exception.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print("Debug HTML saved to /tmp/login_exception.html")
            except Exception as save_err:
                print(f"Could not save debug files: {save_err}")
            raise  # Re-raise the exception so we can see it in logs
    
    def check_authentication(self):
        """Check if authenticated, and perform login if needed"""
        try:
            return self.ensure_authenticated()
        except Exception as e:
            print(f"Authentication check failed with error: {str(e)}")
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
            # Ensure we're authenticated before generating
            if not self.ensure_authenticated():
                return {
                    'status': 'error',
                    'message': 'Authentication failed. Cannot generate image.'
                }
            
            driver = self.init_driver()
            
            # Navigate to home page
            driver.get(self.home_url)
            time.sleep(2)
            
            print(f"Navigated to: {driver.current_url}")
            print(f"Page title: {driver.title}")
            
            # Ensure we're on the AI Image section
            try:
                # Try to click "AI Image" button if visible (to ensure correct section is active)
                ai_image_selectors = [
                    (By.XPATH, "//button[contains(text(), 'AI Image')]"),
                    (By.XPATH, "//*[contains(text(), 'AI Image')]"),
                ]
                for selector_type, selector_value in ai_image_selectors:
                    try:
                        ai_image_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((selector_type, selector_value))
                        )
                        driver.execute_script("arguments[0].click();", ai_image_btn)
                        print("Clicked 'AI Image' section")
                        time.sleep(0.5)
                        break
                    except:
                        continue
            except Exception as e:
                # Not critical if this fails - the page might already be on the right section
                print(f"Note: Could not click AI Image section (might already be active): {str(e)}")
            
            # Find and fill prompt input - optimized with specific selectors first
            prompt_entered = False
            input_selectors = [
                (By.CSS_SELECTOR, "textarea"),
                (By.CSS_SELECTOR, "input[type='text']"),
            ]
            
            for selector_type, selector_value in input_selectors:
                try:
                    prompt_input = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    prompt_input.click()
                    time.sleep(0.1)
                    prompt_input.clear()
                    prompt_input.send_keys(prompt)
                    prompt_entered = True
                    print(f"Prompt entered using {selector_type}")
                    break
                except (StaleElementReferenceException, TimeoutException, Exception) as e:
                    continue
            
            if not prompt_entered:
                return {
                    'status': 'error',
                    'message': 'Failed to enter prompt. Please check if authentication is valid.'
                }
            
            # Wait for Generate button to become active after entering prompt
            # The button may need time to enable after prompt is entered
            print("Waiting for Generate button to become available...")
            time.sleep(1.5)  # Give page time to fully load and enable button after entering prompt
            button_clicked = False
            
            # Updated button selectors for current Dreamina page (October 2025)
            button_selectors = [
                # Try standard Generate button first
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'generate')]"),
                (By.CSS_SELECTOR, "button[class*='generate']"),
                (By.CSS_SELECTOR, "button[class*='Generate']"),
                # Try blue primary button (common pattern for Generate CTA)
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(@class, 'primary')]"),
                (By.XPATH, "//button[contains(@class, 'btn-primary')]"),
                # Fallback to any clickable button in workspace area
                (By.CSS_SELECTOR, "button[class*='submit']"),
            ]
            
            for selector_type, selector_value in button_selectors:
                try:
                    generate_button = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    # Scroll button into view first
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", generate_button)
                    time.sleep(0.3)
                    # Use JavaScript click for reliability
                    driver.execute_script("arguments[0].click();", generate_button)
                    button_clicked = True
                    print(f"✓ Button clicked using selector: {selector_value}")
                    break
                except (StaleElementReferenceException, TimeoutException, Exception) as e:
                    continue
            
            if not button_clicked:
                # Enhanced debug: Save screenshot and button info
                try:
                    # Take screenshot for debugging
                    screenshot_path = '/tmp/dreamina_debug.png'
                    driver.save_screenshot(screenshot_path)
                    print(f"Debug screenshot saved to: {screenshot_path}")
                    
                    # Save page HTML for analysis
                    html_path = '/tmp/dreamina_debug.html'
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"Debug HTML saved to: {html_path}")
                    
                    # Find all buttons and log them
                    all_buttons = driver.find_elements(By.TAG_NAME, "button")
                    button_info = []
                    for i, btn in enumerate(all_buttons[:15]):  # Increased limit to 15
                        try:
                            text = btn.text[:80] if btn.text else "No text"
                            btn_class = btn.get_attribute('class')
                            classes = btn_class[:80] if btn_class else "No class"
                            btn_type = btn.get_attribute('type') or "no type"
                            visible = btn.is_displayed()
                            button_info.append(f"[{i}] Text:'{text}' | Class:'{classes}' | Type:'{btn_type}' | Visible:{visible}")
                        except Exception as btn_err:
                            button_info.append(f"[{i}] Error reading button: {str(btn_err)}")
                    
                    debug_msg = "\n".join(button_info) if button_info else "No buttons found"
                    print(f"Available buttons ({len(all_buttons)} total):\n{debug_msg}")
                except Exception as debug_err:
                    print(f"Debug error: {str(debug_err)}")
                
                return {
                    'status': 'error',
                    'message': 'Failed to click generate button. Debug files saved to /tmp/dreamina_debug.png and /tmp/dreamina_debug.html. Check logs for button details.'
                }
            
            # Capture existing images BEFORE generation
            print("Capturing existing images...")
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
                print(f"Found {len(existing_image_urls)} existing images")
            except Exception as e:
                print(f"Warning: Could not capture existing images: {str(e)}")
            
            # Optimized waiting for image generation
            print("Waiting for generation...")
            max_wait_time = 35  # Reduced from 45s
            wait_interval = 2   # Check every 2 seconds (reduced from 4s)
            total_waited = 0
            
            # Initial wait for generation to start
            time.sleep(3)  # Reduced from 5s
            total_waited += 3
            
            new_image_urls = []
            while total_waited < max_wait_time:
                try:
                    current_images = driver.find_elements(By.TAG_NAME, "img")
                    new_image_urls = []
                    
                    for img in current_images:
                        try:
                            src = img.get_attribute('src')
                            if src and ('ibyteimg.com' in src or 'bytedance' in src or 'capcut' in src):
                                if src not in existing_image_urls:
                                    new_image_urls.append(src)
                        except:
                            continue
                    
                    print(f"[{total_waited}s] New images: {len(new_image_urls)}")
                    
                    # Dreamina generates 4 images
                    if len(new_image_urls) >= 4:
                        print(f"✓ Generated {len(new_image_urls)} images in {total_waited}s")
                        break
                    
                    # Continue waiting
                    time.sleep(wait_interval)
                    total_waited += wait_interval
                    
                except Exception as e:
                    print(f"Check error: {str(e)}")
                    time.sleep(wait_interval)
                    total_waited += wait_interval
            
            # Return results - require at least 4 images for success
            if len(new_image_urls) >= 4:
                print(f"✓ Success: {len(new_image_urls)} images generated in {total_waited}s")
                return {
                    'status': 'success',
                    'prompt': prompt,
                    'model': model,
                    'aspect_ratio': aspect_ratio,
                    'quality': quality,
                    'images': new_image_urls,
                    'count': len(new_image_urls),
                    'generation_time': f"{total_waited}s"
                }
            else:
                # Image detection failed - save debug info
                try:
                    screenshot_path = '/tmp/dreamina_debug.png'
                    driver.save_screenshot(screenshot_path)
                    print(f"Debug screenshot saved to: {screenshot_path}")
                    
                    html_path = '/tmp/dreamina_debug.html'
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"Debug HTML saved to: {html_path}")
                    
                    # Log all images found
                    all_imgs = driver.find_elements(By.TAG_NAME, "img")
                    print(f"Total <img> elements found: {len(all_imgs)}")
                    print(f"Existing images (before generation): {len(existing_image_urls)}")
                    print(f"New images detected: {len(new_image_urls)}")
                    if new_image_urls:
                        print(f"New image URLs: {new_image_urls[:3]}...")  # Show first 3
                except Exception as debug_err:
                    print(f"Debug error: {str(debug_err)}")
                
                if new_image_urls:
                    return {
                        'status': 'error',
                        'message': f'Only {len(new_image_urls)} images generated (expected 4). Generation may have been incomplete. Debug files saved to /tmp/dreamina_debug.png'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'No images generated after {total_waited}s. This could be: 1) Authentication failed/expired, 2) Generation still in progress, 3) Page structure changed. Debug files saved to /tmp/dreamina_debug.png and /tmp/dreamina_debug.html'
                    }
                
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
