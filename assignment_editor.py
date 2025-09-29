import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime
from rubric_manager import RubricManager, load_predefined_rubrics
from assignment_matcher import match_assignment_to_rubric, suggest_rubric_for_assignment, get_assignment_type_from_name
from migration_helper import show_rubric_compatibility_check

def assignment_management_page(grader):
    """Enhanced assignment management with JSON upload and editing capabilities"""
    st.header("📋 Assignment Management")
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Assignment", "✏️ Edit Assignments", "📊 Assignment Overview", "🔄 Migration Helper"])
    
    with tab1:
        create_assignment_with_upload(grader)
    
    with tab2:
        edit_assignments(grader)
    
    with tab3:
        assignment_overview(grader)
    
    with tab4:
        migration_helper_tab(grader)

def create_assignment_with_upload(grader):
    """Create assignment with JSON file upload for rubric"""
    st.subheader("Create New Assignment")
    
    with st.form("create_assignment_enhanced"):
        col1, col2 = st.columns(2)
        
        with col1:
            assignment_name = st.text_input("Assignment Name", placeholder="e.g., Homework 2 - Data Cleaning")
            description = st.text_area("Description", placeholder="Brief description of the assignment")
            total_points = st.number_input("Total Points", min_value=1.0, value=37.5, step=0.5)
            
            # Show assignment type suggestion
            if assignment_name:
                assignment_type = get_assignment_type_from_name(assignment_name)
                st.info(f"🎯 Detected assignment type: **{assignment_type}**")
                
                # Show rubric suggestion
                suggestion = suggest_rubric_for_assignment(assignment_name)
                st.info(f"💡 Suggested rubric: {suggestion}")
        
        with col2:
            st.subheader("📁 File Uploads")
            template_file = st.file_uploader("Template Notebook", type=['ipynb'], key="template_upload")
            solution_file = st.file_uploader("Solution Notebook", type=['ipynb'], key="solution_upload")
        
        st.subheader("📋 Grading Rubric")
        rubric_method = st.radio("Rubric Input Method:", ["Upload JSON File", "Manual Entry"])
        
        rubric_data = {}
        rubric_manager = RubricManager(grader)
        
        if rubric_method == "Upload JSON File":
            # Option to use predefined rubrics
            predefined_rubrics = load_predefined_rubrics()
            if predefined_rubrics:
                st.write("**Choose from predefined rubrics:**")
                
                # Try to auto-suggest the best rubric
                suggested_rubric = None
                if assignment_name:
                    suggested_rubric = match_assignment_to_rubric(assignment_name, predefined_rubrics)
                
                predefined_options = ["Upload new file..."] + list(predefined_rubrics.keys())
                
                # Set default to suggested rubric if found
                default_index = 0
                if suggested_rubric and suggested_rubric in predefined_options:
                    default_index = predefined_options.index(suggested_rubric)
                    st.success(f"🎯 Auto-suggested: **{suggested_rubric}** (based on assignment name)")
                
                selected_predefined = st.selectbox(
                    "Predefined Rubrics", 
                    predefined_options,
                    index=default_index
                )
                
                if selected_predefined != "Upload new file...":
                    rubric_data = predefined_rubrics[selected_predefined]
                    st.success(f"✅ Loaded predefined rubric: {selected_predefined}")
            
            if not rubric_data:  # Only show file uploader if no predefined rubric selected
                rubric_file = st.file_uploader("Upload Rubric JSON", type=['json'], key="rubric_upload")
                if rubric_file:
                    try:
                        rubric_data = json.load(rubric_file)
                        st.success("✅ Rubric JSON loaded successfully!")
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Invalid JSON format: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error reading rubric file: {str(e)}")
            
            # Validate and show preview if rubric loaded
            if rubric_data:
                # Validate rubric structure
                validation_errors = rubric_manager.validate_rubric_structure(rubric_data)
                if validation_errors:
                    st.error("❌ Rubric validation errors:")
                    for error in validation_errors:
                        st.error(f"  • {error}")
                else:
                    st.success("✅ Rubric structure is valid!")
                
                # Show preview of loaded rubric
                with st.expander("📋 Rubric Preview"):
                    summary = rubric_manager.get_rubric_summary(rubric_data)
                    if isinstance(summary, dict):
                        st.write(f"**Title:** {summary['title']}")
                        st.write(f"**Total Points:** {summary['total_points']}")
                        st.write(f"**Elements:** {summary['element_count']}")
                        
                        st.write("**Rubric Elements:**")
                        for element in summary['elements']:
                            st.write(f"- **{element['name']}**: {element['points']} points - {element['description']}")
                    else:
                        st.error(summary)
                    
                    # Show full JSON in collapsible section
                    with st.expander("🔍 Full JSON Structure"):
                        st.json(rubric_data)
        else:
            rubric_text = st.text_area(
                "Rubric (JSON format)",
                placeholder='''
{
    "assignment_info": {
        "title": "Assignment Title",
        "total_points": 37.5
    },
    "rubric_elements": {
        "element1": {
            "max_points": 10,
            "description": "Description of element"
        }
    }
}
                ''',
                height=300
            )
            
            if rubric_text:
                try:
                    rubric_data = json.loads(rubric_text)
                    st.success("✅ Rubric JSON is valid!")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {str(e)}")
        
        submitted = st.form_submit_button("🚀 Create Assignment", type="primary")
        
        if submitted:
            create_assignment_in_db(grader, assignment_name, description, total_points, 
                                  rubric_data, template_file, solution_file)

def create_assignment_in_db(grader, name, description, total_points, rubric_data, template_file, solution_file):
    """Save assignment to database with proper error handling"""
    try:
        if not name.strip():
            st.error("❌ Assignment name is required!")
            return
            
        if not rubric_data:
            st.error("❌ Rubric is required!")
            return
        
        # Save uploaded files
        template_path = None
        solution_path = None
        
        if template_file:
            template_path = os.path.join(grader.assignments_dir, f"{name}_template.ipynb")
            os.makedirs(grader.assignments_dir, exist_ok=True)
            with open(template_path, "wb") as f:
                f.write(template_file.getbuffer())
        
        if solution_file:
            solution_path = os.path.join(grader.assignments_dir, f"{name}_solution.ipynb")
            os.makedirs(grader.assignments_dir, exist_ok=True)
            with open(solution_path, "wb") as f:
                f.write(solution_file.getbuffer())
        
        # Save to database
        conn = sqlite3.connect(grader.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO assignments (name, description, total_points, rubric, template_notebook, solution_notebook)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, total_points, json.dumps(rubric_data), template_path, solution_path))
        
        conn.commit()
        conn.close()
        
        st.success(f"🎉 Assignment '{name}' created successfully!")
        st.balloons()
        
        # Show summary
        with st.expander("📋 Assignment Summary"):
            st.write(f"**Name:** {name}")
            st.write(f"**Description:** {description}")
            st.write(f"**Total Points:** {total_points}")
            st.write(f"**Template:** {'✅ Uploaded' if template_file else '❌ Not provided'}")
            st.write(f"**Solution:** {'✅ Uploaded' if solution_file else '❌ Not provided'}")
            st.write(f"**Rubric Elements:** {len(rubric_data.get('rubric_elements', {}))}")
        
    except sqlite3.IntegrityError:
        st.error(f"❌ Assignment '{name}' already exists! Please choose a different name.")
    except Exception as e:
        st.error(f"❌ Error creating assignment: {str(e)}")

def edit_assignments(grader):
    """Edit existing assignments and their rubrics"""
    st.subheader("Edit Existing Assignments")
    
    # Load assignments
    conn = sqlite3.connect(grader.db_path)
    assignments = pd.read_sql_query(
        "SELECT id, name, description, total_points, rubric, created_date FROM assignments ORDER BY created_date DESC", 
        conn
    )
    conn.close()
    
    if assignments.empty:
        st.info("📝 No assignments found. Create your first assignment in the 'Create Assignment' tab!")
        return
    
    # Select assignment to edit
    assignment_options = {f"{row['name']} (ID: {row['id']})": row['id'] for _, row in assignments.iterrows()}
    selected_assignment = st.selectbox("Select Assignment to Edit:", list(assignment_options.keys()))
    
    if selected_assignment:
        assignment_id = assignment_options[selected_assignment]
        assignment_data = assignments[assignments['id'] == assignment_id].iloc[0]
        
        # Display current assignment info
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Current Assignment Info")
            st.write(f"**Name:** {assignment_data['name']}")
            st.write(f"**Description:** {assignment_data['description']}")
            st.write(f"**Total Points:** {assignment_data['total_points']}")
            st.write(f"**Created:** {assignment_data['created_date']}")
        
        with col2:
            st.subheader("📊 Current Rubric")
            try:
                current_rubric = json.loads(assignment_data['rubric']) if assignment_data['rubric'] else {}
                if current_rubric:
                    st.json(current_rubric)
                else:
                    st.info("No rubric data available")
            except:
                st.error("Invalid rubric data in database")
        
        st.markdown("---")
        
        # Edit form
        with st.form(f"edit_assignment_{assignment_id}"):
            st.subheader("✏️ Edit Assignment")
            
            new_name = st.text_input("Assignment Name", value=assignment_data['name'])
            new_description = st.text_area("Description", value=assignment_data['description'] or "")
            new_total_points = st.number_input("Total Points", value=float(assignment_data['total_points']), step=0.5)
            
            st.subheader("📋 Update Rubric")
            rubric_update_method = st.radio("Rubric Update Method:", ["Upload New JSON File", "Edit Current JSON"])
            
            new_rubric_data = {}
            if rubric_update_method == "Upload New JSON File":
                new_rubric_file = st.file_uploader("Upload New Rubric JSON", type=['json'], key=f"edit_rubric_{assignment_id}")
                if new_rubric_file:
                    try:
                        new_rubric_data = json.load(new_rubric_file)
                        st.success("✅ New rubric loaded!")
                        with st.expander("📋 New Rubric Preview"):
                            st.json(new_rubric_data)
                    except Exception as e:
                        st.error(f"❌ Error reading new rubric: {str(e)}")
            else:
                current_rubric_text = json.dumps(current_rubric, indent=2) if current_rubric else "{}"
                new_rubric_text = st.text_area("Edit Rubric JSON", value=current_rubric_text, height=300)
                try:
                    new_rubric_data = json.loads(new_rubric_text)
                    st.success("✅ Rubric JSON is valid!")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {str(e)}")
            
            col1, col2 = st.columns(2)
            with col1:
                update_submitted = st.form_submit_button("💾 Update Assignment", type="primary")
            with col2:
                delete_submitted = st.form_submit_button("🗑️ Delete Assignment", type="secondary")
            
            if update_submitted:
                update_assignment_in_db(grader, assignment_id, new_name, new_description, 
                                      new_total_points, new_rubric_data)
            
            if delete_submitted:
                delete_assignment_from_db(grader, assignment_id, assignment_data['name'])

def update_assignment_in_db(grader, assignment_id, name, description, total_points, rubric_data):
    """Update assignment in database"""
    try:
        conn = sqlite3.connect(grader.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE assignments 
            SET name = ?, description = ?, total_points = ?, rubric = ?
            WHERE id = ?
        ''', (name, description, total_points, json.dumps(rubric_data), assignment_id))
        
        conn.commit()
        conn.close()
        
        st.success(f"✅ Assignment updated successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error updating assignment: {str(e)}")

def delete_assignment_from_db(grader, assignment_id, assignment_name):
    """Delete assignment from database with confirmation"""
    if st.session_state.get(f'confirm_delete_{assignment_id}', False):
        try:
            conn = sqlite3.connect(grader.db_path)
            cursor = conn.cursor()
            
            # Check for existing submissions
            cursor.execute("SELECT COUNT(*) FROM submissions WHERE assignment_id = ?", (assignment_id,))
            submission_count = cursor.fetchone()[0]
            
            if submission_count > 0:
                st.warning(f"⚠️ This assignment has {submission_count} submissions. Deleting will remove all associated data!")
                if st.button("🗑️ Confirm Delete (This will remove all submissions!)", type="secondary"):
                    cursor.execute("DELETE FROM submissions WHERE assignment_id = ?", (assignment_id,))
                    cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"🗑️ Assignment '{assignment_name}' and all submissions deleted!")
                    st.rerun()
            else:
                cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
                conn.commit()
                conn.close()
                st.success(f"🗑️ Assignment '{assignment_name}' deleted!")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error deleting assignment: {str(e)}")
    else:
        st.warning(f"⚠️ Are you sure you want to delete '{assignment_name}'?")
        if st.button("🗑️ Yes, Delete Assignment", key=f"confirm_delete_{assignment_id}"):
            st.session_state[f'confirm_delete_{assignment_id}'] = True
            st.rerun()

def assignment_overview(grader):
    """Overview of all assignments with statistics"""
    st.subheader("📊 Assignment Overview")
    
    # Load assignments with submission counts
    conn = sqlite3.connect(grader.db_path)
    
    query = '''
    SELECT 
        a.id,
        a.name,
        a.description,
        a.total_points,
        a.created_date,
        COUNT(s.id) as submission_count,
        AVG(s.final_score) as avg_score,
        COUNT(CASE WHEN s.final_score IS NOT NULL THEN 1 END) as graded_count
    FROM assignments a
    LEFT JOIN submissions s ON a.id = s.assignment_id
    GROUP BY a.id, a.name, a.description, a.total_points, a.created_date
    ORDER BY a.created_date DESC
    '''
    
    assignments = pd.read_sql_query(query, conn)
    conn.close()
    
    if assignments.empty:
        st.info("📝 No assignments found.")
        return
    
    # Display assignments in cards
    for _, assignment in assignments.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.subheader(f"📋 {assignment['name']}")
                st.write(f"**Description:** {assignment['description'] or 'No description'}")
                st.caption(f"Created: {assignment['created_date']}")
            
            with col2:
                st.metric("Total Points", f"{assignment['total_points']}")
            
            with col3:
                st.metric("Submissions", f"{assignment['submission_count']}")
                st.metric("Graded", f"{assignment['graded_count']}")
            
            with col4:
                if assignment['graded_count'] > 0:
                    avg_score = assignment['avg_score'] or 0
                    st.metric("Avg Score", f"{avg_score:.1f}")
                    st.metric("Avg %", f"{(avg_score/assignment['total_points']*100):.1f}%")
                else:
                    st.metric("Avg Score", "N/A")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"✏️ Edit", key=f"edit_btn_{assignment['id']}"):
                    st.session_state.selected_assignment_for_edit = assignment['id']
            with col2:
                if st.button(f"📊 View Results", key=f"results_btn_{assignment['id']}"):
                    st.session_state.page = "View Results"
                    st.session_state.selected_assignment = assignment['id']
            with col3:
                if st.button(f"🎯 Grade", key=f"grade_btn_{assignment['id']}"):
                    st.session_state.page = "Grade Submissions"
                    st.session_state.selected_assignment = assignment['id']
            
            st.markdown("---")

def migration_helper_tab(grader):
    """Migration helper tab content"""
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
    
    st.write(f"Found **{len(assignments)}** assignments and **{len(predefined_rubrics)}** predefined rubrics.")
    
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
    
    st.warning(f"⚠️ **{len(migration_needed)}** assignments need rubric updates:")
    
    # Show migration options
    for item in migration_needed:
        assignment = item['assignment']
        issues = item['issues']
        suggested_rubric = item['suggested_rubric']
        
        with st.expander(f"📋 {assignment['name']} (ID: {assignment['id']})"):
            st.write(f"**Issues:** {', '.join(issues)}")
            
            if suggested_rubric:
                st.write(f"**Suggested Rubric:** {suggested_rubric}")
                
                # Show compatibility check
                rubric_data = predefined_rubrics[suggested_rubric]
                try:
                    is_compatible = show_rubric_compatibility_check(assignment['name'], rubric_data)
                except:
                    st.info("Compatibility check not available")
                
                if st.button(f"Apply {suggested_rubric}", key=f"apply_{assignment['id']}"):
                    # Apply the suggested rubric
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
                    
                    # Show compatibility for manual selection
                    if selected_manual:
                        rubric_data = predefined_rubrics[selected_manual]
                        try:
                            is_compatible = show_rubric_compatibility_check(assignment['name'], rubric_data)
                        except:
                            st.info("Compatibility check not available")
                    
                    if st.button(f"Apply {selected_manual}", key=f"manual_apply_{assignment['id']}"):
                        rubric_data = predefined_rubrics[selected_manual]
                        success, message = rubric_manager.update_assignment_rubric(assignment['id'], rubric_data)
                        
                        if success:
                            st.success(f"✅ Applied {selected_manual} to {assignment['name']}")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to apply rubric: {message}")

def get_assignment_rubric(grader, assignment_id):
    """Helper function to get rubric for a specific assignment"""
    try:
        conn = sqlite3.connect(grader.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT rubric FROM assignments WHERE id = ?", (assignment_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return json.loads(result[0])
        return {}
    except Exception as e:
        st.error(f"Error loading rubric: {str(e)}")
        return {}