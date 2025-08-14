#!/usr/bin/env python3
"""
School Counting Tool - Count total schools in each district of every state
Uses phase1_statewise_scraper.py as reference to navigate UDISE Plus portal
and extract school counts from search results.
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json
import re
import undetected_chromedriver as uc
import logging
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchoolCountingTool:
    def __init__(self):
        self.driver = None
        self.current_state = None
        self.current_district = None
        
        # State list (all 38 Indian states)
        self.states_list = [
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

    def setup_driver(self):
        """Initialize the Chrome browser driver with optimized performance settings"""
        try:
            # Setup Chrome options for optimal performance and reliability
            options = uc.ChromeOptions()

            # Core stability options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")

            # Performance optimizations (balanced for speed and functionality)
            options.add_argument("--disable-images")  # Speed optimization
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")

            # Memory and resource optimizations
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")

            # Initialize Chrome driver
            self.driver = uc.Chrome(options=options, version_main=138)
            self.driver.maximize_window()

            # Balanced timeouts for reliability and speed
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(20)

            logger.info("✅ Chrome browser driver initialized for school counting")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome driver: {e}")
            logger.error("Please ensure Chrome browser is installed and updated")
            return False

    def navigate_to_portal(self, max_retries=3):
        """Navigate to the UDISE Plus portal and access advance search with retry mechanism"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 Navigating to UDISE Plus portal... (attempt {attempt + 1}/{max_retries})")
                self.driver.get("https://udiseplus.gov.in/#/en/home")
                time.sleep(3)

                # Click on Visit Portal
                logger.info("🔍 Looking for Visit Portal button...")
                visit_portal_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Visit Portal')]"))
                )
                visit_portal_btn.click()
                logger.info("✅ Clicked Visit Portal button")
                time.sleep(3)

                # Switch to new tab if opened
                if len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    logger.info("🔄 Switched to new tab")
                    time.sleep(2)

                # Click on Advance Search
                logger.info("🔍 Looking for Advance Search button...")
                advance_search_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@id='advanceSearch']"))
                )
                advance_search_btn.click()
                logger.info("✅ Clicked Advance Search button")
                time.sleep(3)

                # Verify we're on the advance search page
                if "advance" in self.driver.current_url.lower():
                    logger.info("✅ Successfully navigated to advance search page")
                    return True
                else:
                    logger.warning(f"⚠️ May not be on advance search page. Current URL: {self.driver.current_url}")
                    return True  # Continue anyway

            except Exception as e:
                logger.error(f"❌ Navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    logger.error("❌ All navigation attempts failed")
                    return False

        return False

    def extract_states_data(self):
        """Extract all states data from dropdown"""
        try:
            logger.info("🔍 Looking for state dropdown...")

            # Wait for state dropdown to be present and populated
            state_select = WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.form-select.select"))
            )
            logger.info("✅ Found state dropdown")

            # Wait for options to populate
            time.sleep(1)

            # Get all state options
            state_options = state_select.find_elements(By.TAG_NAME, "option")
            logger.info(f"📋 Found {len(state_options)} total options in state dropdown")

            if len(state_options) <= 1:
                logger.error("❌ State dropdown appears to be empty or not loaded")
                return []

            states_data = []
            for option in state_options[1:]:  # Skip first "Select State" option
                state_value = option.get_attribute("value")
                state_text = option.text.strip()

                if state_value and state_text and state_text != "Select State":
                    try:
                        # Try to parse as JSON (complex state data)
                        state_data = json.loads(state_value)
                        if isinstance(state_data, dict) and 'stateName' in state_data:
                            states_data.append(state_data)
                            logger.info(f"✅ Found state (JSON): {state_data['stateName']}")
                        else:
                            # Simple state data
                            state_data = {
                                'stateName': state_text,
                                'stateId': state_value
                            }
                            states_data.append(state_data)
                            logger.info(f"✅ Found state (simple): {state_text}")
                    except json.JSONDecodeError:
                        # Simple state data
                        state_data = {
                            'stateName': state_text,
                            'stateId': state_value
                        }
                        states_data.append(state_data)
                        logger.info(f"✅ Found state (simple): {state_text}")

            logger.info(f"✅ Extracted {len(states_data)} states")
            return states_data

        except Exception as e:
            logger.error(f"❌ Failed to extract states data: {e}")
            return []

    def select_state(self, state_data):
        """Select a specific state from the dropdown"""
        try:
            self.current_state = state_data
            logger.info(f"🔄 Selecting state: {state_data['stateName']}")

            state_select_element = self.driver.find_element(By.CSS_SELECTOR, "select.form-select.select")
            state_select = Select(state_select_element)

            # Try multiple methods to select the state
            success = False

            # Method 1: Try exact JSON match
            try:
                state_value = json.dumps(state_data, separators=(',', ':'))
                state_select.select_by_value(state_value)
                success = True
                logger.info(f"✅ Selected state by exact JSON: {state_data['stateName']}")
            except:
                pass

            # Method 2: Try by state ID
            if not success:
                try:
                    state_id = str(state_data.get('stateId', ''))
                    if state_id:
                        state_select.select_by_value(state_id)
                        success = True
                        logger.info(f"✅ Selected state by ID: {state_data['stateName']}")
                except:
                    pass

            # Method 3: Try by visible text
            if not success:
                try:
                    state_select.select_by_visible_text(state_data['stateName'])
                    success = True
                    logger.info(f"✅ Selected state by text: {state_data['stateName']}")
                except:
                    pass

            if not success:
                logger.error(f"❌ Failed to select state: {state_data['stateName']}")
                return False

            # Wait for districts to load
            time.sleep(2)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to select state {state_data['stateName']}: {e}")
            return False

    def extract_districts_data(self):
        """Extract districts data for the currently selected state"""
        try:
            if not self.current_state:
                logger.error("❌ current_state is None")
                return []

            logger.info(f"🔍 Extracting districts for {self.current_state['stateName']}...")

            # Wait for district dropdown to be populated
            time.sleep(2)

            # Find all select elements and get the district one (usually the second one)
            select_elements = self.driver.find_elements(By.CSS_SELECTOR, "select.form-select.select")

            if len(select_elements) < 2:
                logger.warning("❌ District dropdown not found")
                return []

            district_select = select_elements[1]  # Second select is usually districts
            district_options = district_select.find_elements(By.TAG_NAME, "option")[1:]  # Skip "Select District"

            districts_data = []
            for option in district_options:
                district_value = option.get_attribute("value")
                district_text = option.text.strip()

                if district_value and district_text and district_text != "Select District":
                    try:
                        # Try to parse as JSON (complex district data)
                        district_data = json.loads(district_value)
                        if isinstance(district_data, dict) and 'districtName' in district_data:
                            districts_data.append(district_data)
                            logger.info(f"✅ Found district (JSON): {district_data['districtName']}")
                        else:
                            # Simple district data
                            district_data = {
                                'districtName': district_text,
                                'districtId': district_value
                            }
                            districts_data.append(district_data)
                            logger.info(f"✅ Found district (simple): {district_text}")
                    except json.JSONDecodeError:
                        # Simple district data
                        district_data = {
                            'districtName': district_text,
                            'districtId': district_value
                        }
                        districts_data.append(district_data)
                        logger.info(f"✅ Found district (simple): {district_text}")

            logger.info(f"✅ Extracted {len(districts_data)} districts for {self.current_state['stateName']}")
            return districts_data

        except Exception as e:
            logger.error(f"❌ Failed to extract districts data: {e}")
            return []

    def select_district(self, district_data):
        """Select a specific district from the dropdown"""
        try:
            self.current_district = district_data
            logger.info(f"🔄 Selecting district: {district_data['districtName']}")

            # Wait for district dropdown to populate
            time.sleep(1)

            select_elements = self.driver.find_elements(By.CSS_SELECTOR, "select.form-select.select")

            if len(select_elements) < 2:
                raise Exception("District dropdown not found")

            district_select_element = select_elements[1]
            district_select = Select(district_select_element)

            # Try multiple methods to select the district
            success = False

            # Method 1: Try selecting by district ID
            try:
                district_id = str(district_data.get('districtId', ''))
                if district_id:
                    district_select.select_by_value(district_id)
                    success = True
                    logger.info(f"✅ Selected district by ID: {district_data['districtName']}")
            except Exception as e:
                logger.debug(f"Method 1 failed: {e}")

            # Method 2: Try JSON format
            if not success:
                try:
                    district_value = json.dumps(district_data, separators=(',', ':'))
                    district_select.select_by_value(district_value)
                    success = True
                    logger.info(f"✅ Selected district by JSON: {district_data['districtName']}")
                except Exception as e:
                    logger.debug(f"Method 2 failed: {e}")

            # Method 3: Try by visible text
            if not success:
                try:
                    district_select.select_by_visible_text(district_data['districtName'])
                    success = True
                    logger.info(f"✅ Selected district by text: {district_data['districtName']}")
                except Exception as e:
                    logger.debug(f"Method 3 failed: {e}")

            if not success:
                logger.error(f"❌ Failed to select district: {district_data['districtName']}")
                return False

            # Brief wait for any dynamic updates
            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to select district {district_data['districtName']}: {e}")
            return False

    def click_search_button(self):
        """Click the search button to load results"""
        try:
            # Try multiple selectors for the search button
            search_selectors = [
                "button.purpleBtn",
                "//button[contains(text(),'Search')]",
                "//button[contains(@class,'purpleBtn')]",
                "button[class*='purpleBtn']",
                "//button[normalize-space()='Search']"
            ]

            search_button = None
            working_selector = None

            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    if elements:
                        search_button = elements[0]
                        working_selector = selector
                        logger.info(f"✅ Found search button with selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not search_button:
                logger.error("❌ Search button not found with any selector")
                return False

            # Scroll to button and click
            try:
                # Scroll to the search button
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_button)
                time.sleep(1)

                # Try clicking with JavaScript if regular click fails
                try:
                    search_button.click()
                    logger.info(f"✅ Clicked search button using selector: {working_selector}")
                except Exception as click_error:
                    logger.warning(f"⚠️ Regular click failed, trying JavaScript click: {click_error}")
                    self.driver.execute_script("arguments[0].click();", search_button)
                    logger.info(f"✅ Clicked search button with JavaScript using selector: {working_selector}")

            except Exception as scroll_error:
                logger.error(f"❌ Failed to scroll to or click search button: {scroll_error}")
                return False

            # Wait for results to load
            time.sleep(3)

            # Verify results loaded by checking for common result indicators
            result_indicators = [
                ".accordion-body",
                ".accordion-item",
                "[class*='accordion']",
                "li:contains('Showing')",
                ".pagination",
                "table tbody tr"
            ]

            result_found = False
            for indicator in result_indicators:
                try:
                    if indicator.startswith("li:contains"):
                        # Special handling for text-based selectors
                        elements = self.driver.find_elements(By.XPATH, f"//li[contains(text(),'Showing')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)

                    if elements:
                        logger.info(f"✅ Results loaded - found indicator: {indicator}")
                        result_found = True
                        break
                except:
                    continue

            if not result_found:
                logger.warning("⚠️ No results found with any indicator - checking page content")
                page_text = self.driver.page_source[:2000]
                if "No records found" in page_text or "No data available" in page_text:
                    logger.info("📄 No schools found for this district")
                else:
                    logger.warning("⚠️ Results may not have loaded properly")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to click search button: {e}")
            return False

    def extract_school_count(self):
        """Extract total school count from the 'Showing X to Y of Z' element"""
        try:
            logger.info("🔢 Extracting school count...")

            # Try multiple methods to find the count element
            count_selectors = [
                "//li[contains(text(),'Showing')]//label",
                "//p[contains(text(),'Showing')]//label",
                "//label[contains(text(),'Showing')]",
                "//li[contains(text(),'Showing')]",
                "//p[contains(text(),'Showing')]",
                ".pagination-info",
                ".result-count"
            ]

            count_text = None
            working_selector = None

            for selector in count_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    if elements:
                        count_text = elements[0].text.strip()
                        working_selector = selector
                        logger.info(f"✅ Found count element with selector: {selector}")
                        logger.info(f"   Count text: '{count_text}'")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not count_text:
                logger.warning("⚠️ Count element not found with any selector")
                # Try to find it in page source as fallback
                page_source = self.driver.page_source
                showing_pattern = r'Showing\s+\d+\s+to\s+\d+\s+of\s+(\d+)'
                match = re.search(showing_pattern, page_source, re.IGNORECASE)
                if match:
                    total_count = int(match.group(1))
                    logger.info(f"✅ Found count in page source: {total_count}")
                    return total_count
                else:
                    logger.warning("⚠️ No count found in page source either")
                    return 0

            # Extract the total count using regex
            # Pattern: "Showing X to Y of Z" -> extract Z
            count_pattern = r'Showing\s+\d+\s+to\s+\d+\s+of\s+(\d+)'
            match = re.search(count_pattern, count_text, re.IGNORECASE)

            if match:
                total_count = int(match.group(1))
                logger.info(f"✅ Extracted school count: {total_count}")
                return total_count
            else:
                # Try alternative patterns
                alternative_patterns = [
                    r'of\s+(\d+)',  # Just "of X"
                    r'total[:\s]*(\d+)',  # "total: X" or "total X"
                    r'(\d+)\s+schools?',  # "X schools"
                    r'(\d+)\s+results?'   # "X results"
                ]

                for pattern in alternative_patterns:
                    match = re.search(pattern, count_text, re.IGNORECASE)
                    if match:
                        total_count = int(match.group(1))
                        logger.info(f"✅ Extracted school count with alternative pattern: {total_count}")
                        return total_count

                logger.warning(f"⚠️ Could not parse count from text: '{count_text}'")
                return 0

        except Exception as e:
            logger.error(f"❌ Failed to extract school count: {e}")
            return 0

    def save_state_counts_to_csv(self, state_name, district_counts):
        """Save district counts for a state to CSV file"""
        try:
            # Create filename
            clean_state_name = state_name.replace(' ', '_').replace('&', 'and').replace('/', '_').upper()
            filename = f"{clean_state_name}_school_counts.csv"

            # Prepare data
            csv_data = []
            for district_name, count in district_counts.items():
                csv_data.append({
                    'State': state_name,
                    'District': district_name,
                    'Total_Schools': count
                })

            # Write to CSV
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False)

            logger.info(f"✅ Saved {len(csv_data)} district counts to {filename}")
            return filename

        except Exception as e:
            logger.error(f"❌ Failed to save CSV for {state_name}: {e}")
            return None

    def process_single_state(self, state_data):
        """Process a single state to count schools in all its districts"""
        try:
            state_name = state_data['stateName']
            logger.info(f"\n{'='*80}")
            logger.info(f"🏛️ PROCESSING STATE: {state_name}")
            logger.info(f"{'='*80}")

            # Select the state
            if not self.select_state(state_data):
                logger.error(f"❌ Failed to select state: {state_name}")
                return False

            # Get districts for this state
            districts = self.extract_districts_data()
            if not districts:
                logger.warning(f"⚠️ No districts found for {state_name}")
                return False

            total_districts = len(districts)
            logger.info(f"📍 Found {total_districts} districts in {state_name}")

            # Process each district
            district_counts = {}
            successful_districts = 0

            for district_index, district in enumerate(districts, 1):
                district_name = district['districtName']
                logger.info(f"\n🏘️ Processing district {district_index}/{total_districts}: {district_name}")

                try:
                    # Select district
                    if self.select_district(district):
                        # Click search to load results
                        if self.click_search_button():
                            # Extract school count
                            school_count = self.extract_school_count()
                            district_counts[district_name] = school_count
                            successful_districts += 1

                            logger.info(f"✅ {district_name}: {school_count} schools")
                        else:
                            logger.error(f"❌ Failed to click search for {district_name}")
                            district_counts[district_name] = 0
                    else:
                        logger.error(f"❌ Failed to select district: {district_name}")
                        district_counts[district_name] = 0

                except Exception as district_error:
                    logger.error(f"❌ Error processing district {district_name}: {district_error}")
                    district_counts[district_name] = 0

                # Brief pause between districts
                time.sleep(1)

            # Save results to CSV
            csv_file = self.save_state_counts_to_csv(state_name, district_counts)

            # Summary
            total_schools = sum(district_counts.values())
            logger.info(f"\n📊 STATE SUMMARY: {state_name}")
            logger.info(f"   🏘️ Districts processed: {successful_districts}/{total_districts}")
            logger.info(f"   🏫 Total schools: {total_schools}")
            logger.info(f"   📝 CSV file: {csv_file}")

            return True

        except Exception as e:
            logger.error(f"❌ Error processing state {state_name}: {e}")
            return False

    def run_school_counting(self, target_states=None):
        """Main function to run school counting for all states or specific states"""
        try:
            logger.info("🚀 STARTING SCHOOL COUNTING TOOL")
            logger.info("="*80)

            # Setup driver and navigate
            if not self.setup_driver():
                logger.error("❌ Failed to setup driver")
                return False

            if not self.navigate_to_portal():
                logger.error("❌ Failed to navigate to portal")
                return False

            # Extract all states
            states = self.extract_states_data()
            if not states:
                logger.error("❌ No states extracted. Cannot proceed.")
                return False

            # Filter states if target_states specified
            if target_states:
                if isinstance(target_states, str):
                    target_states = [target_states]
                states = [state for state in states if state['stateName'] in target_states]
                logger.info(f"🎯 Filtered to target states: {[s['stateName'] for s in states]}")

            total_states = len(states)
            logger.info(f"🎯 Processing {total_states} states")

            # Process each state
            successful_states = 0
            failed_states = []

            for state_index, state in enumerate(states, 1):
                try:
                    logger.info(f"\n🔄 Processing state {state_index}/{total_states}")

                    if self.process_single_state(state):
                        successful_states += 1
                    else:
                        failed_states.append(state['stateName'])

                except Exception as state_error:
                    logger.error(f"❌ Critical error processing state {state['stateName']}: {state_error}")
                    failed_states.append(state['stateName'])

                # Brief pause between states
                time.sleep(2)

            # Final summary
            logger.info(f"\n{'='*80}")
            logger.info("🎯 SCHOOL COUNTING COMPLETED")
            logger.info(f"{'='*80}")
            logger.info(f"✅ Successful states: {successful_states}/{total_states}")
            logger.info(f"❌ Failed states: {len(failed_states)}")
            if failed_states:
                logger.info(f"   Failed: {', '.join(failed_states)}")
            logger.info("📝 Check individual state CSV files for detailed results")

            return True

        except Exception as e:
            logger.error(f"❌ Critical error in school counting: {e}")
            return False

        finally:
            # Cleanup
            if self.driver:
                self.driver.quit()
                logger.info("🔒 Browser driver closed")

def main():
    """Main function for school counting tool"""
    try:
        print("🚀 SCHOOL COUNTING TOOL")
        print("Counts total schools in each district of every state")
        print("Generates CSV reports with State, District, Total_Schools")
        print()

        # Create and run the counting tool
        counter = SchoolCountingTool()

        # Option to run for specific states (for testing)
        # target_states = ["GOA", "DELHI"]  # Uncomment and modify for specific states
        target_states = None  # Process all states

        success = counter.run_school_counting(target_states)

        if success:
            print("\n✅ School counting completed successfully!")
            print("📝 Check the generated CSV files for results")
        else:
            print("\n❌ School counting failed. Check logs for details.")

    except Exception as e:
        print(f"❌ Critical error: {e}")
        print("Please check the logs above for details")

if __name__ == "__main__":
    main()
