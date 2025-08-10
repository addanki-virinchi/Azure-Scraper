#!/usr/bin/env python3
"""
Standalone Phase 2 Processor - Independent CSV-based Phase 2 Processing
- Accepts Phase 1 CSV file as input (specify file path in code)
- Skips Phase 1 entirely - only performs Phase 2 processing
- Visits each "know_more_link" URL to extract detailed school information
- Consolidates original Phase 1 data with newly extracted Phase 2 data
- Creates output CSV with incremental writing for crash recovery
- Handles cases where schools may not have valid "know_more_link" URLs
"""

import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
from datetime import datetime
import os
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== CONFIGURATION SECTION =====
# Specify the Phase 1 CSV file to process
INPUT_CSV_FILE = "GOA_phase1_complete_20250809_103414.csv"  # Change this to your Phase 1 CSV file

# Optional: Limit processing for testing (set to None for all records)
MAX_RECORDS_TO_PROCESS = None  # Set to a number like 10 for testing, None for all

# ===== END CONFIGURATION SECTION =====

class StandalonePhase2Processor:
    def __init__(self, input_csv_file):
        self.input_csv_file = input_csv_file
        self.driver = None
        self.processed_count = 0
        self.success_count = 0
        self.fail_count = 0
        
        # Output file setup
        self.output_csv_file = None
        self.csv_headers_written = False
        
        # Extract state name from input file
        self.state_name = self.extract_state_name_from_filename(input_csv_file)
        
        # Setup output CSV file
        self.setup_output_csv()

    def extract_state_name_from_filename(self, filename):
        """Extract state name from CSV filename"""
        try:
            basename = os.path.basename(filename)
            
            # Extract state name from different naming patterns
            if "_phase1_complete_" in basename:
                state_name = basename.split("_phase1_complete_")[0]
            elif "_with_links_" in basename:
                state_name = basename.split("_with_links_")[0]
            else:
                state_name = basename.split("_")[0]
            
            # Convert back to readable format
            state_name = state_name.replace("_", " ").replace("and", "&")
            return state_name
            
        except Exception as e:
            logger.error(f"❌ Error extracting state name from {filename}: {e}")
            return "UNKNOWN_STATE"

    def setup_output_csv(self):
        """Setup output CSV file for Phase 2 complete data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_state = self.state_name.replace(' ', '_').replace('&', 'and').replace('/', '_').upper()
            
            self.output_csv_file = f"{clean_state}_phase2_complete_{timestamp}.csv"
            self.csv_headers_written = False
            
            logger.info(f"📝 Output file will be: {self.output_csv_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up output CSV: {e}")
            return False

    def write_to_output_csv(self, combined_data):
        """Write a single school record to output CSV immediately (incremental writing)"""
        try:
            if not self.output_csv_file:
                logger.warning("⚠️ Output CSV file not setup")
                return False
            
            # Convert to DataFrame for consistent handling
            df = pd.DataFrame([combined_data])
            
            # Write headers if first record
            if not self.csv_headers_written:
                df.to_csv(self.output_csv_file, mode='w', index=False, header=True)
                self.csv_headers_written = True
                logger.info(f"📝 Created output CSV with headers: {self.output_csv_file}")
            else:
                # Append data without headers
                df.to_csv(self.output_csv_file, mode='a', index=False, header=False)
            
            logger.debug(f"📝 Appended 1 record to output CSV")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error writing to output CSV: {e}")
            return False

    def check_already_processed(self, udise_code):
        """Check if a school has already been processed (for crash recovery)"""
        try:
            if not os.path.exists(self.output_csv_file):
                return False
            
            # Read existing output file to check for this UDISE code
            existing_df = pd.read_csv(self.output_csv_file)
            if 'udise_code' in existing_df.columns:
                return udise_code in existing_df['udise_code'].values
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking if already processed: {e}")
            return False

    def setup_driver(self):
        """Initialize Chrome browser driver with optimized settings for Phase 2 processing"""
        try:
            # Setup Chrome options for Phase 2 data extraction
            options = uc.ChromeOptions()
            
            # Core stability options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Performance optimizations (KEEP JavaScript enabled for dynamic content)
            options.add_argument("--disable-images")  # Speed optimization
            options.add_argument("--disable-plugins")  # Speed optimization
            
            # Memory and resource optimizations
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            
            self.driver = uc.Chrome(options=options)
            self.driver.maximize_window()
            
            # Balanced timeouts for Phase 2 processing
            self.driver.implicitly_wait(5)
            self.driver.set_page_load_timeout(25)
            
            logger.info("✅ Chrome browser driver initialized for standalone Phase 2 processing")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome driver: {e}")
            logger.error("Please ensure Chrome browser is installed and updated")
            return False

    def load_phase1_data(self):
        """Load and validate Phase 1 CSV data"""
        try:
            if not os.path.exists(self.input_csv_file):
                logger.error(f"❌ Input CSV file not found: {self.input_csv_file}")
                return None
            
            # Load CSV data
            df = pd.read_csv(self.input_csv_file)
            logger.info(f"📊 Loaded {len(df)} total records from {self.input_csv_file}")
            
            # Check for required columns
            required_columns = ['know_more_link']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                logger.info(f"Available columns: {list(df.columns)}")
                return None
            
            # Filter schools with valid know_more_link URLs
            valid_schools = df[
                df['know_more_link'].notna() & 
                (df['know_more_link'] != 'N/A') & 
                (df['know_more_link'].str.contains('http', na=False))
            ].copy()
            
            logger.info(f"📊 Found {len(valid_schools)} schools with valid know_more_link URLs")
            
            if len(valid_schools) == 0:
                logger.warning("⚠️ No schools with valid know_more_link URLs found")
                return pd.DataFrame()
            
            return valid_schools
            
        except Exception as e:
            logger.error(f"❌ Error loading Phase 1 data: {e}")
            return None

    def extract_focused_data(self, url, max_retries=2):
        """Extract comprehensive data from school detail page with immediate browser refresh"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 Navigating to school detail page: {url}")
                
                # IMMEDIATE BROWSER REFRESH: Navigate and immediately refresh
                try:
                    # Step 1: Navigate to the URL
                    self.driver.get(url)
                    logger.debug(f"   📍 Initial navigation completed")
                    
                    # Step 2: IMMEDIATE REFRESH as requested
                    logger.debug(f"   🔄 Performing IMMEDIATE browser refresh...")
                    self.driver.refresh()
                    
                    # Step 3: Wait for refresh to complete
                    time.sleep(4)  # Increased wait for refresh completion
                    
                    # Step 4: Verify page is loaded
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                    # Step 5: Additional wait for dynamic content
                    time.sleep(2)
                    
                    logger.debug(f"   ✅ Page refreshed and loaded successfully")
                    
                except Exception as e:
                    logger.error(f"   ❌ Navigation/refresh error: {e}")
                    if attempt < max_retries - 1:
                        continue
                    return None
                
                # Initialize comprehensive data structure for all extracted fields
                data = {
                    # School identification
                    'detail_school_name': 'N/A',
                    'extraction_timestamp': datetime.now().isoformat(),

                    # Basic Details section
                    'academic_year': 'N/A',
                    'location': 'N/A',
                    'school_category': 'N/A',
                    'class_from': 'N/A',
                    'class_to': 'N/A',
                    'class_range': 'N/A',
                    'school_type': 'N/A',
                    'year_of_establishment': 'N/A',
                    'national_management': 'N/A',
                    'state_management': 'N/A',
                    'affiliation_board_sec': 'N/A',
                    'affiliation_board_hsec': 'N/A',

                    # Student Enrollment section
                    'total_students': 'N/A',
                    'total_boys': 'N/A',
                    'total_girls': 'N/A',
                    'enrollment_class_range': 'N/A',

                    # Teacher section
                    'total_teachers': 'N/A',
                    'male_teachers': 'N/A',
                    'female_teachers': 'N/A'
                }
                
                # Get page content for extraction
                page_text = self.driver.page_source
                
                # Extract school ID for verification
                url_school_id = re.search(r'/(\d+)/\d+$', url)
                expected_school_id = url_school_id.group(1) if url_school_id else "unknown"
                
                logger.debug(f"   📄 Expected school ID: {expected_school_id}")
                logger.debug(f"   📄 Page content length: {len(page_text)} characters")
                
                # Continue with data extraction in the next part...
                return self.extract_data_from_page(data, page_text, expected_school_id)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract data from {url} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"⏳ Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    return None
        
        return None

    def extract_data_from_page(self, data, page_text, expected_school_id):
        """Extract data from the loaded page"""
        try:
            # 1. BASIC DETAILS SECTION - Extract from .innerPad div with .schoolInfoCol elements
            try:
                logger.debug(f"   📋 Extracting Basic Details...")

                # Try to find Basic Details section using Selenium elements first
                try:
                    basic_details_elements = self.driver.find_elements(By.CSS_SELECTOR, ".innerPad .schoolInfoCol")
                    if basic_details_elements:
                        logger.debug(f"   Found {len(basic_details_elements)} basic detail elements")

                        # Define field mapping for proper extraction
                        basic_fields_map = {
                            'Location': 'location',
                            'School Category': 'school_category',
                            'Class From': 'class_from',
                            'Class To': 'class_to',
                            'School Type': 'school_type',
                            'Year of Establishment': 'year_of_establishment',
                            'National Management': 'national_management',
                            'State Management': 'state_management',
                            'Affiliation Board Sec.': 'affiliation_board_sec',
                            'Affiliation Board HSec.': 'affiliation_board_hsec'
                        }

                        for element in basic_details_elements:
                            try:
                                # Find the title element within this schoolInfoCol
                                title_element = element.find_element(By.CSS_SELECTOR, ".title p.fw-600")
                                title_text = title_element.text.strip()

                                # Find the corresponding value element
                                value_element = element.find_element(By.CSS_SELECTOR, ".blueCol")
                                value_text = value_element.text.strip()

                                # Map the field to our data structure
                                if title_text in basic_fields_map and value_text:
                                    field_key = basic_fields_map[title_text]
                                    data[field_key] = value_text
                                    logger.debug(f"   Extracted {title_text}: {value_text}")

                            except Exception as e:
                                logger.debug(f"   Error processing basic detail element: {e}")
                                continue

                except Exception as e:
                    logger.debug(f"   Error finding basic details elements: {e}")

                # Fallback: Use regex patterns for basic details
                if data['location'] == 'N/A':
                    location_match = re.search(r'Location</p></div><div[^>]*class="blueCol">([^<]+)', page_text, re.IGNORECASE)
                    if location_match:
                        data['location'] = location_match.group(1).strip()

                if data['school_category'] == 'N/A':
                    category_match = re.search(r'School Category</p></div><div[^>]*class="blueCol">([^<]+)', page_text, re.IGNORECASE)
                    if category_match:
                        data['school_category'] = category_match.group(1).strip()

                if data['school_type'] == 'N/A':
                    type_match = re.search(r'School Type</p></div><div[^>]*class="blueCol">([^<]+)', page_text, re.IGNORECASE)
                    if type_match:
                        data['school_type'] = type_match.group(1).strip()

                if data['year_of_establishment'] == 'N/A':
                    year_match = re.search(r'Year of Establishment</p></div><div[^>]*class="blueCol">([^<]+)', page_text, re.IGNORECASE)
                    if year_match:
                        data['year_of_establishment'] = year_match.group(1).strip()

                # Combine class range if both from and to are found
                if data['class_from'] != 'N/A' and data['class_to'] != 'N/A':
                    data['class_range'] = f"{data['class_from']} To {data['class_to']}"

            except Exception as e:
                logger.debug(f"   Error extracting basic details: {e}")

            # 2. STUDENT ENROLLMENT SECTION
            try:
                logger.debug(f"   👥 Extracting Student Enrollment...")

                # Try to find Student Enrollment section using Selenium elements first
                try:
                    h3_value_elements = self.driver.find_elements(By.CSS_SELECTOR, ".bg-white .H3Value")
                    if h3_value_elements:
                        logger.debug(f"   Found {len(h3_value_elements)} H3Value elements")

                        for element in h3_value_elements:
                            try:
                                # Get the parent container to find the label
                                parent = element.find_element(By.XPATH, "..")
                                parent_text = parent.text.strip().lower()
                                value = element.text.strip()

                                if value.isdigit():
                                    if "total students" in parent_text:
                                        data['total_students'] = value
                                        logger.debug(f"   Found Total Students: {value}")
                                    elif "boys" in parent_text and "total" not in parent_text:
                                        data['total_boys'] = value
                                        logger.debug(f"   Found Boys: {value}")
                                    elif "girls" in parent_text:
                                        data['total_girls'] = value
                                        logger.debug(f"   Found Girls: {value}")
                            except Exception as e:
                                logger.debug(f"   Error processing H3Value element: {e}")
                                continue
                except Exception as e:
                    logger.debug(f"   Error finding H3Value elements: {e}")

                # Fallback: Use regex patterns for student enrollment
                if data['total_students'] == 'N/A':
                    total_students_patterns = [
                        r'Total Students[^>]*</p>\s*<p[^>]*class="H3Value[^>]*>\s*(\d+)\s*</p>',
                        r'Total Students[^>]*>\s*(\d+)\s*<',
                        r'Total Students[:\s]*(\d+)'
                    ]
                    for pattern in total_students_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            data['total_students'] = match.group(1).strip()
                            logger.debug(f"   Found Total Students (regex): {data['total_students']}")
                            break

            except Exception as e:
                logger.debug(f"   Error extracting student enrollment: {e}")

            # 3. TEACHER SECTION - Enhanced extraction for the specific HTML structure
            try:
                logger.debug(f"   👨‍🏫 Extracting Teacher data...")

                # Method 1: Look for teacher section with specific structure
                try:
                    # Find teacher section by looking for "Teacher" heading
                    teacher_sections = self.driver.find_elements(By.XPATH, "//h2[contains(text(), 'Teacher')]/following-sibling::div")

                    if teacher_sections:
                        teacher_section = teacher_sections[0]
                        logger.debug(f"   Found teacher section")

                        # Look for H3Value elements within the teacher section
                        h3_elements = teacher_section.find_elements(By.CSS_SELECTOR, ".H3Value")

                        for element in h3_elements:
                            try:
                                # Get the preceding sibling or parent to find the label
                                parent_li = element.find_element(By.XPATH, "ancestor::li[1]")
                                label_text = parent_li.text.strip().lower()
                                value = element.text.strip()

                                if value.isdigit():
                                    if "total teachers" in label_text:
                                        data['total_teachers'] = value
                                        logger.debug(f"   Found Total Teachers: {value}")
                                    elif "male" in label_text and "total" not in label_text and "female" not in label_text:
                                        data['male_teachers'] = value
                                        logger.debug(f"   Found Male Teachers: {value}")
                                    elif "female" in label_text and "male" not in label_text:
                                        data['female_teachers'] = value
                                        logger.debug(f"   Found Female Teachers: {value}")
                            except Exception as e:
                                logger.debug(f"   Error processing teacher element: {e}")
                                continue

                except Exception as e:
                    logger.debug(f"   Error finding teacher section: {e}")

                # Method 2: Fallback - Look for any H3Value elements with teacher context
                if data['total_teachers'] == 'N/A':
                    try:
                        all_h3_elements = self.driver.find_elements(By.CSS_SELECTOR, ".H3Value")

                        for i, element in enumerate(all_h3_elements):
                            try:
                                value = element.text.strip()
                                if not value.isdigit():
                                    continue

                                # Get surrounding context
                                parent_text = ""
                                try:
                                    # Try multiple parent levels to find context
                                    for level in ["../..", "..", "../.."]:
                                        try:
                                            context_element = element.find_element(By.XPATH, level)
                                            context_text = context_element.text.lower()
                                            if "teacher" in context_text:
                                                parent_text = context_text
                                                break
                                        except:
                                            continue
                                except:
                                    pass

                                # Also check if this is in a teacher-related section by looking at nearby elements
                                if not parent_text:
                                    try:
                                        # Look for teacher-related text in nearby elements
                                        nearby_elements = self.driver.find_elements(By.XPATH, f"//p[contains(@class, 'H3Value')][{i+1}]/preceding::*[position()<=5] | //p[contains(@class, 'H3Value')][{i+1}]/following::*[position()<=5]")
                                        for nearby in nearby_elements:
                                            if "teacher" in nearby.text.lower():
                                                parent_text = nearby.text.lower()
                                                break
                                    except:
                                        pass

                                # Assign based on context and position
                                if "total teachers" in parent_text:
                                    data['total_teachers'] = value
                                    logger.debug(f"   Found Total Teachers (fallback): {value}")
                                elif "male" in parent_text and "teacher" in parent_text:
                                    data['male_teachers'] = value
                                    logger.debug(f"   Found Male Teachers (fallback): {value}")
                                elif "female" in parent_text and "teacher" in parent_text:
                                    data['female_teachers'] = value
                                    logger.debug(f"   Found Female Teachers (fallback): {value}")
                                elif "teacher" in parent_text and data['total_teachers'] == 'N/A':
                                    # If we find a teacher-related number and don't have total yet, assume it's total
                                    data['total_teachers'] = value
                                    logger.debug(f"   Found Total Teachers (assumed): {value}")

                            except Exception as e:
                                logger.debug(f"   Error processing H3Value element {i}: {e}")
                                continue

                    except Exception as e:
                        logger.debug(f"   Error in fallback teacher extraction: {e}")

                # Method 3: Regex fallback for teacher data
                if data['total_teachers'] == 'N/A' or data['male_teachers'] == 'N/A' or data['female_teachers'] == 'N/A':
                    try:
                        # Look for teacher data in the page source with regex
                        teacher_patterns = [
                            (r'Total Teachers[^>]*</p>\s*<p[^>]*class="H3Value[^>]*>\s*(\d+)\s*</p>', 'total_teachers'),
                            (r'Male[^>]*</p>\s*<p[^>]*class="H3Value[^>]*>\s*(\d+)\s*</p>', 'male_teachers'),
                            (r'Female[^>]*</p>\s*<p[^>]*class="H3Value[^>]*>\s*(\d+)\s*</p>', 'female_teachers'),
                        ]

                        for pattern, field_name in teacher_patterns:
                            if data[field_name] == 'N/A':
                                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                                if match:
                                    data[field_name] = match.group(1).strip()
                                    logger.debug(f"   Found {field_name} (regex): {data[field_name]}")

                    except Exception as e:
                        logger.debug(f"   Error in regex teacher extraction: {e}")

            except Exception as e:
                logger.debug(f"   Error extracting teacher data: {e}")

            # 4. SCHOOL NAME - Extract from page title, header, or breadcrumb
            try:
                logger.debug(f"   🏫 Extracting School Name...")

                # Method 1: Try to get school name from page title
                page_title = self.driver.title
                if page_title and page_title != "Know Your School" and "UDISE" not in page_title:
                    clean_title = page_title.replace("Know Your School", "").replace("-", "").strip()
                    if clean_title and len(clean_title) > 3:
                        data['detail_school_name'] = clean_title
                        logger.debug(f"   Found school name from title: {clean_title}")

                # Fallback: Use school ID as identifier
                if data['detail_school_name'] == 'N/A':
                    data['detail_school_name'] = f"School_ID_{expected_school_id}"
                    logger.debug(f"   Using school ID as name: {data['detail_school_name']}")

            except Exception as e:
                logger.debug(f"   Error extracting school name: {e}")
                data['detail_school_name'] = f"School_ID_{expected_school_id}"

            # COMPREHENSIVE DATA VALIDATION AND STATUS INDICATORS
            try:
                logger.debug(f"   📊 Validating extracted data...")

                # Count successfully extracted fields
                extracted_fields = 0
                critical_fields = 0

                # Critical fields for Phase 2
                if data['total_students'] != 'N/A':
                    critical_fields += 1
                    extracted_fields += 1
                if data['total_teachers'] != 'N/A':
                    critical_fields += 1
                    extracted_fields += 1
                if data['detail_school_name'] != 'N/A' and not data['detail_school_name'].startswith('School_ID_'):
                    extracted_fields += 1

                # Additional fields
                additional_fields = [
                    'total_boys', 'total_girls', 'male_teachers', 'female_teachers',
                    'school_category', 'school_type', 'location', 'academic_year'
                ]
                for field in additional_fields:
                    if data[field] != 'N/A':
                        extracted_fields += 1

                # Add extraction status indicators
                data['extraction_status'] = 'SUCCESS' if critical_fields >= 2 else 'PARTIAL' if critical_fields >= 1 else 'FAILED'
                data['fields_extracted'] = extracted_fields
                data['critical_fields_extracted'] = critical_fields

                # Validation summary
                if critical_fields >= 2:
                    logger.info(f"✅ EXCELLENT extraction")
                    logger.info(f"   🎯 Critical fields: {critical_fields}/2, Total fields: {extracted_fields}")
                    logger.info(f"   👥 Students: {data['total_students']}, Teachers: {data['total_teachers']}")
                elif critical_fields >= 1:
                    logger.info(f"⚠️ PARTIAL extraction")
                    logger.info(f"   🎯 Critical fields: {critical_fields}/2, Total fields: {extracted_fields}")
                else:
                    logger.warning(f"❌ FAILED extraction")
                    logger.warning(f"   🎯 Critical fields: {critical_fields}/2, Total fields: {extracted_fields}")

            except Exception as e:
                logger.debug(f"   Error in data validation: {e}")
                data['extraction_status'] = 'ERROR'
                data['fields_extracted'] = 0
                data['critical_fields_extracted'] = 0

            return data

        except Exception as e:
            logger.error(f"   ❌ Error in extract_data_from_page: {e}")
            return None

    def process_schools(self):
        """Main processing method - processes all schools from Phase 1 CSV"""
        try:
            logger.info(f"\n🚀 STARTING STANDALONE PHASE 2 PROCESSING")
            logger.info(f"="*80)
            logger.info(f"📁 Input file: {self.input_csv_file}")
            logger.info(f"🏛️ State: {self.state_name}")
            logger.info(f"📝 Output file: {self.output_csv_file}")
            logger.info(f"="*80)

            # Load Phase 1 data
            schools_df = self.load_phase1_data()
            if schools_df is None or len(schools_df) == 0:
                logger.error("❌ No valid Phase 1 data to process")
                return False

            # Apply record limit if specified
            if MAX_RECORDS_TO_PROCESS:
                schools_df = schools_df.head(MAX_RECORDS_TO_PROCESS)
                logger.info(f"🔢 Limited to {MAX_RECORDS_TO_PROCESS} records for testing")

            total_schools = len(schools_df)
            logger.info(f"🎯 Processing {total_schools} schools with know_more_link URLs")

            # Setup browser driver
            if not self.setup_driver():
                logger.error("❌ Failed to setup browser driver")
                return False

            # Process each school individually
            start_time = time.time()

            for idx, (_, school) in enumerate(schools_df.iterrows(), 1):
                try:
                    school_name = school.get('school_name', f'School_{idx}')
                    udise_code = school.get('udise_code', f'UDISE_{idx}')
                    know_more_link = school.get('know_more_link', '')

                    logger.info(f"\n🏫 Processing school {idx}/{total_schools}: {school_name}")
                    logger.info(f"   📋 UDISE Code: {udise_code}")

                    # Check if already processed (crash recovery)
                    if self.check_already_processed(udise_code):
                        logger.info(f"   ⏭️ Already processed - skipping")
                        continue

                    # Extract Phase 2 data
                    extracted_data = self.extract_focused_data(know_more_link)

                    if extracted_data:
                        # Combine original Phase 1 data with extracted Phase 2 data
                        combined_data = school.to_dict()
                        combined_data.update(extracted_data)

                        # Remove unwanted columns
                        unwanted_columns = ['last_modified', 'source_url']
                        for col in unwanted_columns:
                            combined_data.pop(col, None)

                        # Write immediately to output CSV (incremental writing)
                        if self.write_to_output_csv(combined_data):
                            self.success_count += 1
                            logger.info(f"   ✅ Successfully processed and saved")
                        else:
                            logger.error(f"   ❌ Failed to save to CSV")
                            self.fail_count += 1
                    else:
                        logger.warning(f"   ⚠️ Failed to extract Phase 2 data")

                        # Still save the original Phase 1 data with extraction failure markers
                        combined_data = school.to_dict()
                        combined_data.update({
                            'extraction_status': 'FAILED',
                            'extraction_timestamp': datetime.now().isoformat(),
                            'fields_extracted': 0,
                            'critical_fields_extracted': 0
                        })

                        # Remove unwanted columns
                        unwanted_columns = ['last_modified', 'source_url']
                        for col in unwanted_columns:
                            combined_data.pop(col, None)

                        if self.write_to_output_csv(combined_data):
                            logger.info(f"   📝 Saved with extraction failure markers")

                        self.fail_count += 1

                    self.processed_count += 1

                    # Progress update
                    if idx % 10 == 0 or idx == total_schools:
                        elapsed_time = time.time() - start_time
                        avg_time_per_school = elapsed_time / idx
                        remaining_schools = total_schools - idx
                        estimated_remaining_time = remaining_schools * avg_time_per_school

                        logger.info(f"\n📊 PROGRESS UPDATE:")
                        logger.info(f"   🎯 Processed: {idx}/{total_schools} ({idx/total_schools*100:.1f}%)")
                        logger.info(f"   ✅ Successful: {self.success_count}")
                        logger.info(f"   ❌ Failed: {self.fail_count}")
                        logger.info(f"   ⏱️ Elapsed: {elapsed_time/60:.1f} minutes")
                        logger.info(f"   ⏱️ Estimated remaining: {estimated_remaining_time/60:.1f} minutes")
                        logger.info(f"   📝 Output file: {self.output_csv_file}")

                    # Brief pause between schools
                    time.sleep(1)

                except Exception as school_error:
                    logger.error(f"   ❌ Error processing school {idx}: {school_error}")
                    self.fail_count += 1
                    continue

            # Final summary
            total_time = time.time() - start_time
            self.show_final_summary(total_time)

            return True

        except Exception as e:
            logger.error(f"❌ Critical error in process_schools: {e}")
            return False
        finally:
            # Cleanup
            if self.driver:
                self.driver.quit()
                logger.info("🔒 Browser driver closed")

    def show_final_summary(self, total_time):
        """Show final processing summary"""
        logger.info(f"\n{'='*80}")
        logger.info("🎯 STANDALONE PHASE 2 PROCESSING COMPLETED")
        logger.info(f"{'='*80}")
        logger.info(f"⏱️ Total processing time: {total_time/60:.1f} minutes")
        logger.info(f"📊 Total schools processed: {self.processed_count}")
        logger.info(f"✅ Successfully extracted: {self.success_count}")
        logger.info(f"❌ Failed extractions: {self.fail_count}")
        logger.info(f"📈 Success rate: {self.success_count/self.processed_count*100:.1f}%" if self.processed_count > 0 else "📈 Success rate: 0%")
        logger.info(f"📁 Input file: {self.input_csv_file}")
        logger.info(f"📝 Output file: {self.output_csv_file}")
        logger.info(f"💾 Output contains: Phase 1 + Phase 2 combined data")
        logger.info("🎉 Standalone Phase 2 processing complete!")

def main():
    """Main function for standalone Phase 2 processing"""
    try:
        print("🚀 STANDALONE PHASE 2 PROCESSOR")
        print("Processes Phase 1 CSV files independently to extract detailed school data")
        print(f"📁 Input file: {INPUT_CSV_FILE}")
        print()

        # Check if input file exists
        if not os.path.exists(INPUT_CSV_FILE):
            print(f"❌ Input file not found: {INPUT_CSV_FILE}")
            print("Please update the INPUT_CSV_FILE variable in the script with the correct path")
            return

        # Create processor and run
        processor = StandalonePhase2Processor(INPUT_CSV_FILE)
        success = processor.process_schools()

        if success:
            print(f"\n✅ Processing completed successfully!")
            print(f"📝 Output file: {processor.output_csv_file}")
        else:
            print(f"\n❌ Processing failed. Check logs for details.")

    except Exception as e:
        print(f"❌ Critical error: {e}")
        print("Please check the logs above for details")

if __name__ == "__main__":
    main()
