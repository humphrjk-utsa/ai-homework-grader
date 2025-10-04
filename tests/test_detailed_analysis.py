#!/usr/bin/env python3
"""
Test the detailed homework analysis system
"""

import sys
sys.path.append('.')

from detailed_analyzer import DetailedHomeworkAnalyzer, format_detailed_feedback

def test_detailed_analysis():
    """Test the detailed analysis on the homework assignment"""
    print("🧪 Testing Detailed Homework Analysis")
    print("=" * 50)
    
    analyzer = DetailedHomeworkAnalyzer()
    
    # Test with the actual homework file
    homework_file = "../assignment/Homework/homework_lesson_1.ipynb"
    
    try:
        print(f"📓 Analyzing: {homework_file}")
        analysis = analyzer.analyze_notebook(homework_file)
        
        print(f"\n📊 **ANALYSIS RESULTS:**")
        print(f"Total Score: {analysis['total_score']:.1f} / {analysis['max_score']}")
        print(f"Percentage: {(analysis['total_score']/analysis['max_score']*100):.1f}%")
        
        print(f"\n📋 **ELEMENT SCORES:**")
        for element, score in analysis['element_scores'].items():
            print(f"  • {element}: {score}")
        
        print(f"\n❌ **MISSING ELEMENTS ({len(analysis['missing_elements'])}):**")
        for element in analysis['missing_elements']:
            print(f"  • {element}")
        
        print(f"\n⚠️ **CODE ISSUES ({len(analysis['code_issues'])}):**")
        for issue in analysis['code_issues']:
            print(f"  • {issue}")
        
        print(f"\n💭 **QUESTION ANALYSIS:**")
        for q_key, q_data in analysis['question_analysis'].items():
            print(f"  • {q_key}: {q_data['quality']} ({q_data['score']:.1f}/{q_data['max_score']})")
        
        print(f"\n📝 **FORMATTED FEEDBACK:**")
        print("=" * 30)
        feedback = format_detailed_feedback(analysis)
        for line in feedback:
            print(line)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_sample_notebook():
    """Test with a sample notebook that has some content"""
    print(f"\n🧪 Testing with Sample Solution Notebook")
    print("=" * 50)
    
    analyzer = DetailedHomeworkAnalyzer()
    
    # Test with sample solution
    sample_file = "sample_solution.ipynb"
    
    try:
        print(f"📓 Analyzing: {sample_file}")
        analysis = analyzer.analyze_notebook(sample_file)
        
        print(f"\n📊 **SAMPLE ANALYSIS RESULTS:**")
        print(f"Total Score: {analysis['total_score']:.1f} / {analysis['max_score']}")
        print(f"Percentage: {(analysis['total_score']/analysis['max_score']*100):.1f}%")
        
        print(f"\n📋 **ELEMENT BREAKDOWN:**")
        for element, score in analysis['element_scores'].items():
            max_score = analyzer.required_elements.get(element, {}).get('points', 'unknown')
            print(f"  • {element}: {score} / {max_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with sample: {e}")
        return False

if __name__ == "__main__":
    print("🎓 Detailed Homework Analysis Test Suite")
    print("=" * 60)
    
    success1 = test_detailed_analysis()
    success2 = test_with_sample_notebook()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests completed! The detailed analysis system is working.")
        print("💡 This will provide specific feedback on what students did/didn't do.")
    else:
        print("⚠️ Some tests had issues. Check the errors above.")
    
    print("\n🔧 **What this system provides:**")
    print("• Specific identification of missing elements")
    print("• Detailed scoring breakdown by category") 
    print("• Analysis of reflection question quality")
    print("• Code execution issue detection")
    print("• Actionable recommendations for improvement")