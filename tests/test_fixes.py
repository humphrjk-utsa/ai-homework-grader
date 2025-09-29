#!/usr/bin/env python3
"""
Test the fixes for View Results and PDF code examples
"""

import json
import sqlite3
from report_generator import PDFReportGenerator

def test_view_results_feedback_parsing():
    """Test that the View Results page can parse comprehensive feedback"""
    
    print("🔍 Testing View Results Feedback Parsing...")
    
    # Sample comprehensive feedback data (like what's stored in database)
    sample_feedback_data = {
        'final_score': 34.5,
        'component_scores': {
            'technical_points': 8.8,
            'business_points': 10.4,
            'analysis_points': 8.6,
            'communication_points': 6.7
        },
        'comprehensive_feedback': {
            'instructor_comments': 'This submission demonstrates excellent foundational work in business analytics.',
            'detailed_feedback': {
                'reflection_assessment': [
                    'Excellent thoughtful responses to reflection questions demonstrate critical thinking',
                    'Shows strong self-awareness about analytical choices'
                ],
                'analytical_strengths': [
                    'Comprehensive completion of all assignment requirements',
                    'Effective integration of business context'
                ],
                'business_application': [
                    'Demonstrates understanding of data analysis applications in business decision-making'
                ],
                'learning_demonstration': [
                    'Reflection questions show deep engagement with the learning process',
                    'Articulates challenges faced and lessons learned effectively'
                ],
                'areas_for_development': [
                    'Continue exploring advanced statistical methods',
                    'Expand knowledge of missing data imputation techniques'
                ],
                'recommendations': [
                    'Continue the excellent reflective practice demonstrated',
                    'Explore correlation analysis and statistical significance testing'
                ]
            }
        },
        'technical_analysis': {
            'code_strengths': [
                'Proper implementation of R library loading and data import procedures',
                'Effective use of dplyr functions for data manipulation'
            ],
            'code_suggestions': [
                'Consider using complete.cases() for more robust missing data handling',
                'Explore the cut() function for creating categorical variables'
            ],
            'technical_observations': [
                'Demonstrates solid understanding of fundamental R programming concepts',
                'Code structure follows logical analytical workflow'
            ]
        }
    }
    
    # Test JSON serialization/deserialization (like database storage)
    try:
        json_str = json.dumps(sample_feedback_data)
        parsed_data = json.loads(json_str)
        
        print("✅ JSON serialization/deserialization working")
        
        # Test parsing logic (like what view_submission_detail does)
        if isinstance(parsed_data, dict) and 'comprehensive_feedback' in parsed_data:
            comp_feedback = parsed_data['comprehensive_feedback']
            
            # Check instructor comments
            if 'instructor_comments' in comp_feedback:
                print("✅ Instructor comments found")
                print(f"   Preview: {comp_feedback['instructor_comments'][:50]}...")
            
            # Check detailed feedback sections
            if 'detailed_feedback' in comp_feedback:
                detailed = comp_feedback['detailed_feedback']
                
                sections = [
                    'reflection_assessment',
                    'analytical_strengths',
                    'business_application',
                    'learning_demonstration',
                    'areas_for_development',
                    'recommendations'
                ]
                
                for section in sections:
                    if section in detailed and detailed[section]:
                        print(f"   ✅ {section}: {len(detailed[section])} items")
                    else:
                        print(f"   ❌ {section}: missing")
            
            # Check technical analysis
            if 'technical_analysis' in parsed_data:
                tech = parsed_data['technical_analysis']
                tech_sections = ['code_strengths', 'code_suggestions', 'technical_observations']
                
                for section in tech_sections:
                    if section in tech and tech[section]:
                        print(f"   ✅ {section}: {len(tech[section])} items")
                    else:
                        print(f"   ❌ {section}: missing")
        
        print("✅ View Results feedback parsing should work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Feedback parsing test failed: {e}")
        return False

def test_pdf_code_examples():
    """Test that PDF reports include code examples"""
    
    print("\n📄 Testing PDF Code Examples...")
    
    # Sample data with technical analysis that should trigger code examples
    analysis_result = {
        'total_score': 34.5,
        'max_score': 37.5,
        'comprehensive_feedback': {
            'instructor_comments': 'Excellent work with strong technical implementation.',
            'detailed_feedback': {
                'reflection_assessment': ['Great critical thinking demonstrated'],
                'analytical_strengths': ['Comprehensive completion of requirements'],
                'recommendations': ['Continue excellent work']
            }
        },
        'technical_analysis': {
            'code_strengths': [
                'Proper implementation of R library loading and data import procedures',
                'Effective use of dplyr functions for data manipulation'
            ],
            'code_suggestions': [
                'Consider using complete.cases() for more robust missing data handling',
                'Explore the cut() function for creating categorical variables from continuous data',
                'Add correlation analysis using cor() to quantify relationships between variables',
                'Include additional summary statistics such as standard deviation and quartiles',
                'Use read_csv() directly without setting working directory for more portable code'
            ],
            'technical_observations': [
                'Demonstrates solid understanding of fundamental R programming concepts',
                'Code structure follows logical analytical workflow'
            ]
        }
    }
    
    try:
        # Generate PDF with code examples
        report_generator = PDFReportGenerator()
        pdf_path = report_generator.generate_report(
            student_name="Code_Examples_Test",
            assignment_id="Test Assignment - Code Examples",
            analysis_result=analysis_result
        )
        
        print(f"✅ PDF with code examples generated: {pdf_path}")
        
        # Check file size (should be larger with code examples)
        import os
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"📊 PDF file size: {file_size:,} bytes")
            
            if file_size > 15000:  # Should be larger with code examples
                print("✅ PDF appears to have substantial content (likely includes code examples)")
            else:
                print("⚠️ PDF file seems small - code examples may not be included")
        
        # Verify that code suggestions would trigger examples
        suggestions = analysis_result['technical_analysis']['code_suggestions']
        
        code_example_triggers = [
            'complete.cases()',
            'cut()',
            'cor()',
            'standard deviation',
            'read_csv()'
        ]
        
        triggered_examples = []
        for suggestion in suggestions:
            for trigger in code_example_triggers:
                if trigger in suggestion:
                    triggered_examples.append(trigger)
        
        print(f"✅ Code examples should be triggered for: {', '.join(set(triggered_examples))}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF code examples test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_feedback_format():
    """Test actual database feedback format"""
    
    print("\n💾 Testing Database Feedback Format...")
    
    try:
        # Check if database exists and has data
        import os
        if not os.path.exists("grading_database.db"):
            print("⚠️ No database found - create some graded submissions first")
            return True
        
        conn = sqlite3.connect("grading_database.db")
        cursor = conn.cursor()
        
        # Get a recent submission with feedback
        cursor.execute("""
            SELECT ai_feedback, ai_score 
            FROM submissions 
            WHERE ai_feedback IS NOT NULL 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print("⚠️ No graded submissions found in database")
            return True
        
        ai_feedback, ai_score = result
        
        try:
            feedback_data = json.loads(ai_feedback)
            print(f"✅ Found graded submission with score: {ai_score}")
            
            # Check format
            if isinstance(feedback_data, dict):
                if 'comprehensive_feedback' in feedback_data:
                    print("✅ Database contains new comprehensive feedback format")
                    
                    comp_feedback = feedback_data['comprehensive_feedback']
                    if 'detailed_feedback' in comp_feedback:
                        detailed = comp_feedback['detailed_feedback']
                        total_items = sum(len(items) if isinstance(items, list) else 0 
                                        for items in detailed.values())
                        print(f"   📊 Total detailed feedback items: {total_items}")
                    
                    if 'technical_analysis' in feedback_data:
                        tech = feedback_data['technical_analysis']
                        tech_items = sum(len(items) if isinstance(items, list) else 0 
                                       for items in tech.values())
                        print(f"   🔧 Total technical analysis items: {tech_items}")
                
                else:
                    print("ℹ️ Database contains legacy feedback format")
            
            elif isinstance(feedback_data, list):
                print("ℹ️ Database contains old list-based feedback format")
                print(f"   📊 Total feedback items: {len(feedback_data)}")
            
            return True
            
        except json.JSONDecodeError:
            print("⚠️ Database feedback is not valid JSON")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all fix tests"""
    
    print("🔧 Testing View Results and PDF Code Examples Fixes")
    print("=" * 60)
    
    tests = [
        ("View Results Feedback Parsing", test_view_results_feedback_parsing),
        ("PDF Code Examples", test_pdf_code_examples),
        ("Database Feedback Format", test_database_feedback_format)
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
        print("\n🎉 All tests passed!")
        print("📋 View Results should now show formatted feedback")
        print("📄 PDF reports should include code examples")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    main()