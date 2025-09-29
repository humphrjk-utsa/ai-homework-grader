import sqlite3
import json
import pandas as pd
import streamlit as st
from rubric_manager import RubricManager, load_predefined_rubrics
from assignment_matcher import match_assignment_to_rubric

def migrate_existing_assignments(grader):
    """Help migrate existing assignments to use proper rubrics"""
    st.subheader("🔄 Assignment Migration Helper")
    st.write("This tool helps ensure existing assignments have proper rubrics assigned.")
    
    # Load existing assignments
    conn = sqlite3.connect(grader.db_path)
    assignments = pd.read_sql_query(
        "SELECT id, name, description, total_points, rubric FROM assignments ORDER BY created_date DESC", 
        conn
    )
    conn.close()
    
    if assignments.empty:
        st.info("No assignments found to migrate.")
        return
    
    # Load available rubrics
    predefined_rubrics = load_predefined_rubrics()
    rubric_manager = RubricManager(grader)
    
    st.write(f"Found {len(assignments)} assignments and {len(predefined_rubrics)} predefined rubrics.")
    
    # Check each assignment
    migration_needed = []
    for _, assignment in assignments.iterrows():
        current_rubric = {}
        if assignment['rubric']:
            try:
                current_rubric = json.loads(assignment['rubric'])
            except:
                pass
        
        # Check if rubric needs updating
        needs_migration = False
        issues = []
        
        if not current_rubric:
            needs_migration = True
            issues.append("No rubric assigned")
        else:
            # Validate current rubric
            validation_errors = rubric_manager.validate_rubric_structure(current_rubric)
            if validation_errors:
                needs_migration = True
                issues.append(f"Rubric validation errors: {len(validation_errors)}")
        
        if needs_migration:
            # Suggest a rubric
            suggested_rubric = match_assignment_to_rubric(assignment['name'], predefined_rubrics)
            migration_needed.append({
                'assignment': assignment,
                'issues': issues,
                'suggested_rubric': suggested_rubric
            })
    
    if not migration_needed:
        st.success("✅ All assignments have valid rubrics!")
        return
    
    st.warning(f"⚠️ {len(migration_needed)} assignments need rubric updates:")
    
    # Show migration options
    for item in migration_needed:
        assignment = item['assignment']
        issues = item['issues']
        suggested_rubric = item['suggested_rubric']
        
        with st.expander(f"📋 {assignment['name']} (ID: {assignment['id']})"):
            st.write(f"**Issues:** {', '.join(issues)}")
            
            if suggested_rubric:
                st.write(f"**Suggested Rubric:** {suggested_rubric}")
                
                if st.button(f"Apply {suggested_rubric}", key=f"apply_{assignment['id']}"):
                    # Apply the suggested rubric
                    rubric_data = predefined_rubrics[suggested_rubric]
                    success, message = rubric_manager.update_assignment_rubric(assignment['id'], rubric_data)
                    
                    if success:
                        st.success(f"✅ Applied {suggested_rubric} to {assignment['name']}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to apply rubric: {message}")
            else:
                st.write("**No automatic suggestion available**")
                
                # Manual rubric selection
                manual_options = list(predefined_rubrics.keys())
                if manual_options:
                    selected_manual = st.selectbox(
                        "Choose rubric manually:", 
                        manual_options,
                        key=f"manual_{assignment['id']}"
                    )
                    
                    if st.button(f"Apply {selected_manual}", key=f"manual_apply_{assignment['id']}"):
                        rubric_data = predefined_rubrics[selected_manual]
                        success, message = rubric_manager.update_assignment_rubric(assignment['id'], rubric_data)
                        
                        if success:
                            st.success(f"✅ Applied {selected_manual} to {assignment['name']}")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to apply rubric: {message}")

def check_assignment_rubric_compatibility(assignment_name, rubric_data):
    """Check if a rubric is compatible with an assignment"""
    compatibility_score = 0
    issues = []
    suggestions = []
    
    if not rubric_data:
        return 0, ["No rubric data"], ["Add a rubric to enable grading"]
    
    # Check basic structure
    if "assignment_info" in rubric_data:
        compatibility_score += 20
        info = rubric_data["assignment_info"]
        
        # Check if assignment name matches rubric title
        if "title" in info:
            title_lower = info["title"].lower()
            name_lower = assignment_name.lower()
            
            # Look for common keywords
            if any(word in title_lower for word in name_lower.split()):
                compatibility_score += 10
            else:
                suggestions.append("Consider updating rubric title to match assignment name")
    else:
        issues.append("Missing assignment_info section")
    
    if "rubric_elements" in rubric_data:
        compatibility_score += 20
        elements = rubric_data["rubric_elements"]
        
        if len(elements) > 0:
            compatibility_score += 10
        else:
            issues.append("No rubric elements defined")
    else:
        issues.append("Missing rubric_elements section")
    
    # Check for assignment-specific compatibility
    assignment_lower = assignment_name.lower()
    
    if "data" in assignment_lower or "cleaning" in assignment_lower:
        # This should be a data cleaning assignment
        rubric_content = str(rubric_data).lower()
        if any(keyword in rubric_content for keyword in ["missing", "outlier", "cleaning", "imputation"]):
            compatibility_score += 15
            suggestions.append("Good match for data cleaning assignment")
        else:
            issues.append("Assignment appears to be about data cleaning, but rubric doesn't contain related keywords")
    
    if "intro" in assignment_lower or "environment" in assignment_lower:
        # This should be an intro assignment
        rubric_content = str(rubric_data).lower()
        if any(keyword in rubric_content for keyword in ["environment", "setup", "import", "tidyverse"]):
            compatibility_score += 15
            suggestions.append("Good match for introduction/setup assignment")
        else:
            issues.append("Assignment appears to be introductory, but rubric doesn't contain setup-related keywords")
    
    return compatibility_score, issues, suggestions

def show_rubric_compatibility_check(assignment_name, rubric_data):
    """Show compatibility check results in Streamlit"""
    score, issues, suggestions = check_assignment_rubric_compatibility(assignment_name, rubric_data)
    
    # Show compatibility score
    if score >= 70:
        st.success(f"✅ High compatibility: {score}/100")
    elif score >= 50:
        st.warning(f"⚠️ Moderate compatibility: {score}/100")
    else:
        st.error(f"❌ Low compatibility: {score}/100")
    
    # Show issues
    if issues:
        st.write("**Issues:**")
        for issue in issues:
            st.error(f"• {issue}")
    
    # Show suggestions
    if suggestions:
        st.write("**Suggestions:**")
        for suggestion in suggestions:
            st.info(f"• {suggestion}")
    
    return score >= 50  # Return True if compatibility is acceptable