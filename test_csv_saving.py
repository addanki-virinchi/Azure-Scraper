#!/usr/bin/env python3
"""
Test CSV Saving Functionality
This script tests the CSV saving methods in isolation to verify they work correctly
"""

import os
import csv
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCSVSaver:
    def __init__(self):
        self.current_csv_file = None
        self.csv_headers_written = False
        self.total_schools_saved = 0

    def initialize_csv_file(self, state_name):
        """Initialize CSV file for incremental saving with enhanced debugging"""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_state_name = state_name.replace(' ', '_').replace('&', 'and').replace('/', '_').upper()
            self.current_csv_file = f"TEST_{clean_state_name}_phase1_complete_{timestamp}.csv"
            
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

def test_csv_functionality():
    """Test the CSV saving functionality"""
    try:
        print("🧪 TESTING CSV SAVING FUNCTIONALITY")
        print("="*60)
        
        # Create test saver
        saver = TestCSVSaver()
        
        # Test 1: Initialize CSV file
        print("\n📋 Test 1: Initialize CSV file")
        success = saver.initialize_csv_file("ARUNACHAL PRADESH")
        if success:
            print("✅ CSV initialization: PASSED")
        else:
            print("❌ CSV initialization: FAILED")
            return False
        
        # Test 2: Create sample school data
        print("\n📋 Test 2: Create sample school data")
        sample_schools = [
            {
                'state': 'ARUNACHAL PRADESH',
                'state_id': '12',
                'district': 'TEST DISTRICT',
                'district_id': '123',
                'udise_code': '12345678901',
                'school_name': 'Test School 1',
                'operational_status': 'Functional',
                'school_category': 'Primary',
                'school_management': 'Government',
                'school_type': 'Co-educational',
                'location': 'Rural',  # Will be mapped to school_location
                'pincode': '123456',  # Will be mapped to pin_code
                'address': 'Test Address 1',
                'know_more_link': 'https://kys.udiseplus.gov.in/#/schooldetail/12345/12',
                'email': 'test@school.com',
                'extraction_date': datetime.now().isoformat()
            },
            {
                'state': 'ARUNACHAL PRADESH',
                'state_id': '12',
                'district': 'TEST DISTRICT',
                'district_id': '123',
                'udise_code': '12345678902',
                'school_name': 'Test School 2',
                'operational_status': 'Functional',
                'school_category': 'Secondary',
                'school_management': 'Private',
                'school_type': 'Co-educational',
                'location': 'Urban',  # Will be mapped to school_location
                'pincode': '123456',  # Will be mapped to pin_code
                'address': 'Test Address 2',
                'know_more_link': 'https://kys.udiseplus.gov.in/#/schooldetail/67890/12',
                'email': 'test2@school.com',
                'extraction_date': datetime.now().isoformat()
            }
        ]
        print(f"✅ Created {len(sample_schools)} sample schools")
        
        # Test 3: Save first page
        print("\n📋 Test 3: Save first page of schools")
        success = saver.save_schools_to_csv_incremental(sample_schools, 1)
        if success:
            print("✅ First page save: PASSED")
        else:
            print("❌ First page save: FAILED")
            return False
        
        # Test 4: Save second page
        print("\n📋 Test 4: Save second page of schools")
        success = saver.save_schools_to_csv_incremental(sample_schools, 2)
        if success:
            print("✅ Second page save: PASSED")
        else:
            print("❌ Second page save: FAILED")
            return False
        
        # Test 5: Verify final file
        print("\n📋 Test 5: Verify final CSV file")
        if os.path.exists(saver.current_csv_file):
            file_size = os.path.getsize(saver.current_csv_file)
            abs_path = os.path.abspath(saver.current_csv_file)
            
            # Count lines in file
            with open(saver.current_csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"✅ File exists: {saver.current_csv_file}")
            print(f"📍 Absolute path: {abs_path}")
            print(f"📊 File size: {file_size} bytes")
            print(f"📊 Lines in file: {len(lines)} (1 header + {len(lines)-1} data rows)")
            print(f"📊 Expected data rows: {len(sample_schools) * 2}")
            
            if len(lines) == (len(sample_schools) * 2) + 1:  # +1 for header
                print("✅ File verification: PASSED")
                
                # Clean up test file
                os.remove(saver.current_csv_file)
                print("🗑️ Test file cleaned up")
                return True
            else:
                print("❌ File verification: FAILED - incorrect number of rows")
                return False
        else:
            print("❌ File verification: FAILED - file does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Critical error in CSV testing: {e}")
        return False

if __name__ == "__main__":
    success = test_csv_functionality()
    if success:
        print("\n🎉 ALL CSV TESTS PASSED!")
        print("The CSV saving functionality is working correctly.")
    else:
        print("\n⚠️ CSV TESTS FAILED!")
        print("There are issues with the CSV saving functionality.")
