#!/usr/bin/env python3
"""
Verify CSV Headers and Content
This script creates a test CSV file and verifies the headers match the specification exactly
"""

import csv
import pandas as pd
from datetime import datetime
from test_csv_saving import TestCSVSaver

def verify_csv_headers_and_content():
    """Verify that CSV headers and content match the Phase 1 specification"""
    try:
        print("🔍 VERIFYING CSV HEADERS AND CONTENT")
        print("="*60)
        
        # Expected headers from specification
        expected_headers = [
            'has_know_more_link', 'phase2_ready', 'state', 'state_id', 'district', 'district_id',
            'extraction_date', 'udise_code', 'school_name', 'know_more_link', 'email',
            'operational_status', 'school_category', 'school_management', 'school_type',
            'school_location', 'address', 'pin_code'
        ]
        
        print(f"📋 Expected headers ({len(expected_headers)}):")
        for i, header in enumerate(expected_headers, 1):
            print(f"   {i:2d}. {header}")
        
        # Create test CSV
        saver = TestCSVSaver()
        saver.initialize_csv_file("HEADER_TEST")
        
        # Create test data with valid and invalid know_more_links
        test_schools = [
            {
                'state': 'TEST STATE',
                'state_id': '99',
                'district': 'TEST DISTRICT',
                'district_id': '999',
                'udise_code': '99999999999',
                'school_name': 'School With Valid Link',
                'operational_status': 'Functional',
                'school_category': 'Primary',
                'school_management': 'Government',
                'school_type': 'Co-educational',
                'location': 'Rural',
                'pincode': '123456',
                'address': 'Test Address 1',
                'know_more_link': 'https://kys.udiseplus.gov.in/#/schooldetail/12345/99',  # Valid link
                'email': 'valid@school.com',
                'extraction_date': datetime.now().isoformat()
            },
            {
                'state': 'TEST STATE',
                'state_id': '99',
                'district': 'TEST DISTRICT',
                'district_id': '999',
                'udise_code': '99999999998',
                'school_name': 'School Without Valid Link',
                'operational_status': 'Functional',
                'school_category': 'Secondary',
                'school_management': 'Private',
                'school_type': 'Co-educational',
                'location': 'Urban',
                'pincode': '654321',
                'address': 'Test Address 2',
                'know_more_link': 'N/A',  # Invalid link
                'email': 'N/A',
                'extraction_date': datetime.now().isoformat()
            }
        ]
        
        # Save test data
        saver.save_schools_to_csv_incremental(test_schools, 1)
        
        # Read and verify the CSV
        print(f"\n📄 Reading CSV file: {saver.current_csv_file}")
        
        # Read with pandas for easy analysis
        df = pd.read_csv(saver.current_csv_file)
        
        print(f"\n📊 CSV Analysis:")
        print(f"   Rows: {len(df)} (excluding header)")
        print(f"   Columns: {len(df.columns)}")
        
        # Check headers
        actual_headers = list(df.columns)
        print(f"\n📋 Actual headers ({len(actual_headers)}):")
        for i, header in enumerate(actual_headers, 1):
            print(f"   {i:2d}. {header}")
        
        # Compare headers
        print(f"\n🔍 Header Comparison:")
        headers_match = actual_headers == expected_headers
        if headers_match:
            print("✅ Headers match specification EXACTLY")
        else:
            print("❌ Headers do NOT match specification")
            
            # Show differences
            print("\n📋 Differences:")
            for i, (expected, actual) in enumerate(zip(expected_headers, actual_headers), 1):
                if expected != actual:
                    print(f"   Position {i}: Expected '{expected}', Got '{actual}'")
            
            # Check for missing/extra headers
            missing = set(expected_headers) - set(actual_headers)
            extra = set(actual_headers) - set(expected_headers)
            
            if missing:
                print(f"\n❌ Missing headers: {missing}")
            if extra:
                print(f"\n⚠️ Extra headers: {extra}")
        
        # Verify boolean field values
        print(f"\n🔍 Boolean Field Verification:")
        for index, row in df.iterrows():
            school_name = row['school_name']
            has_link = row['has_know_more_link']
            phase2_ready = row['phase2_ready']
            know_more_link = row['know_more_link']
            
            print(f"\n   School: {school_name}")
            print(f"   know_more_link: {know_more_link}")
            print(f"   has_know_more_link: {has_link} (type: {type(has_link)})")
            print(f"   phase2_ready: {phase2_ready} (type: {type(phase2_ready)})")
            
            # Verify logic
            expected_bool = (know_more_link != 'N/A' and 
                           know_more_link and 
                           'schooldetail' in str(know_more_link))
            
            if has_link == expected_bool and phase2_ready == expected_bool:
                print(f"   ✅ Boolean logic correct")
            else:
                print(f"   ❌ Boolean logic incorrect - Expected: {expected_bool}")
        
        # Verify field mapping
        print(f"\n🔍 Field Mapping Verification:")
        for index, row in df.iterrows():
            school_name = row['school_name']
            school_location = row['school_location']
            pin_code = row['pin_code']
            address = row['address']
            
            print(f"\n   School: {school_name}")
            print(f"   school_location: {school_location}")
            print(f"   pin_code: {pin_code}")
            print(f"   address: {address}")
        
        # Show sample CSV content
        print(f"\n📄 Sample CSV Content:")
        print(df.to_string(index=False, max_cols=10))
        
        # Clean up
        import os
        os.remove(saver.current_csv_file)
        print(f"\n🗑️ Test file cleaned up")
        
        return headers_match
        
    except Exception as e:
        print(f"❌ Error in verification: {e}")
        return False

if __name__ == "__main__":
    success = verify_csv_headers_and_content()
    
    if success:
        print(f"\n🎉 CSV HEADERS VERIFICATION PASSED!")
        print(f"The CSV headers match the Phase 1 specification exactly.")
    else:
        print(f"\n⚠️ CSV HEADERS VERIFICATION FAILED!")
        print(f"The CSV headers need to be corrected.")
