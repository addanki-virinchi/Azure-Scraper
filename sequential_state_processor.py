#!/usr/bin/env python3
"""
Enhanced Sequential State Processor - Complete Phase 1 → Phase 2 workflow per state
- Interactive mode selection menu for flexible processing options
- Enhanced pagination handling with results per page optimization
- Smooth scrolling functionality for better page loading
- Robust connection error handling and retry mechanisms
- Maintains ultra-fast performance optimizations
- Resilient to connection issues with automatic recovery
"""

import time
import logging
import os
import glob
import re
import csv
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedStatewiseSchoolScraper:
    """Enhanced scraper with pagination, results per page, and scrolling improvements"""

    def __init__(self):
        # Import and inherit from the original scraper
        from phase1_statewise_scraper import StatewiseSchoolScraper
        self.base_scraper = StatewiseSchoolScraper()

        # Delegate all base functionality to the original scraper
        self.driver = None
        self.current_state = None
        self.current_district = None
        self.state_schools_with_links = {}
        self.state_schools_no_links = {}

        # CSV file management for incremental saving
        self.current_csv_file = None
        self.csv_headers_written = False
        self.total_schools_saved = 0

    def __getattr__(self, name):
        """Delegate all undefined methods to the base scraper"""
        return getattr(self.base_scraper, name)

    def setup_driver(self):
        """Setup driver using base scraper"""
        result = self.base_scraper.setup_driver()
        self.driver = self.base_scraper.driver
        return result

    def navigate_to_portal(self):
        """Navigate to portal using base scraper"""
        return self.base_scraper.navigate_to_portal()

    def extract_states_data(self):
        """Extract states data using base scraper"""
        return self.base_scraper.extract_states_data()

    def select_state(self, state_data):
        """Select state using base scraper"""
        result = self.base_scraper.select_state(state_data)
        self.current_state = self.base_scraper.current_state
        return result

    def extract_districts_data(self):
        """Extract districts data using base scraper"""
        return self.base_scraper.extract_districts_data()

    def select_district(self, district_data):
        """Select district using base scraper"""
        result = self.base_scraper.select_district(district_data)
        self.current_district = self.base_scraper.current_district
        return result

    def enhanced_click_search_button(self):
        """Enhanced search button click with results per page optimization"""
        try:
            # First, click the search button using the base method
            search_success = self.base_scraper.click_search_button()

            if not search_success:
                logger.error("❌ Failed to click search button")
                return False

            # Balanced wait for initial results to load (reliability focused)
            time.sleep(2.5)  # Increased from 1.5s to 2.5s for better reliability

            # Try to set results per page to 100 with verification
            results_per_page_success = self.set_results_per_page_to_100()
            if results_per_page_success:
                logger.info("✅ Successfully set results per page to 100")
                # Reliable wait for page to reload with 100 results per page
                time.sleep(2.5)  # Increased from 1.5s to 2.5s for complete loading

                # Verify that school elements are now available (with reliable timeout)
                self.wait_for_school_elements_to_load()  # Use full method for reliability
            else:
                logger.warning("⚠️ Failed to set results per page to 100 - continuing with default")

            # Scroll to bottom of page to ensure all content is loaded
            self.scroll_to_bottom()

            return True

        except Exception as e:
            logger.error(f"❌ Error in enhanced search button click: {e}")
            return False

    def set_results_per_page_to_100(self):
        """Set results per page to 100 for maximum efficiency with verification"""
        try:
            logger.info("🔧 Setting results per page to 100...")

            # Wait for the results per page dropdown with reliable timeout
            results_per_page_select = WebDriverWait(self.driver, 8).until(  # Restored to 8s for reliability
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.form-select.w11110"))
            )

            # Create Select object and choose 100
            select = Select(results_per_page_select)

            # Check if 100 option is available
            available_options = [option.get_attribute('value') for option in select.options]
            logger.info(f"📋 Available results per page options: {available_options}")

            if "100" in available_options:
                select.select_by_value("100")

                # Verify the selection was successful
                selected_value = select.first_selected_option.get_attribute('value')
                if selected_value == "100":
                    logger.info("✅ Successfully set and verified results per page to 100")
                    time.sleep(1.5)  # Increased from 0.5s to 1.5s for reliable page update
                    return True
                else:
                    logger.warning(f"⚠️ Selection verification failed. Selected: {selected_value}")
                    return False
            else:
                logger.warning("⚠️ Option '100' not available in results per page dropdown")
                # Try to select the highest available option
                max_option = max([int(opt) for opt in available_options if opt.isdigit()])
                select.select_by_value(str(max_option))
                logger.info(f"📋 Selected maximum available option: {max_option}")
                time.sleep(1.5)  # Increased from 0.5s to 1.5s for reliable page update
                return True

        except Exception as e:
            logger.warning(f"⚠️ Failed to set results per page to 100: {e}")
            return False

    def scroll_to_bottom(self):
        """Optimized scroll to bottom with minimal wait times"""
        try:
            logger.debug("🔄 Scrolling to bottom of page...")

            # Fast scroll to bottom without height checking for performance
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)  # Minimal wait - reduced from 3 seconds to 0.5 seconds

            logger.debug("✅ Scrolled to bottom of page")
            return True

        except Exception as e:
            logger.warning(f"⚠️ Error scrolling to bottom: {e}")
            return False

    def wait_for_school_elements_to_load(self):
        """Wait for school elements to be properly loaded on the page"""
        try:
            logger.info("⏳ Waiting for school elements to load...")

            # Wait for school elements to be present
            selectors_to_check = [
                ".accordion-body",
                ".accordion-item",
                "[class*='accordion']"
            ]

            elements_found = False
            for selector in selectors_to_check:
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: len(driver.find_elements(By.CSS_SELECTOR, selector)) > 0
                    )
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"✅ Found {len(elements)} school elements with selector: {selector}")
                        elements_found = True
                        break
                except:
                    continue

            if not elements_found:
                logger.warning("⚠️ No school elements found after waiting - page may have no results")

            # Reliable wait to ensure all content is fully rendered
            time.sleep(3)  # Increased from 2s to 3s for complete content loading

            return elements_found

        except Exception as e:
            logger.warning(f"⚠️ Error waiting for school elements: {e}")
            return False

    def wait_for_school_elements_to_load_fast(self):
        """Fast version of element loading check with reduced timeouts"""
        try:
            logger.debug("⚡ Fast check for school elements...")

            # Quick check with reduced timeout
            selectors_to_check = [".accordion-body", ".accordion-item", "[class*='accordion']"]

            for selector in selectors_to_check:
                try:
                    WebDriverWait(self.driver, 5).until(  # Reduced from 10s to 5s
                        lambda driver: len(driver.find_elements(By.CSS_SELECTOR, selector)) > 0
                    )
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.debug(f"⚡ Fast found {len(elements)} elements with: {selector}")
                        # Balanced wait for content rendering
                        time.sleep(1.5)  # Increased from 0.5s to 1.5s for better reliability
                        return True
                except:
                    continue

            logger.debug("⚡ Fast check: No elements found")
            return False

        except Exception as e:
            logger.debug(f"⚠️ Error in fast element check: {e}")
            return False

    def initialize_csv_file(self, state_name):
        """Initialize CSV file for incremental saving with enhanced debugging"""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_state_name = state_name.replace(' ', '_').replace('&', 'and').replace('/', '_').upper()
            self.current_csv_file = f"{clean_state_name}_phase1_complete_{timestamp}.csv"

            # Get absolute path for debugging
            abs_path = os.path.abspath(self.current_csv_file)
            current_dir = os.getcwd()

            # Reset tracking variables
            self.csv_headers_written = False
            self.total_schools_saved = 0

            logger.info(f"📁 Initialized CSV file for incremental saving: {self.current_csv_file}")
            logger.info(f"📍 Absolute path: {abs_path}")
            logger.info(f"📂 Current working directory: {current_dir}")

            # Test if we can create the file
            try:
                test_file = open(self.current_csv_file, 'w', encoding='utf-8')
                test_file.close()
                os.remove(self.current_csv_file)  # Clean up test file
                logger.info(f"✅ CSV file creation test successful")
            except Exception as test_error:
                logger.error(f"❌ CSV file creation test failed: {test_error}")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Error initializing CSV file: {e}")
            return False

    def save_schools_to_csv_incremental(self, schools_data, page_number):
        """Save schools data to CSV file incrementally (page by page)"""
        try:
            if not schools_data:
                logger.debug(f"   📄 No schools to save for page {page_number}")
                return True

            if not self.current_csv_file:
                logger.error("❌ CSV file not initialized")
                return False

            # Define CSV headers (matching Phase 1 specification exactly)
            headers = [
                'has_know_more_link', 'phase2_ready', 'state', 'state_id', 'district', 'district_id',
                'extraction_date', 'udise_code', 'school_name', 'know_more_link', 'email',
                'operational_status', 'school_category', 'school_management', 'school_type',
                'school_location', 'address', 'pin_code'
            ]

            # Write headers if this is the first write
            if not self.csv_headers_written:
                try:
                    with open(self.current_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=headers)
                        writer.writeheader()
                        csvfile.flush()  # Ensure data is written to disk

                    # Verify file was created
                    if os.path.exists(self.current_csv_file):
                        file_size = os.path.getsize(self.current_csv_file)
                        logger.info(f"   📝 Created CSV file with headers: {self.current_csv_file} ({file_size} bytes)")
                        self.csv_headers_written = True
                    else:
                        logger.error(f"   ❌ CSV file was not created: {self.current_csv_file}")
                        return False

                except Exception as header_error:
                    logger.error(f"   ❌ Error writing CSV headers: {header_error}")
                    return False

            # Append schools data to CSV
            try:
                with open(self.current_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headers)

                    rows_written = 0
                    for school in schools_data:
                        # Ensure all required fields are present and map field names
                        school_row = {}
                        for header in headers:
                            if header == 'has_know_more_link':
                                # Boolean: True if know_more_link exists and is valid
                                know_more_link = school.get('know_more_link', 'N/A')
                                school_row[header] = (know_more_link != 'N/A' and
                                                    know_more_link and
                                                    'schooldetail' in str(know_more_link))
                            elif header == 'phase2_ready':
                                # Boolean: Same as has_know_more_link (ready for Phase 2 if has valid link)
                                know_more_link = school.get('know_more_link', 'N/A')
                                school_row[header] = (know_more_link != 'N/A' and
                                                    know_more_link and
                                                    'schooldetail' in str(know_more_link))
                            elif header == 'school_location':
                                # Map 'location' field to 'school_location'
                                school_row[header] = school.get('location', 'N/A')
                            elif header == 'pin_code':
                                # Map 'pincode' field to 'pin_code'
                                school_row[header] = school.get('pincode', 'N/A')
                            elif header == 'address':
                                # Use address field or fallback to location
                                school_row[header] = school.get('address', school.get('location', 'N/A'))
                            else:
                                # Direct mapping for all other fields
                                school_row[header] = school.get(header, 'N/A')
                        writer.writerow(school_row)
                        rows_written += 1

                    csvfile.flush()  # Ensure data is written to disk

                self.total_schools_saved += len(schools_data)

                # Verify file exists and has grown
                if os.path.exists(self.current_csv_file):
                    file_size = os.path.getsize(self.current_csv_file)
                    logger.info(f"   💾 Saved page {page_number} with {len(schools_data)} schools to CSV")
                    logger.info(f"   📊 Total schools saved so far: {self.total_schools_saved}")
                    logger.info(f"   📄 Current file size: {file_size} bytes")
                else:
                    logger.error(f"   ❌ CSV file disappeared after writing: {self.current_csv_file}")
                    return False

            except Exception as write_error:
                logger.error(f"   ❌ Error writing schools data to CSV: {write_error}")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Error saving schools to CSV: {e}")
            return False

    def check_csv_file_status(self):
        """Check current CSV file status and provide detailed information"""
        try:
            if not self.current_csv_file:
                logger.warning("⚠️ No CSV file initialized")
                return False

            abs_path = os.path.abspath(self.current_csv_file)
            logger.info(f"🔍 Checking CSV file status:")
            logger.info(f"   📄 Filename: {self.current_csv_file}")
            logger.info(f"   📍 Absolute path: {abs_path}")

            if os.path.exists(self.current_csv_file):
                file_size = os.path.getsize(self.current_csv_file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.current_csv_file))
                logger.info(f"   ✅ File exists: YES")
                logger.info(f"   📊 File size: {file_size} bytes ({file_size/1024:.1f} KB)")
                logger.info(f"   🕒 Last modified: {mod_time}")
                logger.info(f"   📊 Schools saved: {self.total_schools_saved}")
                return True
            else:
                logger.error(f"   ❌ File exists: NO")
                logger.error(f"   📂 Directory contents:")
                try:
                    current_dir = os.getcwd()
                    files = [f for f in os.listdir(current_dir) if f.endswith('.csv')]
                    for f in files[:5]:  # Show first 5 CSV files
                        logger.error(f"      • {f}")
                except:
                    pass
                return False

        except Exception as e:
            logger.error(f"❌ Error checking CSV file status: {e}")
            return False

    def finalize_csv_file(self):
        """Finalize CSV file and provide summary"""
        try:
            # First check the file status
            self.check_csv_file_status()

            if self.current_csv_file and os.path.exists(self.current_csv_file):
                file_size = os.path.getsize(self.current_csv_file)
                abs_path = os.path.abspath(self.current_csv_file)
                logger.info(f"📁 CSV file finalized: {self.current_csv_file}")
                logger.info(f"📍 Full path: {abs_path}")
                logger.info(f"📊 Final statistics: {self.total_schools_saved} schools, {file_size/1024:.1f} KB")
                return True
            else:
                logger.warning("⚠️ No CSV file to finalize or file does not exist")
                return False

        except Exception as e:
            logger.error(f"❌ Error finalizing CSV file: {e}")
            return False

    def enhanced_click_next_page(self):
        """Enhanced pagination handling with robust next button detection and retry mechanism"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                logger.debug(f"Attempting to click next page (attempt {attempt + 1}/{max_retries})")

                # Find next button using the specific HTML structure
                next_buttons = self.driver.find_elements(By.CSS_SELECTOR, "a.nextBtn")

                if not next_buttons:
                    logger.debug("No next button found")
                    return False

                next_button = next_buttons[0]

                # Check if button is displayed
                if not next_button.is_displayed():
                    logger.debug("Next button not displayed")
                    return False

                # CRITICAL: Check if the parent <li> element has disabled class
                try:
                    parent_li = next_button.find_element(By.XPATH, "..")
                    parent_classes = parent_li.get_attribute("class") or ""

                    # Check if parent li has disabled class - this is the primary indicator
                    if "disabled" in parent_classes.lower():
                        logger.info("📄 Next button is disabled (parent li has disabled class) - reached end of pagination")
                        logger.info(f"📊 Final pagination status: Parent classes = '{parent_classes}'")
                        return False

                except Exception as parent_check_error:
                    logger.debug(f"Could not check parent element: {parent_check_error}")
                    # Continue with other checks

                # Additional checks for button state
                button_classes = next_button.get_attribute("class") or ""
                if "disabled" in button_classes.lower():
                    logger.info("📄 Next button is disabled (has disabled class) - reached end of pagination")
                    logger.info(f"📊 Final pagination status: Button classes = '{button_classes}'")
                    return False

                # Check for disabled attribute
                if next_button.get_attribute("disabled"):
                    logger.info("📄 Next button has disabled attribute - reached end of pagination")
                    logger.info(f"📊 Final pagination status: Disabled attribute = True")
                    return False

                # Check if button is enabled (basic Selenium check)
                if not next_button.is_enabled():
                    logger.info("📄 Next button is not enabled - reached end of pagination")
                    logger.info(f"📊 Final pagination status: Button enabled = False")
                    return False

                # Scroll to button to ensure it's visible
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(0.3)  # Reduced from 1 second to 0.3 seconds

                    # Try multiple click methods with retry
                    click_success = False

                    # Method 1: Regular click
                    try:
                        next_button.click()
                        logger.info("✅ Clicked next page button (regular click)")
                        click_success = True
                    except Exception as click_error:
                        logger.debug(f"Regular click failed: {click_error}")

                    # Method 2: JavaScript click if regular click failed
                    if not click_success:
                        try:
                            self.driver.execute_script("arguments[0].click();", next_button)
                            logger.info("✅ Clicked next page button (JavaScript click)")
                            click_success = True
                        except Exception as js_click_error:
                            logger.debug(f"JavaScript click failed: {js_click_error}")

                    # Method 3: Force click with JavaScript if both failed
                    if not click_success:
                        try:
                            self.driver.execute_script("""
                                var event = new MouseEvent('click', {
                                    view: window,
                                    bubbles: true,
                                    cancelable: true
                                });
                                arguments[0].dispatchEvent(event);
                            """, next_button)
                            logger.info("✅ Clicked next page button (force JavaScript click)")
                            click_success = True
                        except Exception as force_click_error:
                            logger.debug(f"Force JavaScript click failed: {force_click_error}")

                    if click_success:
                        # Balanced wait time for page to load after successful click
                        time.sleep(1.5)  # Restored from 0.8s to 1.5s for reliable page loading
                        return True
                    else:
                        logger.warning(f"All click methods failed on attempt {attempt + 1}")

                except Exception as scroll_error:
                    logger.warning(f"Failed to scroll to next button on attempt {attempt + 1}: {scroll_error}")

                # Reasonable wait before retry
                if attempt < max_retries - 1:
                    time.sleep(0.8)  # Increased from 0.3s to 0.8s for better reliability

            except Exception as e:
                logger.warning(f"Error in enhanced_click_next_page attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)

        logger.warning(f"Failed to click next page button after {max_retries} attempts")
        return False

    def extract_email_from_school_element(self, school_element):
        """Ultra-fast email extraction with single DOM access"""
        try:
            # Single DOM access for maximum performance
            element_html = school_element.get_attribute('innerHTML')
            if not element_html:
                return 'N/A'

            # Pre-compiled regex patterns for maximum speed
            if not hasattr(self, '_email_patterns'):
                self._email_patterns = [
                    re.compile(r'href="mailto:([^"]+)"', re.IGNORECASE),  # mailto links
                    re.compile(r'<span[^>]*>([^<]*@[^<]*)</span>', re.IGNORECASE),  # span with email
                    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')  # general email
                ]

            # Fast pattern matching with early exit
            for i, pattern in enumerate(self._email_patterns):
                match = pattern.search(element_html)
                if match:
                    email = match.group(1) if i < 2 else match.group(0)
                    email = email.strip()
                    if email and '@' in email and len(email) > 5:  # Basic validation
                        return email

            return 'N/A'

        except:
            return 'N/A'

    def extract_single_school_data_with_email(self, school_element):
        """Enhanced single school data extraction with validation and email functionality"""
        try:
            # First, get the base school data using the original method
            school_data = self.base_scraper.extract_single_school_data(school_element)

            if not school_data:
                return None

            # Validate that we have meaningful school data
            # Check if essential fields have actual data (not just N/A)
            essential_fields = ['school_name', 'udise_code', 'know_more_link']
            has_meaningful_data = False

            for field in essential_fields:
                value = school_data.get(field, 'N/A')
                if value and value != 'N/A' and value.strip():
                    has_meaningful_data = True
                    break

            # If no meaningful data found, this might be an empty element
            if not has_meaningful_data:
                logger.debug(f"   ⚠️ Skipping element with no meaningful school data")
                return None

            # Add email extraction
            email = self.extract_email_from_school_element(school_element)
            school_data['email'] = email

            return school_data

        except Exception as e:
            logger.debug(f"   Error in enhanced school data extraction: {e}")
            return None

    def extract_schools_from_current_page_with_email(self):
        """Enhanced schools extraction from current page with email functionality"""
        try:
            # Try multiple selectors to find school elements (same as base method)
            selectors_to_try = [
                ".accordion-body",
                ".accordion-item",
                "[class*='accordion']",
                ".card-body",
                ".result-item",
                "table tbody tr",
                ".school-item"
            ]

            school_elements = []

            for selector in selectors_to_try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Filter out potentially empty elements
                    filtered_elements = []
                    for element in elements:
                        try:
                            # Check if element has meaningful content
                            element_text = element.text.strip()
                            element_html = element.get_attribute('innerHTML')

                            # Skip if element is empty or has minimal content
                            if (element_text and len(element_text) > 10) or \
                               (element_html and len(element_html) > 50):
                                filtered_elements.append(element)
                        except:
                            # If we can't check the element, include it to be safe
                            filtered_elements.append(element)

                    if filtered_elements:
                        school_elements = filtered_elements
                        logger.debug(f"   Found {len(elements)} elements, filtered to {len(filtered_elements)} with selector: {selector}")
                        break

            if not school_elements:
                logger.warning("   ⚠️ No school elements found with any selector")
                # Enhanced debugging: Check page content and state
                page_text = self.driver.page_source[:2000]
                current_url = self.driver.current_url
                page_title = self.driver.title

                logger.warning(f"   🔍 Debug info:")
                logger.warning(f"      URL: {current_url}")
                logger.warning(f"      Title: {page_title}")
                logger.warning(f"      Page length: {len(self.driver.page_source)} chars")

                if "No records found" in page_text or "No data available" in page_text:
                    logger.info("   📄 Confirmed: No schools in this district")
                elif "loading" in page_text.lower() or "please wait" in page_text.lower():
                    logger.warning("   ⏳ Page appears to be still loading - waiting for completion...")
                    time.sleep(3)  # Restored from 1.5s to 3s for complete loading
                    # Retry element detection after adequate wait
                    for selector in selectors_to_try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            school_elements = elements
                            logger.info(f"   ✅ Found {len(elements)} school elements after retry with: {selector}")
                            break

                    if not school_elements:
                        logger.warning("   ❌ Still no elements found after retry")
                        return []
                else:
                    logger.warning("   ⚠️ Page may not have loaded properly or has different structure")
                    # Log a sample of page content for debugging
                    logger.warning(f"   📄 Page sample: {page_text[:500]}...")
                    return []

            # Process all schools with enhanced extraction including email
            schools_data = []
            email_found_count = 0
            skipped_elements = 0

            logger.debug(f"   🔍 Processing {len(school_elements)} detected school elements...")

            for i, school_element in enumerate(school_elements, 1):
                try:
                    school_data = self.extract_single_school_data_with_email(school_element)
                    if school_data:
                        schools_data.append(school_data)

                        # Count emails found
                        if school_data.get('email', 'N/A') != 'N/A':
                            email_found_count += 1
                    else:
                        skipped_elements += 1
                        logger.debug(f"   ⚠️ Skipped element {i} - no meaningful data")

                except Exception as e:
                    skipped_elements += 1
                    logger.debug(f"   ❌ Error processing element {i}: {e}")
                    continue

            # Log extraction summary
            logger.info(f"   📊 Processed {len(school_elements)} elements: {len(schools_data)} valid schools, {skipped_elements} skipped")
            if skipped_elements > 0:
                logger.warning(f"   ⚠️ {skipped_elements} elements were skipped due to missing data - this may indicate empty divs or non-school elements")

            # Reduced logging frequency - only log email stats every 10 pages or when significant
            if len(schools_data) > 0:
                logger.info(f"   📧 Email extraction: {email_found_count}/{len(schools_data)} schools have email addresses")
            return schools_data

        except Exception as e:
            logger.error(f"   Error extracting schools from page with email: {e}")
            return []

    def extract_schools_basic_data_enhanced(self):
        """Optimized schools extraction with incremental CSV saving and improved pagination"""
        try:
            schools_data = []
            page_number = 1
            start_time = time.time()

            logger.info("� Starting OPTIMIZED schools data extraction with robust pagination and incremental CSV saving...")
            logger.info("⚡ Performance optimizations: Reduced wait times, optimized scrolling, faster email extraction")

            while True:  # Remove hardcoded page limit - continue until no more pages
                logger.info(f"📄 Processing page {page_number}")

                # Reliable handling for first page
                if page_number == 1:
                    logger.info("🔍 First page - ensuring complete loading...")
                    # Full check for school elements to ensure reliability
                    self.wait_for_school_elements_to_load()
                    # Always scroll on first page to ensure all content is loaded
                    self.scroll_to_bottom()
                elif page_number % 5 == 0:
                    # Balanced scrolling: Scroll every 5th page for reliability
                    self.scroll_to_bottom()

                # Extract schools from current page using enhanced method with email extraction
                page_schools = self.extract_schools_from_current_page_with_email()

                # Reliable first page recovery
                if page_number == 1 and not page_schools:
                    logger.warning("⚠️ First page extraction failed - attempting reliable recovery...")
                    # Adequate wait time for recovery
                    time.sleep(4)  # Increased from 2s to 4s for better recovery
                    self.scroll_to_bottom()
                    # Additional wait after scrolling
                    time.sleep(1)
                    page_schools = self.extract_schools_from_current_page_with_email()

                    if page_schools:
                        logger.info(f"✅ First page recovery successful - found {len(page_schools)} schools")
                    else:
                        logger.error("❌ First page recovery failed - no schools extracted")

                # Save page schools to CSV immediately for crash protection
                if page_schools:
                    save_success = self.save_schools_to_csv_incremental(page_schools, page_number)
                    if not save_success:
                        logger.warning(f"⚠️ Failed to save page {page_number} to CSV, but continuing extraction")

                    # Check CSV file status after first page for debugging
                    if page_number == 1:
                        logger.info(f"🔍 Checking CSV file status after first page:")
                        self.check_csv_file_status()
                else:
                    # Log when no schools are found on a page
                    logger.warning(f"⚠️ No schools extracted from page {page_number}")

                schools_data.extend(page_schools)

                logger.info(f"   ✅ Extracted {len(page_schools)} schools from page {page_number}")
                logger.info(f"   📊 Total schools in memory: {len(schools_data)}")

                # Try to go to next page using enhanced method with retry
                logger.info(f"   🔄 Checking for next page after page {page_number}...")
                if not self.enhanced_click_next_page():
                    logger.info(f"📄 No more pages available after page {page_number}")
                    break

                page_number += 1

                # Balanced wait time for next page to load completely
                time.sleep(2)  # Increased from 1s to 2s for reliable page loading

                # Reliable check for new content with adequate timeout
                try:
                    # Wait for new content to load with reliable timeout
                    WebDriverWait(self.driver, 8).until(  # Restored from 4s to 8s for reliability
                        lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".accordion-body, .accordion-item, [class*='accordion']")) > 0
                    )
                except Exception as wait_error:
                    logger.warning(f"Timeout waiting for new page content: {wait_error}")
                    # Continue anyway as content might already be loaded

            # Performance summary
            total_time = time.time() - start_time
            avg_time_per_page = total_time / page_number if page_number > 0 else 0

            logger.info(f"✅ OPTIMIZED extraction completed: {len(schools_data)} total schools from {page_number} pages")
            logger.info(f"⚡ Performance Summary: {total_time:.1f}s total, {avg_time_per_page:.1f}s per page (target: <180s per page)")
            logger.info(f"📊 Pagination Summary: Processed {page_number} pages with no hardcoded limits")
            logger.info(f"📊 Average schools per page: {len(schools_data)/page_number:.1f}")
            logger.info(f"💾 CSV file saved: {self.current_csv_file} with {self.total_schools_saved} total schools")
            return schools_data

        except Exception as e:
            logger.error(f"Failed to extract schools data with enhanced method: {e}")
            return []

    def process_single_state_enhanced(self, target_state):
        """Enhanced processing for a single state with incremental CSV saving"""
        try:
            logger.info(f"🎯 Enhanced processing for state: {target_state['stateName']}")

            # Set current state
            self.current_state = target_state
            self.base_scraper.current_state = target_state

            # Initialize CSV file for incremental saving
            if not self.initialize_csv_file(target_state['stateName']):
                logger.error(f"❌ Failed to initialize CSV file for {target_state['stateName']}")
                return False

            # Initialize state data storage
            self.state_schools_with_links[target_state['stateName']] = []
            self.state_schools_no_links[target_state['stateName']] = []
            self.base_scraper.state_schools_with_links[target_state['stateName']] = []
            self.base_scraper.state_schools_no_links[target_state['stateName']] = []

            # Select the state
            if not self.select_state(target_state):
                logger.error(f"Failed to select state: {target_state['stateName']}")
                return False

            # Extract districts for this state
            districts = self.extract_districts_data()
            if not districts:
                logger.warning(f"No districts found for {target_state['stateName']}")
                self.base_scraper.save_state_data_to_csv(target_state['stateName'])
                return True

            logger.info(f"📋 Found {len(districts)} districts in {target_state['stateName']}")

            # Process each district with enhanced features
            for district_index, district in enumerate(districts, 1):
                logger.info(f"\n🏛️ Processing district {district_index}/{len(districts)}: {district['districtName']}")
                logger.info(f"💾 Writing to CSV file: {self.current_csv_file}")

                try:
                    # Select district
                    if self.select_district(district):
                        # Enhanced search with results per page optimization
                        if self.enhanced_click_search_button():
                            # Extract schools using enhanced method with incremental CSV saving
                            schools_data = self.extract_schools_basic_data_enhanced()
                        else:
                            logger.error(f"❌ Failed to click search button for district: {district['districtName']}")
                            schools_data = []

                        # Categorize schools
                        for school in schools_data:
                            if school.get('know_more_link') and school['know_more_link'] != 'N/A':
                                self.state_schools_with_links[target_state['stateName']].append(school)
                                self.base_scraper.state_schools_with_links[target_state['stateName']].append(school)
                            else:
                                self.state_schools_no_links[target_state['stateName']].append(school)
                                self.base_scraper.state_schools_no_links[target_state['stateName']].append(school)

                        logger.info(f"✅ Completed {district['districtName']}: {len(schools_data)} schools")
                    else:
                        logger.error(f"❌ Failed to select district: {district['districtName']}")

                except Exception as district_error:
                    logger.error(f"❌ Error processing district {district['districtName']}: {district_error}")
                    continue

            # Save data to CSV (legacy method - but incremental saving already done)
            self.base_scraper.save_state_data_to_csv(target_state['stateName'])

            total_schools = (len(self.state_schools_with_links.get(target_state['stateName'], [])) +
                           len(self.state_schools_no_links.get(target_state['stateName'], [])))
            logger.info(f"✅ Enhanced processing completed for {target_state['stateName']}: {total_schools} total schools")
            logger.info(f"💾 Incremental CSV file: {self.current_csv_file} with {self.total_schools_saved} schools saved")

            # Finalize CSV file
            self.finalize_csv_file()

            return True

        except Exception as e:
            logger.error(f"❌ Error in enhanced single state processing: {e}")
            return False

    def process_single_state_single_district(self, target_state, target_district):
        """Enhanced processing for a single state and single district with incremental CSV saving"""
        try:
            logger.info(f"🎯 Enhanced processing for district: {target_district['districtName']} in {target_state['stateName']}")

            # Set current state and district
            self.current_state = target_state
            self.current_district = target_district
            self.base_scraper.current_state = target_state
            self.base_scraper.current_district = target_district

            # Initialize CSV file for incremental saving
            if not self.initialize_csv_file(target_state['stateName']):
                logger.error(f"❌ Failed to initialize CSV file for {target_state['stateName']}")
                return False

            # Initialize state data storage
            self.state_schools_with_links[target_state['stateName']] = []
            self.state_schools_no_links[target_state['stateName']] = []
            self.base_scraper.state_schools_with_links[target_state['stateName']] = []
            self.base_scraper.state_schools_no_links[target_state['stateName']] = []

            # Select the state
            if not self.select_state(target_state):
                logger.error(f"Failed to select state: {target_state['stateName']}")
                return False

            # Select the district
            if not self.select_district(target_district):
                logger.error(f"Failed to select district: {target_district['districtName']}")
                return False

            # Enhanced search with results per page optimization
            if self.enhanced_click_search_button():
                # Extract schools using enhanced method
                schools_data = self.extract_schools_basic_data_enhanced()
            else:
                logger.error(f"❌ Failed to click search button for district: {target_district['districtName']}")
                schools_data = []

            # Categorize schools
            for school in schools_data:
                if school.get('know_more_link') and school['know_more_link'] != 'N/A':
                    self.state_schools_with_links[target_state['stateName']].append(school)
                    self.base_scraper.state_schools_with_links[target_state['stateName']].append(school)
                else:
                    self.state_schools_no_links[target_state['stateName']].append(school)
                    self.base_scraper.state_schools_no_links[target_state['stateName']].append(school)

            # Save data to CSV (legacy method - but incremental saving already done)
            self.base_scraper.save_state_data_to_csv(target_state['stateName'])

            logger.info(f"✅ Enhanced processing completed for {target_district['districtName']}: {len(schools_data)} schools")
            logger.info(f"💾 Incremental CSV file: {self.current_csv_file} with {self.total_schools_saved} schools saved")

            # Finalize CSV file
            self.finalize_csv_file()

            return True

        except Exception as e:
            logger.error(f"❌ Error in enhanced single district processing: {e}")
            return False

class SequentialStateProcessor:
    def __init__(self):
        self.processed_states = []
        self.failed_states = []
        self.total_schools_processed = 0
        self.start_time = None
        self.max_retries = 3
        self.retry_delay = 30  # seconds

        # State list (all 38 Indian states)
        self.states_list = [
            "ANDAMAN & NICOBAR ISLANDS",
            "ANDHRA PRADESH",
            "ARUNACHAL PRADESH",
            "ASSAM",
            "BIHAR",
            "CHANDIGARH",
            "CHHATTISGARH",
            "DADRA & NAGAR HAVELI AND DAMAN & DIU",
            "DELHI",
            "GOA",
            "GUJARAT",
            "HARYANA",
            "HIMACHAL PRADESH",
            "JAMMU & KASHMIR",
            "JHARKHAND",
            "KARNATAKA",
            "KENDRIYA VIDYALAYA SANGHATHAN",
            "KERALA",
            "LADAKH",
            "LAKSHADWEEP",
            "MADHYA PRADESH",
            "MAHARASHTRA",
            "MANIPUR",
            "MEGHALAYA",
            "MIZORAM",
            "NAGALAND",
            "NAVODAYA VIDYALAYA SAMITI",
            "ODISHA",
            "PUDUCHERRY",
            "PUNJAB",
            "RAJASTHAN",
            "SIKKIM",
            "TAMILNADU",
            "TELANGANA",
            "TRIPURA",
            "UTTARAKHAND",
            "UTTAR PRADESH",
            "WEST BENGAL"
        ]

    def show_interactive_menu(self):
        """Display interactive menu for processing options"""
        print("\n" + "="*80)
        print("🚀 ENHANCED SEQUENTIAL STATE PROCESSOR")
        print("="*80)
        print("Select processing mode:")
        print("1. Process all states (Complete workflow)")
        print("2. Process a single specific state")
        print("3. Process one state and one district (Testing mode)")
        print("4. Exit the program")
        print("="*80)

        while True:
            try:
                choice = input("\nEnter your choice (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    return choice
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
            except KeyboardInterrupt:
                print("\n\n👋 Exiting program...")
                return '4'
            except Exception as e:
                print(f"❌ Error reading input: {e}")
                return '4'

    def select_state_interactive(self):
        """Interactive state selection"""
        print("\n📋 Available States:")
        print("-" * 50)
        for i, state in enumerate(self.states_list, 1):
            print(f"{i:2d}. {state}")
        print("-" * 50)

        while True:
            try:
                choice = input(f"\nSelect state (1-{len(self.states_list)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    return None

                state_index = int(choice) - 1
                if 0 <= state_index < len(self.states_list):
                    selected_state = self.states_list[state_index]
                    print(f"✅ Selected state: {selected_state}")
                    return selected_state
                else:
                    print(f"❌ Invalid choice. Please enter a number between 1 and {len(self.states_list)}.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\n\n👋 Exiting...")
                return None

    def select_district_interactive(self, state_name):
        """Interactive district selection for a given state"""
        try:
            # Import the Phase 1 scraper to get districts
            from phase1_statewise_scraper import StatewiseSchoolScraper

            logger.info(f"🔧 Getting districts for {state_name}...")
            scraper = StatewiseSchoolScraper()
            scraper.setup_driver()

            # Navigate and get state data
            if not scraper.navigate_to_portal():
                logger.error("Failed to navigate to portal")
                scraper.driver.quit()
                return None

            states = scraper.extract_states_data()
            target_state = None
            for state in states:
                if state['stateName'] == state_name:
                    target_state = state
                    break

            if not target_state:
                logger.error(f"State {state_name} not found")
                scraper.driver.quit()
                return None

            # Select state and get districts
            scraper.select_state(target_state)
            districts = scraper.extract_districts_data()
            scraper.driver.quit()

            if not districts:
                print(f"❌ No districts found for {state_name}")
                return None

            print(f"\n📋 Available Districts in {state_name}:")
            print("-" * 60)
            for i, district in enumerate(districts, 1):
                print(f"{i:2d}. {district['districtName']}")
            print("-" * 60)

            while True:
                try:
                    choice = input(f"\nSelect district (1-{len(districts)}) or 'q' to quit: ").strip()
                    if choice.lower() == 'q':
                        return None

                    district_index = int(choice) - 1
                    if 0 <= district_index < len(districts):
                        selected_district = districts[district_index]
                        print(f"✅ Selected district: {selected_district['districtName']}")
                        return selected_district
                    else:
                        print(f"❌ Invalid choice. Please enter a number between 1 and {len(districts)}.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
                except KeyboardInterrupt:
                    print("\n\n👋 Exiting...")
                    return None

        except Exception as e:
            logger.error(f"Error getting districts for {state_name}: {e}")
            return None



    def execute_phase1_single_state(self, state_name, target_district=None):
        """Execute Phase 1 for a single state with enhanced features"""
        try:
            logger.info(f"   🔧 Initializing enhanced Phase 1 scraper for {state_name}")
            scraper = EnhancedStatewiseSchoolScraper()

            # Setup driver with connection error handling
            scraper.setup_driver()

            # Navigate to portal with retry
            success = scraper.navigate_to_portal()
            if not success:
                logger.error(f"   ❌ Failed to navigate to portal for {state_name}")
                return False

            # Extract states list
            states = scraper.extract_states_data()
            if not states:
                logger.error(f"   ❌ Failed to extract states data for {state_name}")
                return False

            # Find the target state
            target_state = None
            for state in states:
                if state['stateName'] == state_name:
                    target_state = state
                    break

            if not target_state:
                logger.error(f"   ❌ State {state_name} not found in states list")
                return False

            # Process the single state (or single district if specified)
            if target_district:
                logger.info(f"   🎯 Processing single district: {target_district['districtName']} in {state_name}")
                success = scraper.process_single_state_single_district(target_state, target_district)
            else:
                logger.info(f"   🎯 Processing single state: {state_name}")
                success = scraper.process_single_state_enhanced(target_state)

            # Cleanup
            scraper.driver.quit()

            return success

        except Exception as e:
            logger.error(f"   ❌ Error in Phase 1 execution for {state_name}: {e}")
            return False



    def find_phase1_csv_for_state(self, state_name):
        """Find the Phase 1 CSV file for a specific state"""
        try:
            # Clean state name for filename matching
            clean_state = state_name.replace(' ', '_').replace('&', 'and').replace('/', '_').upper()
            
            # Look for the Phase 1 CSV file
            pattern = f"{clean_state}_phase1_complete_*.csv"
            csv_files = glob.glob(pattern)
            
            if csv_files:
                # Return the most recent file
                latest_file = max(csv_files, key=os.path.getctime)
                logger.info(f"   📁 Found Phase 1 CSV: {latest_file}")
                return latest_file
            else:
                logger.error(f"   ❌ No Phase 1 CSV found for {state_name}")
                return None
                
        except Exception as e:
            logger.error(f"   ❌ Error finding Phase 1 CSV for {state_name}: {e}")
            return None

    def run_phase2_for_state(self, state_name, csv_file):
        """Run Phase 2 processing for a specific state with retry mechanism"""
        logger.info(f"🔄 Starting Phase 2 for state: {state_name}")
        
        for attempt in range(self.max_retries):
            try:
                result = self.execute_phase2_single_state(state_name, csv_file)
                
                if result:
                    logger.info(f"✅ Phase 2 completed successfully for {state_name}")
                    return True
                else:
                    logger.warning(f"⚠️ Phase 2 failed for {state_name} (attempt {attempt + 1}/{self.max_retries})")
                    
            except Exception as e:
                logger.error(f"❌ Phase 2 error for {state_name} (attempt {attempt + 1}/{self.max_retries}): {e}")
            
            if attempt < self.max_retries - 1:
                logger.info(f"⏳ Retrying Phase 2 for {state_name} in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        logger.error(f"❌ Phase 2 failed for {state_name} after {self.max_retries} attempts")
        return False

    def execute_phase2_single_state(self, state_name, csv_file):
        """Execute Phase 2 for a single state"""
        try:
            # Import the Phase 2 processor components
            from phase2_automated_processor import AutomatedPhase2Processor
            
            logger.info(f"   🔧 Initializing Phase 2 processor for {state_name}")
            processor = AutomatedPhase2Processor()
            
            # Setup driver with connection error handling
            processor.setup_driver()
            
            # Process the single state file
            success = processor.process_state_file_automated(csv_file)
            
            # Cleanup
            processor.driver.quit()
            
            return success
            
        except Exception as e:
            logger.error(f"   ❌ Error in Phase 2 execution for {state_name}: {e}")
            return False

    def process_state_complete_cycle(self, state_name):
        """Process a complete Phase 1 → Phase 2 cycle for one state"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🏛️ PROCESSING STATE: {state_name}")
        logger.info(f"{'='*80}")
        
        state_start_time = time.time()
        
        try:
            # Phase 1: Extract school data
            logger.info(f"📋 PHASE 1: Extracting school data for {state_name}")
            phase1_success = self.run_phase1_for_state(state_name)
            
            if not phase1_success:
                logger.error(f"❌ Phase 1 failed for {state_name} - skipping Phase 2")
                self.failed_states.append(f"{state_name} (Phase 1 failed)")
                return False
            
            # Find the generated CSV file
            csv_file = self.find_phase1_csv_for_state(state_name)
            if not csv_file:
                logger.error(f"❌ No Phase 1 CSV found for {state_name} - skipping Phase 2")
                self.failed_states.append(f"{state_name} (CSV not found)")
                return False
            
            # Brief pause between phases
            time.sleep(5)
            
            # Phase 2: Process detailed data
            logger.info(f"🔍 PHASE 2: Processing detailed data for {state_name}")
            phase2_success = self.run_phase2_for_state(state_name, csv_file)
            
            if not phase2_success:
                logger.error(f"❌ Phase 2 failed for {state_name}")
                self.failed_states.append(f"{state_name} (Phase 2 failed)")
                return False
            
            # Success!
            state_time = time.time() - state_start_time
            self.processed_states.append(state_name)
            
            logger.info(f"✅ COMPLETED {state_name} in {state_time/60:.1f} minutes")
            logger.info(f"📊 Progress: {len(self.processed_states)}/{len(self.states_list)} states completed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Critical error processing {state_name}: {e}")
            self.failed_states.append(f"{state_name} (Critical error)")
            return False

    def run_sequential_processing(self):
        """Run the complete sequential state processing workflow"""
        try:
            self.start_time = time.time()
            
            logger.info("🚀 STARTING SEQUENTIAL STATE PROCESSING")
            logger.info("="*80)
            logger.info(f"📋 Total states to process: {len(self.states_list)}")
            logger.info(f"🔄 Workflow: State → Phase 1 → Phase 2 → Next State")
            logger.info("="*80)
            
            # Process each state sequentially
            for i, state_name in enumerate(self.states_list, 1):
                logger.info(f"\n🎯 STARTING STATE {i}/{len(self.states_list)}: {state_name}")
                
                success = self.process_state_complete_cycle(state_name)
                
                if success:
                    logger.info(f"✅ State {i} completed successfully: {state_name}")
                else:
                    logger.warning(f"⚠️ State {i} failed: {state_name}")
                
                # Brief pause between states
                if i < len(self.states_list):
                    logger.info("⏳ Brief pause before next state...")
                    time.sleep(10)
            
            # Final summary
            self.show_final_summary()
            
        except Exception as e:
            logger.error(f"❌ Critical error in sequential processing: {e}")
        finally:
            logger.info("🔒 Sequential processing completed")

    def show_final_summary(self):
        """Show final processing summary"""
        total_time = time.time() - self.start_time
        
        logger.info(f"\n{'='*80}")
        logger.info("🎯 SEQUENTIAL PROCESSING COMPLETED")
        logger.info(f"{'='*80}")
        logger.info(f"⏱️ Total processing time: {total_time/3600:.1f} hours")
        logger.info(f"✅ Successfully processed states: {len(self.processed_states)}")
        logger.info(f"❌ Failed states: {len(self.failed_states)}")
        logger.info(f"📈 Success rate: {len(self.processed_states)/len(self.states_list)*100:.1f}%")
        
        if self.processed_states:
            logger.info(f"\n✅ SUCCESSFUL STATES:")
            for state in self.processed_states:
                logger.info(f"   ✓ {state}")
        
        if self.failed_states:
            logger.info(f"\n❌ FAILED STATES:")
            for state in self.failed_states:
                logger.info(f"   ✗ {state}")
        
        logger.info(f"\n💾 Output files pattern:")
        logger.info(f"   Phase 1: *_phase1_complete_*.csv")
        logger.info(f"   Phase 2: *_phase2_batch*_*.csv")
        logger.info("🎉 Sequential processing complete!")

    def run_single_state_processing(self, state_name):
        """Run processing for a single state"""
        try:
            self.start_time = time.time()

            logger.info("🚀 STARTING SINGLE STATE PROCESSING")
            logger.info("="*80)
            logger.info(f"🎯 Target state: {state_name}")
            logger.info("="*80)

            success = self.process_state_complete_cycle(state_name)

            if success:
                logger.info(f"✅ Single state processing completed successfully: {state_name}")
            else:
                logger.warning(f"⚠️ Single state processing failed: {state_name}")

            # Show summary
            self.show_final_summary()

        except Exception as e:
            logger.error(f"❌ Critical error in single state processing: {e}")
        finally:
            logger.info("🔒 Single state processing completed")

    def run_single_district_processing(self, state_name, district_data):
        """Run processing for a single district in a state"""
        try:
            self.start_time = time.time()

            logger.info("🚀 STARTING SINGLE DISTRICT PROCESSING")
            logger.info("="*80)
            logger.info(f"🎯 Target state: {state_name}")
            logger.info(f"🎯 Target district: {district_data['districtName']}")
            logger.info("="*80)

            # Phase 1: Extract school data for single district
            logger.info(f"📋 PHASE 1: Extracting school data for {district_data['districtName']}")
            phase1_success = self.run_phase1_for_state(state_name, target_district=district_data)

            if not phase1_success:
                logger.error(f"❌ Phase 1 failed for {district_data['districtName']} - skipping Phase 2")
                self.failed_states.append(f"{state_name} - {district_data['districtName']} (Phase 1 failed)")
                return False

            # Find the generated CSV file
            csv_file = self.find_phase1_csv_for_state(state_name)
            if not csv_file:
                logger.error(f"❌ No Phase 1 CSV found for {state_name} - skipping Phase 2")
                self.failed_states.append(f"{state_name} - {district_data['districtName']} (CSV not found)")
                return False

            # Brief pause between phases
            time.sleep(5)

            # Phase 2: Process detailed data
            logger.info(f"🔍 PHASE 2: Processing detailed data for {district_data['districtName']}")
            phase2_success = self.run_phase2_for_state(state_name, csv_file)

            if not phase2_success:
                logger.error(f"❌ Phase 2 failed for {district_data['districtName']}")
                self.failed_states.append(f"{state_name} - {district_data['districtName']} (Phase 2 failed)")
                return False

            # Success!
            self.processed_states.append(f"{state_name} - {district_data['districtName']}")
            logger.info(f"✅ COMPLETED {district_data['districtName']} in {state_name}")

            # Show summary
            self.show_final_summary()

            return True

        except Exception as e:
            logger.error(f"❌ Critical error in single district processing: {e}")
            return False

    def run_phase1_for_state(self, state_name, target_district=None):
        """Run Phase 1 scraper for a specific state with optional district targeting"""
        logger.info(f"🚀 Starting Phase 1 for state: {state_name}")

        for attempt in range(self.max_retries):
            try:
                # Execute Phase 1 with optional district targeting
                result = self.execute_phase1_single_state(state_name, target_district)

                if result:
                    logger.info(f"✅ Phase 1 completed successfully for {state_name}")
                    return True
                else:
                    logger.warning(f"⚠️ Phase 1 failed for {state_name} (attempt {attempt + 1}/{self.max_retries})")

            except Exception as e:
                logger.error(f"❌ Phase 1 error for {state_name} (attempt {attempt + 1}/{self.max_retries}): {e}")

            if attempt < self.max_retries - 1:
                logger.info(f"⏳ Retrying Phase 1 for {state_name} in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

        logger.error(f"❌ Phase 1 failed for {state_name} after {self.max_retries} attempts")
        return False

def main():
    """Main function with interactive menu for enhanced sequential state processing"""
    try:
        processor = SequentialStateProcessor()

        while True:
            choice = processor.show_interactive_menu()

            if choice == '1':
                # Process all states
                processor.run_sequential_processing()
                break

            elif choice == '2':
                # Process a single specific state
                selected_state = processor.select_state_interactive()
                if selected_state:
                    processor.run_single_state_processing(selected_state)
                break

            elif choice == '3':
                # Process one state and one district
                selected_state = processor.select_state_interactive()
                if selected_state:
                    selected_district = processor.select_district_interactive(selected_state)
                    if selected_district:
                        processor.run_single_district_processing(selected_state, selected_district)
                break

            elif choice == '4':
                # Exit the program
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please try again.")

    except Exception as e:
        print(f"❌ Critical error: {e}")
        print("Please check the logs above for details")

if __name__ == "__main__":
    main()
