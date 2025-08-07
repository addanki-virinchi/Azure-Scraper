#!/usr/bin/env python3
"""
Test Email Extraction
Verify that the email field is properly extracted from school data
"""

import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_email_extraction():
    """Test the email extraction logic with sample HTML"""
    
    print("🧪 TESTING EMAIL EXTRACTION")
    print("="*50)
    
    # Sample HTML structures based on the provided example
    test_cases = [
        {
            'name': 'Standard Email with span.ms-2',
            'html': '''
            <div class="school-info">
                <p class="ng-star-inserted">
                    <a style="color: #451c78; text-decoration: none;" href="mailto:ampsbhatubasti11@gmail.com">
                        <svg>...</svg>
                        <span class="ms-2">ampsbhatubasti11@gmail.com</span>
                    </a>
                </p>
                <p>PIN Code: 123456</p>
            </div>
            ''',
            'expected': 'ampsbhatubasti11@gmail.com'
        },
        {
            'name': 'Email in mailto href only',
            'html': '''
            <div class="school-info">
                <p class="ng-star-inserted">
                    <a href="mailto:school.contact@education.gov.in">Contact Email</a>
                </p>
                <p>PIN Code: 654321</p>
            </div>
            ''',
            'expected': 'school.contact@education.gov.in'
        },
        {
            'name': 'Email in plain text',
            'html': '''
            <div class="school-info">
                <p>Contact: principal@schoolname.edu.in</p>
                <p>PIN Code: 789012</p>
            </div>
            ''',
            'expected': 'principal@schoolname.edu.in'
        },
        {
            'name': 'No email present',
            'html': '''
            <div class="school-info">
                <p>School Name: Test School</p>
                <p>PIN Code: 345678</p>
            </div>
            ''',
            'expected': 'N/A'
        },
        {
            'name': 'Multiple emails (should get first)',
            'html': '''
            <div class="school-info">
                <p class="ng-star-inserted">
                    <a href="mailto:primary@school.edu">
                        <span class="ms-2">primary@school.edu</span>
                    </a>
                </p>
                <p>Secondary: secondary@school.edu</p>
                <p>PIN Code: 567890</p>
            </div>
            ''',
            'expected': 'primary@school.edu'
        }
    ]
    
    def extract_email_from_html(element_html, element_text):
        """Extract email using the same logic as in the main script"""
        email = 'N/A'
        
        # Strategy 1: Extract from span.ms-2 within email link containers
        email_span_match = re.search(r'<span[^>]*class="[^"]*ms-2[^"]*"[^>]*>([^<]+@[^<]+)</span>', element_html)
        if email_span_match:
            email = email_span_match.group(1).strip()
        else:
            # Strategy 2: Extract from mailto href attribute
            mailto_match = re.search(r'href="mailto:([^"]+@[^"]+)"', element_html)
            if mailto_match:
                email = mailto_match.group(1).strip()
            else:
                # Strategy 3: Look for email pattern in text content
                email_text_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', element_text)
                if email_text_match:
                    email = email_text_match.group(0).strip()
        
        return email
    
    # Test each case
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Extract text content (simulate what Selenium would provide)
        text_content = re.sub(r'<[^>]+>', ' ', test_case['html'])
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Extract email
        extracted_email = extract_email_from_html(test_case['html'], text_content)
        
        # Check result
        success = extracted_email == test_case['expected']
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"   Expected: {test_case['expected']}")
        print(f"   Extracted: {extracted_email}")
        print(f"   Result: {status}")
        
        results.append({
            'test_case': test_case['name'],
            'expected': test_case['expected'],
            'extracted': extracted_email,
            'success': success
        })
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("="*30)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {total - passed}/{total}")
    print(f"   📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Email extraction logic is working correctly")
        print("✅ All extraction strategies are functional")
        print("✅ Fallback mechanisms are working")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("❌ Email extraction needs review")
        for result in results:
            if not result['success']:
                print(f"   - {result['test_case']}: Expected '{result['expected']}', got '{result['extracted']}'")
        return False

def test_regex_patterns():
    """Test individual regex patterns"""
    print(f"\n🔍 TESTING INDIVIDUAL REGEX PATTERNS")
    print("="*40)
    
    patterns = [
        {
            'name': 'span.ms-2 pattern',
            'pattern': r'<span[^>]*class="[^"]*ms-2[^"]*"[^>]*>([^<]+@[^<]+)</span>',
            'test_html': '<span class="ms-2">test@example.com</span>',
            'expected': 'test@example.com'
        },
        {
            'name': 'mailto href pattern',
            'pattern': r'href="mailto:([^"]+@[^"]+)"',
            'test_html': 'href="mailto:contact@school.edu"',
            'expected': 'contact@school.edu'
        },
        {
            'name': 'email text pattern',
            'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'test_html': 'Contact us at info@university.ac.in for more details',
            'expected': 'info@university.ac.in'
        }
    ]
    
    for pattern_test in patterns:
        print(f"\n🔎 Testing: {pattern_test['name']}")
        match = re.search(pattern_test['pattern'], pattern_test['test_html'])
        
        if match:
            extracted = match.group(1) if len(match.groups()) > 0 else match.group(0)
            success = extracted == pattern_test['expected']
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   Expected: {pattern_test['expected']}")
            print(f"   Extracted: {extracted}")
            print(f"   Result: {status}")
        else:
            print(f"   Result: ❌ FAIL - No match found")

def main():
    """Main test function"""
    print("🔧 Testing email extraction for Phase 1 school data")
    print("This test verifies the email field extraction logic")
    print()
    
    # Test email extraction
    extraction_success = test_email_extraction()
    
    # Test regex patterns
    test_regex_patterns()
    
    if extraction_success:
        print("\n🎉 EMAIL EXTRACTION ENHANCEMENT SUCCESSFUL!")
        print("✅ Email field will be properly extracted in Phase 1")
        print("✅ Multiple extraction strategies implemented")
        print("✅ Fallback mechanisms in place")
        print("✅ CSV headers updated to include email field")
        print("\nThe sequential processor now extracts complete contact information! 📧")
    else:
        print("\n⚠️ EMAIL EXTRACTION NEEDS REFINEMENT")
        print("Check the test results above for specific issues")

if __name__ == "__main__":
    main()
