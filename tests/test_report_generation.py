#!/usr/bin/env python3
"""
Test the report generation system
"""

import sys
import os
sys.path.append('.')

from report_generator import StudentReportGenerator
from detailed_analyzer import DetailedHomeworkAnalyzer

def test_report_generation():
    """Test generating student reports"""
    print("📝 Testing Student Report Generation")
    print("=" * 50)
    
    # Analyze a sample notebook
    analyzer = DetailedHomeworkAnalyzer()
    
    # Use the homework assignment as test data
    notebook_path = "../assignment/Homework/homework_lesson_1.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"❌ Test notebook not found: {notebook_path}")
        return False
    
    print(f"📓 Analyzing: {notebook_path}")
    analysis = analyzer.analyze_notebook(notebook_path)
    
    print(f"📊 Analysis complete: {analysis['total_score']:.1f}/{analysis['max_score']} points")
    
    # Generate reports
    report_generator = StudentReportGenerator()
    
    test_student_id = "john_doe_123"
    test_assignment = "Homework 1 - Intro to R"
    
    print(f"\n📝 Generating reports for: {test_student_id}")
    
    try:
        reports = report_generator.generate_student_report(
            test_student_id, test_assignment, analysis
        )
        
        print("✅ Reports generated successfully!")
        
        for format_type, file_path in reports.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"  📄 {format_type.upper()}: {file_path} ({file_size:.1f} KB)")
            else:
                print(f"  ❌ {format_type.upper()}: File not created")
        
        # Show sample HTML content
        if 'html' in reports and os.path.exists(reports['html']):
            print(f"\n📄 Sample HTML Report Preview:")
            with open(reports['html'], 'r', encoding='utf-8') as f:
                content = f.read()
                # Show first 500 characters
                preview = content[:500] + "..." if len(content) > 500 else content
                print(preview)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating reports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_students():
    """Test generating reports for multiple students"""
    print(f"\n👥 Testing Multiple Student Reports")
    print("=" * 40)
    
    analyzer = DetailedHomeworkAnalyzer()
    report_generator = StudentReportGenerator()
    
    # Simulate different student performance levels
    test_students = [
        {
            'id': 'alice_smith_456',
            'notebook': '../assignment/Homework/homework_lesson_1.ipynb',
            'performance': 'high'
        },
        {
            'id': 'bob_jones_789', 
            'notebook': 'sample_solution.ipynb',
            'performance': 'medium'
        }
    ]
    
    generated_reports = []
    
    for student in test_students:
        if os.path.exists(student['notebook']):
            print(f"\n📚 Processing: {student['id']}")
            
            analysis = analyzer.analyze_notebook(student['notebook'])
            
            reports = report_generator.generate_student_report(
                student['id'], "Homework 1 - Intro to R", analysis
            )
            
            generated_reports.append({
                'student': student['id'],
                'score': analysis['total_score'],
                'reports': reports
            })
            
            print(f"  Score: {analysis['total_score']:.1f}/37.5")
            print(f"  Reports: {list(reports.keys())}")
    
    print(f"\n📊 Summary:")
    print(f"Generated reports for {len(generated_reports)} students")
    
    for report in generated_reports:
        print(f"  • {report['student']}: {report['score']:.1f} points")
    
    return len(generated_reports) > 0

def show_report_features():
    """Show what features are included in the reports"""
    print(f"\n🎯 Report Features")
    print("=" * 30)
    
    features = [
        "📊 Overall score with color-coded grade",
        "📋 Detailed breakdown by category",
        "💭 Individual reflection question analysis", 
        "👨‍🏫 Professor-style feedback for each section",
        "🎯 Specific recommendations for improvement",
        "📝 Professional formatting (HTML & Word)",
        "📅 Date and assignment information",
        "🎨 Clean, student-friendly design"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n📁 Output Formats:")
    print(f"  • HTML: Opens in any web browser, easy to view")
    print(f"  • Word: Professional format, easy to print/share")
    print(f"  • Saved in: feedback_reports/ folder")

if __name__ == "__main__":
    print("🎓 Student Report Generation Test Suite")
    print("=" * 60)
    
    success1 = test_report_generation()
    success2 = test_multiple_students()
    
    show_report_features()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests passed! Report generation is working.")
        print("💡 You can now generate individual feedback reports for students.")
        print("📁 Check the 'feedback_reports' folder for generated files.")
    else:
        print("⚠️ Some tests had issues. Check the errors above.")
    
    print(f"\n🔧 Next Steps:")
    print(f"1. Grade your assignments in the Streamlit app")
    print(f"2. Click 'Generate Individual Reports' in View Results")
    print(f"3. Download or share the HTML/Word files with students")