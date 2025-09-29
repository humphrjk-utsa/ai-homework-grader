#!/usr/bin/env python3
"""
Test which grading system is actually being used
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_import():
    """Test which grade_submissions_page is being imported"""
    
    print("🔍 Testing which grading system is imported...")
    
    try:
        # Test the import exactly as app.py does it
        from connect_web_interface import grade_submissions_page
        
        # Check the function's module and location
        print(f"✅ Imported grade_submissions_page from: {grade_submissions_page.__module__}")
        print(f"📁 Function file: {grade_submissions_page.__code__.co_filename}")
        print(f"📝 Function name: {grade_submissions_page.__name__}")
        
        # Check the docstring to identify which function it is
        docstring = grade_submissions_page.__doc__
        if docstring:
            print(f"📋 Docstring: {docstring[:100]}...")
        
        # Check if it mentions BusinessAnalyticsGrader
        import inspect
        source = inspect.getsource(grade_submissions_page)
        
        if "BusinessAnalyticsGrader" in source:
            print("✅ Function uses BusinessAnalyticsGrader - CORRECT!")
        else:
            print("❌ Function does NOT use BusinessAnalyticsGrader - WRONG!")
        
        if "ai_grader.grade_notebook" in source:
            print("❌ Function uses old ai_grader system - WRONG!")
        else:
            print("✅ Function does NOT use old ai_grader - CORRECT!")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_business_grader_import():
    """Test if BusinessAnalyticsGrader can be imported"""
    
    print("\n🤖 Testing BusinessAnalyticsGrader import...")
    
    try:
        from business_analytics_grader import BusinessAnalyticsGrader
        print("✅ BusinessAnalyticsGrader imported successfully")
        
        # Test initialization
        grader = BusinessAnalyticsGrader()
        print("✅ BusinessAnalyticsGrader initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ BusinessAnalyticsGrader import/init failed: {e}")
        return False

def main():
    """Run the tests"""
    
    print("🧪 TESTING WHICH GRADING SYSTEM IS USED")
    print("=" * 50)
    
    # Test imports
    import_ok = test_import()
    grader_ok = test_business_grader_import()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    if import_ok and grader_ok:
        print("🎉 CORRECT GRADING SYSTEM IS IMPORTED!")
        print("   The web interface should use BusinessAnalyticsGrader")
        print("   If it's still using fallback, there may be an error during execution")
    else:
        print("❌ IMPORT ISSUES FOUND!")
        print("   The web interface may be using the wrong grading system")

if __name__ == "__main__":
    main()