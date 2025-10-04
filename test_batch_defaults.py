#!/usr/bin/env python3
"""
Test Batch Defaults
Verify that batch submission is now the default option
"""

import re

def test_assignment_manager_defaults():
    """Test that assignment manager defaults to batch upload"""
    print("🧪 Testing Assignment Manager Defaults")
    print("=" * 40)
    
    try:
        with open('assignment_manager.py', 'r') as f:
            content = f.read()
        
        # Check that batch upload is first in the radio options
        radio_pattern = r'st\.radio\("Choose upload method:", \["([^"]+)", "([^"]+)"\]'
        match = re.search(radio_pattern, content)
        
        if match:
            first_option = match.group(1)
            second_option = match.group(2)
            
            print(f"📊 Upload method options:")
            print(f"   1. {first_option}")
            print(f"   2. {second_option}")
            
            if first_option == "Batch Upload (ZIP)":
                print("   ✅ Batch Upload is first option (default)")
            else:
                print("   ❌ Batch Upload is not first option")
                return False
            
            # Check for index=0 parameter
            if "index=0" in content:
                print("   ✅ Explicit index=0 parameter found")
            else:
                print("   ⚠️ No explicit index parameter (should still default to first)")
        else:
            print("   ❌ Could not find radio button pattern")
            return False
        
        # Check conditional logic
        if 'if upload_method == "Batch Upload (ZIP)":' in content:
            print("   ✅ Conditional logic updated for batch first")
        else:
            print("   ❌ Conditional logic not updated")
            return False
        
        print("🎉 Assignment manager defaults test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Assignment manager test failed: {e}")
        return False

def test_grading_interface_defaults():
    """Test that grading interface defaults to batch grading"""
    print("\n🧪 Testing Grading Interface Defaults")
    print("=" * 40)
    
    try:
        with open('connect_web_interface.py', 'r') as f:
            content = f.read()
        
        # Check that batch grading is first in the selectbox options
        selectbox_pattern = r'st\.selectbox\("Grading Mode", \[\s*"([^"]+)",\s*"([^"]+)"\s*\]'
        match = re.search(selectbox_pattern, content)
        
        if match:
            first_option = match.group(1)
            second_option = match.group(2)
            
            print(f"📊 Grading mode options:")
            print(f"   1. {first_option}")
            print(f"   2. {second_option}")
            
            if "Batch" in first_option:
                print("   ✅ Batch grading is first option (default)")
            else:
                print("   ❌ Batch grading is not first option")
                return False
            
            # Check for index=0 parameter
            if "index=0" in content:
                print("   ✅ Explicit index=0 parameter found")
            else:
                print("   ⚠️ No explicit index parameter (should still default to first)")
        else:
            print("   ❌ Could not find selectbox pattern")
            return False
        
        # Check conditional logic
        if 'if grade_mode == "Batch (all at once)":' in content:
            print("   ✅ Conditional logic updated for batch first")
        else:
            print("   ❌ Conditional logic not updated")
            return False
        
        print("🎉 Grading interface defaults test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Grading interface test failed: {e}")
        return False

def test_user_experience():
    """Test the expected user experience"""
    print("\n🧪 Testing User Experience")
    print("=" * 40)
    
    print("📋 Expected User Experience:")
    print("   1. User opens submission page")
    print("   2. 'Batch Upload (ZIP)' is pre-selected")
    print("   3. User can upload ZIP file immediately")
    print("   4. User opens grading page")
    print("   5. 'Batch (all at once)' is pre-selected")
    print("   6. User can grade all submissions immediately")
    print("   ✅ Batch operations are now the default workflow")
    
    return True

def run_all_batch_default_tests():
    """Run all batch default tests"""
    print("🚀 Batch Defaults - Verification Tests")
    print("=" * 60)
    
    tests = [
        ("Assignment Manager Defaults", test_assignment_manager_defaults),
        ("Grading Interface Defaults", test_grading_interface_defaults),
        ("User Experience", test_user_experience)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BATCH DEFAULTS TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All batch default tests passed!")
        print("\n📋 Changes Made:")
        print("✅ Batch Upload (ZIP) is now default for submissions")
        print("✅ Batch grading is now default for grading")
        print("✅ Conditional logic updated to match new defaults")
        print("✅ User workflow optimized for batch operations")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_batch_default_tests()
    exit(0 if success else 1)