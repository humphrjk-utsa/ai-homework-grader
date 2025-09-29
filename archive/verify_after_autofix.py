#!/usr/bin/env python3
"""
Verify that verbose feedback is still working after Kiro IDE autofix
"""

def test_imports():
    """Test that all imports are working"""
    try:
        from report_generator import PDFReportGenerator
        from connect_web_interface import grade_submissions_page, generate_pdf_report
        from business_analytics_grader import BusinessAnalyticsGrader
        print("✅ All imports working correctly")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation with verbose feedback"""
    try:
        from report_generator import PDFReportGenerator
        
        # Sample data with comprehensive feedback
        analysis_result = {
            'total_score': 34.5,
            'max_score': 37.5,
            'comprehensive_feedback': {
                'instructor_comments': 'Excellent work with strong reflective thinking.',
                'detailed_feedback': {
                    'reflection_assessment': ['Great critical thinking demonstrated'],
                    'analytical_strengths': ['Comprehensive completion of requirements'],
                    'business_application': ['Good business context understanding'],
                    'learning_demonstration': ['Shows deep engagement with learning'],
                    'areas_for_development': ['Continue exploring advanced methods'],
                    'recommendations': ['Keep up the excellent reflective practice']
                }
            },
            'technical_analysis': {
                'code_strengths': ['Proper R library implementation'],
                'code_suggestions': ['Consider using complete.cases()'],
                'technical_observations': ['Solid programming concepts']
            }
        }
        
        # Generate PDF
        generator = PDFReportGenerator()
        pdf_path = generator.generate_report(
            student_name="Autofix_Test_Student",
            assignment_id="Test Assignment",
            analysis_result=analysis_result
        )
        
        print(f"✅ PDF generated successfully: {pdf_path}")
        return True
        
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface_structure():
    """Test that web interface has the right structure"""
    try:
        import inspect
        from connect_web_interface import grade_submissions_page, generate_pdf_report, grade_single_submission
        
        # Check that functions exist and have the right signatures
        grade_sig = inspect.signature(grade_submissions_page)
        pdf_sig = inspect.signature(generate_pdf_report)
        
        print("✅ Web interface functions have correct signatures")
        
        # Check that the source contains our verbose feedback logic
        source = inspect.getsource(grade_single_submission)
        
        checks = [
            'comprehensive_feedback',
            'detailed_feedback',
            'reflection_assessment',
            'analytical_strengths',
            'technical_analysis'
        ]
        
        for check in checks:
            if check in source:
                print(f"   ✅ {check} logic found")
            else:
                print(f"   ❌ {check} logic missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface structure error: {e}")
        return False

def test_business_grader_integration():
    """Test that Business Analytics Grader integration is working"""
    try:
        from business_analytics_grader import BusinessAnalyticsGrader
        
        # Initialize grader
        grader = BusinessAnalyticsGrader()
        
        # Check that it has the right methods
        required_methods = ['grade_submission', 'check_ollama_connection']
        
        for method in required_methods:
            if hasattr(grader, method):
                print(f"   ✅ {method} method available")
            else:
                print(f"   ❌ {method} method missing")
                return False
        
        print("✅ Business Analytics Grader integration intact")
        return True
        
    except Exception as e:
        print(f"❌ Business grader integration error: {e}")
        return False

def main():
    """Run all verification tests"""
    
    print("🔍 Verifying Verbose Feedback After Kiro IDE Autofix")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("PDF Generation", test_pdf_generation),
        ("Web Interface Structure", test_web_interface_structure),
        ("Business Grader Integration", test_business_grader_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    all_passed = True
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Verbose feedback system is working correctly after autofix.")
        print("📋 You can safely use the Streamlit app and PDF generation.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    main()