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

            # Wait a moment for results to load
            time.sleep(3)

            # Try to set results per page to 100
            self.set_results_per_page_to_100()

            # Scroll to bottom of page to ensure all content is loaded
            self.scroll_to_bottom()

            return True

        except Exception as e:
            logger.error(f"❌ Error in enhanced search button click: {e}")
            return False

    def set_results_per_page_to_100(self):
        """Set results per page to 100 for maximum efficiency"""
        try:
            logger.info("🔧 Setting results per page to 100...")

            # Wait for the results per page dropdown to be available
            results_per_page_select = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.form-select.w11110"))
            )

            # Create Select object and choose 100
            select = Select(results_per_page_select)
            select.select_by_value("100")

            logger.info("✅ Successfully set results per page to 100")
            time.sleep(2)  # Wait for page to update
            return True

        except Exception as e:
            logger.warning(f"⚠️ Failed to set results per page to 100: {e}")
            return False

    def scroll_to_bottom(self):
        """Scroll directly to bottom of page to ensure all content is loaded"""
        try:
            logger.info("🔄 Scrolling to bottom of page...")

            # Scroll to bottom of page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for any dynamic content to load

            logger.info("✅ Scrolled to bottom of page")
            return True

        except Exception as e:
            logger.warning(f"⚠️ Error scrolling to bottom: {e}")
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
                        logger.info("📄 Next button is disabled (parent li has disabled class) - no more pages")
                        return False

                except Exception as parent_check_error:
                    logger.debug(f"Could not check parent element: {parent_check_error}")
                    # Continue with other checks

                # Additional checks for button state
                button_classes = next_button.get_attribute("class") or ""
                if "disabled" in button_classes.lower():
                    logger.info("📄 Next button is disabled (has disabled class) - no more pages")
                    return False

                # Check for disabled attribute
                if next_button.get_attribute("disabled"):
                    logger.info("📄 Next button has disabled attribute - no more pages")
                    return False

                # Check if button is enabled (basic Selenium check)
                if not next_button.is_enabled():
                    logger.info("📄 Next button is not enabled - no more pages")
                    return False

                # Scroll to button to ensure it's visible
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(1)

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
                        # Wait for page to load after successful click
                        time.sleep(2)
                        return True
                    else:
                        logger.warning(f"All click methods failed on attempt {attempt + 1}")

                except Exception as scroll_error:
                    logger.warning(f"Failed to scroll to next button on attempt {attempt + 1}: {scroll_error}")

                # Wait before retry
                if attempt < max_retries - 1:
                    time.sleep(1)

            except Exception as e:
                logger.warning(f"Error in enhanced_click_next_page attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)

        logger.warning(f"Failed to click next page button after {max_retries} attempts")
        return False

    def extract_schools_basic_data_enhanced(self):
        """Enhanced schools extraction with improved pagination and no smooth scrolling"""
        try:
            schools_data = []
            page_number = 1
            max_pages = 100  # Increased safety limit

            logger.info("🔍 Starting enhanced schools data extraction with robust pagination...")

            while page_number <= max_pages:
                logger.info(f"📄 Processing page {page_number}")

                # Scroll to bottom to ensure all content is loaded
                self.scroll_to_bottom()

                # Extract schools from current page using base method
                page_schools = self.base_scraper.extract_schools_from_current_page()
                schools_data.extend(page_schools)

                logger.info(f"   ✅ Extracted {len(page_schools)} schools from page {page_number}")
                logger.info(f"   📊 Total schools so far: {len(schools_data)}")

                # Try to go to next page using enhanced method with retry
                logger.info(f"   🔄 Checking for next page after page {page_number}...")
                if not self.enhanced_click_next_page():
                    logger.info(f"📄 No more pages available after page {page_number}")
                    break

                page_number += 1

                # Wait for next page to load completely
                time.sleep(3)

                # Additional check: verify we're on a new page by checking if content changed
                try:
                    # Wait for new content to load
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".accordion-body, .accordion-item, [class*='accordion']")) > 0
                    )
                except Exception as wait_error:
                    logger.warning(f"Timeout waiting for new page content: {wait_error}")
                    # Continue anyway as content might already be loaded

            if page_number > max_pages:
                logger.warning(f"⚠️ Reached maximum page limit ({max_pages}). There might be more data available.")

            logger.info(f"✅ Enhanced extraction completed: {len(schools_data)} total schools from {page_number} pages")
            return schools_data

        except Exception as e:
            logger.error(f"Failed to extract schools data with enhanced method: {e}")
            return []

    def process_single_state_enhanced(self, target_state):
        """Enhanced processing for a single state"""
        try:
            logger.info(f"🎯 Enhanced processing for state: {target_state['stateName']}")

            # Set current state
            self.current_state = target_state
            self.base_scraper.current_state = target_state

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

                try:
                    # Select district
                    if self.select_district(district):
                        # Enhanced search with results per page optimization
                        if self.enhanced_click_search_button():
                            # Extract schools using enhanced method
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

            # Save data to CSV
            self.base_scraper.save_state_data_to_csv(target_state['stateName'])

            total_schools = (len(self.state_schools_with_links.get(target_state['stateName'], [])) +
                           len(self.state_schools_no_links.get(target_state['stateName'], [])))
            logger.info(f"✅ Enhanced processing completed for {target_state['stateName']}: {total_schools} total schools")

            return True

        except Exception as e:
            logger.error(f"❌ Error in enhanced single state processing: {e}")
            return False

    def process_single_state_single_district(self, target_state, target_district):
        """Enhanced processing for a single state and single district"""
        try:
            logger.info(f"🎯 Enhanced processing for district: {target_district['districtName']} in {target_state['stateName']}")

            # Set current state and district
            self.current_state = target_state
            self.current_district = target_district
            self.base_scraper.current_state = target_state
            self.base_scraper.current_district = target_district

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

            # Save data to CSV
            self.base_scraper.save_state_data_to_csv(target_state['stateName'])

            logger.info(f"✅ Enhanced processing completed for {target_district['districtName']}: {len(schools_data)} schools")

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
