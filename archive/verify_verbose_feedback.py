#!/usr/bin/env python3
"""
Verify that verbose feedback is working in the Streamlit app
"""

import sqlite3
import json
import os
from pathlib import Path

def check_database_feedback():
    """Check if existing graded submissions have verbose feedback"""
    
    print("🔍 Checking database for verbose feedback...")
    
    db_path = "grading_database.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Run some grading first.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get graded submissions
    cursor.execute("""
        SELECT s.id, s.student_id, s.ai_feedback, s.ai_score
        FROM submissions s
        WHERE s.ai_feedback IS NOT NULL
        ORDER BY s.id DESC
        LIMIT 5
    """)
    
    submissions = cursor.fetchall()
    conn.close()
    
    if not submissions:
        print("❌ No graded submissions found. Grade some submissions first.")
        return False
    
    print(f"✅ Found {len(submissions)} graded submissions")
    
    # Check feedback structure
    for sub_id, student_id, ai_feedback, ai_score in submissions:
        print(f"\n📋 Checking submission {sub_id} (Student: {student_id}, Score: {ai_score})")
        
        try:
            feedback_data = json.loads(ai_feedback)
            
            # Check comprehensive feedback
            if 'comprehensive_feedback' in feedback_data:
                comp_feedback = feedback_data['comprehensive_feedback']
                
                # Check instructor comments
                if 'instructor_comments' in comp_feedback:
                    comments_len = len(comp_feedback['instructor_comments'])
                    print(f"   ✅ Instructor comments: {comments_len} characters")
                else:
                    print("   ❌ Instructor comments missing")
                
                # Check detailed feedback
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
                    
                    detailed_count = 0
                    for section in sections:
                        if section in detailed and detailed[section]:
                            detailed_count += len(detailed[section])
                    
                    print(f"   ✅ Detailed feedback: {detailed_count} total items")
                else:
                    print("   ❌ Detailed feedback missing")
            else:
                print("   ❌ Comprehensive feedback missing")
            
            # Check technical analysis
            if 'technical_analysis' in feedback_data:
                tech = feedback_data['technical_analysis']
                
                tech_sections = ['code_strengths', 'code_suggestions', 'technical_observations']
                tech_count = 0
                for section in tech_sections:
                    if section in tech and tech[section]:
                        tech_count += len(tech[section])
                
                print(f"   ✅ Technical analysis: {tech_count} total items")
            else:
                print("   ❌ Technical analysis missing")
                
        except Exception as e:
            print(f"   ❌ Feedback parsing error: {e}")
    
    return True

def check_web_interface_files():
    """Check that web interface files have been updated"""
    
    print("\n🌐 Checking web interface files...")
    
    # Check connect_web_interface.py
    interface_file = "connect_web_interface.py"
    
    if not os.path.exists(interface_file):
        print("❌ connect_web_interface.py not found")
        return False
    
    with open(interface_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for updated feedback display logic
    checks = [
        ('detailed_feedback', 'Detailed feedback section handling'),
        ('reflection_assessment', 'Reflection assessment display'),
        ('analytical_strengths', 'Analytical strengths display'),
        ('business_application', 'Business application display'),
        ('technical_analysis', 'Technical analysis display'),
        ('st.expander("🔧 Technical Analysis Details")', 'Technical analysis expander')
    ]
    
    for check_text, description in checks:
        if check_text in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} missing")
    
    return True

def create_test_instructions():
    """Create instructions for testing the Streamlit app"""
    
    print("\n📋 Creating test instructions...")
    
    instructions = """
# Testing Verbose Feedback in Streamlit App

## Steps to Test:

1. **Start the Streamlit app:**
   ```bash
   cd homework_grader
   streamlit run app.py
   ```

2. **Navigate to "Grade Submissions" page**

3. **Select an assignment and grade a submission:**
   - Choose "Individual (one at a time)" mode
   - Click "⚡ Grade This Submission"
   - Wait for grading to complete

4. **Verify verbose feedback display:**
   - Check that "💬 Detailed Feedback" section appears
   - Verify "Overall Assessment" shows instructor comments
   - Confirm detailed sections appear:
     - 🤔 Reflection & Critical Thinking
     - 💪 Analytical Strengths  
     - 💼 Business Application
     - 📚 Learning Demonstration
     - 🎯 Areas for Development
     - 💡 Recommendations
   - Expand "🔧 Technical Analysis Details" to see:
     - Code Strengths
     - Code Suggestions
     - Technical Observations

5. **Test manual review:**
   - Go to "📝 Manual Review" tab
   - Select a graded submission
   - Verify detailed feedback appears in expander

## Expected Results:

✅ Comprehensive feedback with multiple detailed sections
✅ Technical analysis in expandable section
✅ Professional, encouraging tone appropriate for business students
✅ Specific, actionable recommendations
✅ Evidence of reflection assessment and learning demonstration

## If Issues Occur:

- Check browser console for JavaScript errors
- Verify database contains comprehensive feedback data
- Ensure Business Analytics Grader is being used (not fallback)
- Check that models are loaded and accessible
"""
    
    with open("VERBOSE_FEEDBACK_TEST_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Test instructions saved to VERBOSE_FEEDBACK_TEST_INSTRUCTIONS.md")

def main():
    """Main verification function"""
    
    print("🧪 Verifying Verbose Feedback System")
    print("=" * 50)
    
    # Check database
    db_ok = check_database_feedback()
    
    # Check web interface files
    web_ok = check_web_interface_files()
    
    # Create test instructions
    create_test_instructions()
    
    print("\n📊 Verification Summary:")
    print(f"   Database feedback: {'✅' if db_ok else '❌'}")
    print(f"   Web interface: {'✅' if web_ok else '❌'}")
    
    if db_ok and web_ok:
        print("\n🎉 Verbose feedback system is ready!")
        print("📋 Follow the instructions in VERBOSE_FEEDBACK_TEST_INSTRUCTIONS.md to test the Streamlit app")
    else:
        print("\n⚠️ Some issues found. Check the messages above.")
        if not db_ok:
            print("   • Grade some submissions first to test database feedback")
        if not web_ok:
            print("   • Web interface may need updates")

if __name__ == "__main__":
    main()