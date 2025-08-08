#!/usr/bin/env python3
"""
Test Script for Phase 2 Scraper Fixes Validation
Tests the recent fixes to Basic Details extraction, particularly:
- Year of Establishment extraction
- National/State Management fields
- Affiliation Board Sec./HSec. fields
- Data combination integrity
"""

import pandas as pd
import glob
import os
import time
from datetime import datetime
import logging
from phase2_automated_processor import AutomatedPhase2Processor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_phase2_fixes.log')
    ]
)
logger = logging.getLogger(__name__)

class Phase2FixesValidator:
    """Test validator for Phase 2 scraper fixes"""
    
    def __init__(self):
        self.processor = None
        self.test_results = []
        self.basic_details_fields = [
            'location', 'school_category', 'school_type', 'year_of_establishment',
            'national_management', 'state_management', 'affiliation_board_sec', 'affiliation_board_hsec'
        ]
        
    def find_phase1_files(self):
        """Find available Phase 1 CSV files"""
        logger.info("🔍 Looking for Phase 1 CSV files...")
        
        # Look for new format first
        pattern1 = "*_phase1_complete_*.csv"
        csv_files = glob.glob(pattern1)
        
        if not csv_files:
            # Fallback to legacy format
            pattern2 = "*_with_links_*.csv"
            csv_files = glob.glob(pattern2)
            logger.info("Using legacy Phase 1 files (with_links format)")
        
        if csv_files:
            logger.info(f"✅ Found {len(csv_files)} Phase 1 files: {csv_files}")
            return csv_files
        else:
            logger.error("❌ No Phase 1 CSV files found!")
            return []
    
    def select_test_schools(self, csv_file, num_schools=10):
        """Select exactly 10 schools with valid know_more_links for testing"""
        logger.info(f"📊 Loading data from: {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            logger.info(f"   📋 Total records in file: {len(df)}")
            
            # Filter schools with valid know_more_links
            if 'phase2_ready' in df.columns:
                valid_schools = df[df['phase2_ready'] == True].copy()
                logger.info(f"   🎯 Phase 2 ready schools: {len(valid_schools)}")
            elif 'has_know_more_link' in df.columns:
                valid_schools = df[df['has_know_more_link'] == True].copy()
                logger.info(f"   🎯 Schools with know_more_links: {len(valid_schools)}")
            else:
                # Legacy format
                valid_schools = df[df['know_more_link'].notna() & (df['know_more_link'] != 'N/A')].copy()
                logger.info(f"   🎯 Schools with valid know_more_links: {len(valid_schools)}")
            
            if len(valid_schools) == 0:
                logger.error("❌ No schools with valid know_more_links found!")
                return None
            
            # Select exactly num_schools for testing
            test_schools = valid_schools.head(num_schools).copy()
            logger.info(f"✅ Selected {len(test_schools)} schools for testing")
            
            return test_schools
            
        except Exception as e:
            logger.error(f"❌ Error loading CSV file: {e}")
            return None
    
    def setup_processor(self):
        """Initialize the Phase 2 processor"""
        logger.info("🔧 Setting up Phase 2 processor...")
        
        try:
            self.processor = AutomatedPhase2Processor()
            self.processor.setup_driver()
            logger.info("✅ Phase 2 processor initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup processor: {e}")
            return False
    
    def test_single_school(self, school_data, school_index):
        """Test Phase 2 extraction for a single school"""
        school_name = school_data.get('school_name', 'Unknown School')
        know_more_link = school_data.get('know_more_link', '')
        
        logger.info(f"\n📍 TESTING SCHOOL {school_index + 1}/10: {school_name}")
        logger.info(f"   🔗 URL: {know_more_link}")
        
        test_result = {
            'school_index': school_index + 1,
            'school_name': school_name,
            'know_more_link': know_more_link,
            'extraction_success': False,
            'basic_details_extracted': 0,
            'basic_details_total': len(self.basic_details_fields),
            'extracted_fields': {},
            'error_message': None
        }
        
        try:
            # Extract Phase 2 data
            start_time = time.time()
            extracted_data = self.processor.extract_focused_data(know_more_link)
            extraction_time = time.time() - start_time
            
            if extracted_data:
                test_result['extraction_success'] = True
                test_result['extraction_time'] = extraction_time
                
                # Check Basic Details fields
                basic_details_count = 0
                for field in self.basic_details_fields:
                    value = extracted_data.get(field, 'N/A')
                    test_result['extracted_fields'][field] = value
                    if value != 'N/A':
                        basic_details_count += 1
                
                test_result['basic_details_extracted'] = basic_details_count
                
                # Combine with original data
                combined_data = school_data.to_dict()
                combined_data.update(extracted_data)
                test_result['combined_data'] = combined_data
                
                # Log results
                logger.info(f"   ✅ SUCCESS: Extracted {basic_details_count}/{len(self.basic_details_fields)} Basic Details fields")
                logger.info(f"   ⏱️ Extraction time: {extraction_time:.2f}s")
                logger.info(f"   📋 Year of Establishment: {extracted_data.get('year_of_establishment', 'N/A')}")
                logger.info(f"   🏛️ National Management: {extracted_data.get('national_management', 'N/A')}")
                logger.info(f"   🏛️ State Management: {extracted_data.get('state_management', 'N/A')}")
                logger.info(f"   📜 Affiliation Board Sec: {extracted_data.get('affiliation_board_sec', 'N/A')}")
                logger.info(f"   📜 Affiliation Board HSec: {extracted_data.get('affiliation_board_hsec', 'N/A')}")
                logger.info(f"   👥 Students: {extracted_data.get('total_students', 'N/A')}")
                logger.info(f"   👨‍🏫 Teachers: {extracted_data.get('total_teachers', 'N/A')}")
                
            else:
                test_result['error_message'] = "No data extracted"
                logger.warning(f"   ❌ FAILED: No data extracted")
                
        except Exception as e:
            test_result['error_message'] = str(e)
            logger.error(f"   ❌ ERROR: {e}")
        
        self.test_results.append(test_result)
        return test_result
    
    def run_validation_test(self):
        """Run the complete validation test using the new dual output strategy"""
        logger.info("🚀 STARTING PHASE 2 FIXES VALIDATION TEST")
        logger.info("🎯 Testing NEW DUAL OUTPUT STRATEGY (Incremental CSV + Google Sheets)")
        logger.info("="*80)

        # Find Phase 1 files
        csv_files = self.find_phase1_files()
        if not csv_files:
            return False

        # Use the first available file
        csv_file = csv_files[0]
        logger.info(f"📁 Using file: {csv_file}")

        # Select test schools and create a temporary test CSV
        test_schools = self.select_test_schools(csv_file, num_schools=10)
        if test_schools is None:
            return False

        # Create a temporary CSV file with just the test schools
        test_csv_file = "temp_test_phase2_10_schools.csv"
        test_schools.to_csv(test_csv_file, index=False)
        logger.info(f"📝 Created temporary test CSV: {test_csv_file}")

        # Setup processor
        if not self.setup_processor():
            return False

        # Test the COMPLETE dual output strategy workflow
        logger.info(f"\n🧪 TESTING DUAL OUTPUT STRATEGY WITH {len(test_schools)} SCHOOLS")
        logger.info("="*80)
        logger.info("📝 Testing: Incremental CSV writing")
        logger.info("📤 Testing: Google Sheets upload (if enabled)")

        try:
            # Use the actual state processing method that contains our incremental CSV logic
            success = self.processor.process_state_file_automated(test_csv_file)

            if success:
                logger.info("✅ Dual output strategy test SUCCESSFUL!")

                # Check if incremental CSV was created
                if self.processor.incremental_csv_file and os.path.exists(self.processor.incremental_csv_file):
                    logger.info(f"✅ Incremental CSV created: {self.processor.incremental_csv_file}")

                    # Load the incremental CSV to verify data
                    df_incremental = pd.read_csv(self.processor.incremental_csv_file)
                    logger.info(f"✅ Incremental CSV contains: {len(df_incremental)} records")

                    # Copy to our expected output file
                    df_incremental.to_csv("Output_phase_2_10.csv", index=False)
                    logger.info("✅ Copied incremental CSV to Output_phase_2_10.csv")

                    # Analyze the results
                    self.analyze_incremental_csv_results(df_incremental)

                else:
                    logger.warning("⚠️ Incremental CSV file not found")

            else:
                logger.error("❌ Dual output strategy test FAILED!")

        except Exception as e:
            logger.error(f"❌ Error testing dual output strategy: {e}")
            success = False

        # Cleanup temporary file
        try:
            if os.path.exists(test_csv_file):
                os.remove(test_csv_file)
                logger.info(f"🗑️ Cleaned up temporary file: {test_csv_file}")
        except:
            pass

        # Cleanup driver
        if self.processor and self.processor.driver:
            self.processor.driver.quit()
            logger.info("🔒 Driver closed")

        return success

    def analyze_incremental_csv_results(self, df_incremental):
        """Analyze the results from the incremental CSV file"""
        logger.info(f"\n📊 ANALYZING INCREMENTAL CSV RESULTS")
        logger.info("="*50)

        # Basic statistics
        total_records = len(df_incremental)
        logger.info(f"📋 Total records: {total_records}")

        # Check Basic Details fields
        basic_details_stats = {}
        for field in self.basic_details_fields:
            if field in df_incremental.columns:
                non_na_count = len(df_incremental[df_incremental[field] != 'N/A'])
                percentage = (non_na_count / total_records * 100) if total_records > 0 else 0
                basic_details_stats[field] = {'count': non_na_count, 'percentage': percentage}
                logger.info(f"   {field}: {non_na_count}/{total_records} ({percentage:.1f}%)")

        # Special focus on Year of Establishment (our primary fix)
        if 'year_of_establishment' in df_incremental.columns:
            year_values = df_incremental[df_incremental['year_of_establishment'] != 'N/A']['year_of_establishment']
            if len(year_values) > 0:
                logger.info(f"\n🎯 YEAR OF ESTABLISHMENT VALIDATION:")
                logger.info(f"   ✅ Successfully extracted: {len(year_values)}/{total_records} schools")
                logger.info(f"   📅 Sample years: {list(year_values.head(3))}")
            else:
                logger.warning(f"   ⚠️ No Year of Establishment data extracted")

        # Check student/teacher data
        student_teacher_fields = ['total_students', 'total_teachers']
        logger.info(f"\n👥 STUDENT/TEACHER DATA:")
        for field in student_teacher_fields:
            if field in df_incremental.columns:
                non_na_count = len(df_incremental[df_incremental[field] != 'N/A'])
                percentage = (non_na_count / total_records * 100) if total_records > 0 else 0
                logger.info(f"   {field}: {non_na_count}/{total_records} ({percentage:.1f}%)")

        # Check data combination integrity
        logger.info(f"\n🔗 DATA COMBINATION INTEGRITY:")
        phase1_fields = ['school_name', 'district', 'state', 'know_more_link']
        for field in phase1_fields:
            if field in df_incremental.columns:
                non_na_count = len(df_incremental[df_incremental[field].notna()])
                logger.info(f"   Phase 1 field '{field}': {non_na_count}/{total_records} preserved")

        return basic_details_stats

    def save_test_results(self, combined_data):
        """Save test results to CSV file"""
        try:
            output_file = "Output_phase_2_10.csv"
            
            if combined_data:
                df = pd.DataFrame(combined_data)
                df.to_csv(output_file, index=False)
                logger.info(f"\n💾 SAVED RESULTS: {output_file}")
                logger.info(f"   📊 Records saved: {len(combined_data)}")
                logger.info(f"   📋 Columns: {len(df.columns)}")
            else:
                # Create empty file with expected headers
                empty_data = {
                    'school_name': [], 'district': [], 'state': [],
                    'know_more_link': [], 'detail_school_name': [],
                    'year_of_establishment': [], 'location': [], 'school_category': [],
                    'school_type': [], 'national_management': [], 'state_management': [],
                    'affiliation_board_sec': [], 'affiliation_board_hsec': [],
                    'total_students': [], 'total_teachers': []
                }
                df_empty = pd.DataFrame(empty_data)
                df_empty.to_csv(output_file, index=False)
                logger.info(f"\n💾 CREATED EMPTY FILE: {output_file}")
                
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
    
    def show_test_summary(self):
        """Show comprehensive test summary"""
        logger.info(f"\n{'='*80}")
        logger.info("📊 PHASE 2 FIXES VALIDATION SUMMARY")
        logger.info(f"{'='*80}")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['extraction_success'])
        
        logger.info(f"🧪 Total schools tested: {total_tests}")
        logger.info(f"✅ Successful extractions: {successful_tests}")
        logger.info(f"❌ Failed extractions: {total_tests - successful_tests}")
        
        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")
        
        # Basic Details field analysis
        logger.info(f"\n📋 BASIC DETAILS FIELDS ANALYSIS:")
        field_success_count = {field: 0 for field in self.basic_details_fields}
        
        for result in self.test_results:
            if result['extraction_success']:
                for field in self.basic_details_fields:
                    if result['extracted_fields'].get(field, 'N/A') != 'N/A':
                        field_success_count[field] += 1
        
        for field, count in field_success_count.items():
            percentage = (count / successful_tests * 100) if successful_tests > 0 else 0
            logger.info(f"   {field}: {count}/{successful_tests} ({percentage:.1f}%)")
        
        # Specific focus on Year of Establishment
        year_extracted = field_success_count.get('year_of_establishment', 0)
        logger.info(f"\n🎯 YEAR OF ESTABLISHMENT FIX VALIDATION:")
        logger.info(f"   Successfully extracted: {year_extracted}/{successful_tests} schools")
        
        if year_extracted > 0:
            logger.info("   ✅ Year of Establishment extraction is WORKING!")
        else:
            logger.warning("   ⚠️ Year of Establishment extraction needs attention")
        
        logger.info(f"\n🎉 VALIDATION TEST COMPLETED!")

def main():
    """Main function to run the validation test"""
    print("🧪 PHASE 2 FIXES VALIDATION TEST - DUAL OUTPUT STRATEGY")
    print("Testing Basic Details extraction improvements + New incremental CSV functionality")
    print("🎯 Primary Focus: Year of Establishment, Management fields, Affiliation fields")
    print("📝 New Feature: Incremental CSV writing for crash protection")
    print("📤 New Feature: Google Sheets bulk upload after completion")
    print()
    
    validator = Phase2FixesValidator()
    success = validator.run_validation_test()
    
    if success:
        print("\n✅ Dual output strategy validation test completed successfully!")
        print("📁 Check 'Output_phase_2_10.csv' for results")
        print("📝 Check '*_phase2_incremental_*.csv' for incremental CSV files")
        print("📤 Check Google Sheets for uploaded data (if enabled)")
        print("📄 Check 'test_phase2_fixes.log' for detailed logs")
    else:
        print("\n❌ Dual output strategy validation test failed!")
        print("📄 Check 'test_phase2_fixes.log' for error details")

if __name__ == "__main__":
    main()
