import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from pathlib import Path
import nbformat
import shutil
import tempfile
from rubric_manager import RubricManager, load_predefined_rubrics
from assignment_matcher import match_assignment_to_rubric, suggest_rubric_for_assignment, get_assignment_type_from_name

def create_assignment_page(grader):
    st.header("📝 Create New Assignment")
    
    with st.form("create_assignment"):
        assignment_name = st.text_input("Assignment Name", placeholder="e.g., Homework 1 - Intro to R")
        description = st.text_area("Description", placeholder="Brief description of the assignment")
        total_points = st.number_input("Total Points", min_value=1, value=100)
        
        st.subheader("Grading Rubric")
        rubric_text = st.text_area(
            "Rubric (JSON format)",
            placeholder='''
{
    "code_execution": {"points": 40, "description": "Code runs without errors"},
    "correct_output": {"points": 30, "description": "Produces expected results"},
    "code_quality": {"points": 20, "description": "Clean, readable code with comments"},
    "analysis": {"points": 10, "description": "Proper interpretation of results"}
}
            ''',
            height=200
        )
        
        st.subheader("Solution Notebook")
        solution_file = st.file_uploader("Upload Solution Notebook (Required for grading)", type=['ipynb'])
        st.caption("This notebook will be used to compare student submissions during grading")
        
        submitted = st.form_submit_button("Create Assignment")
        
        if submitted:
            try:
                # Validate rubric JSON
                rubric = json.loads(rubric_text) if rubric_text else {}
                
                # Save solution notebook
                solution_path = None
                
                if solution_file:
                    solution_path = os.path.join(grader.assignments_dir, f"{assignment_name}_solution.ipynb")
                    with open(solution_path, "wb") as f:
                        f.write(solution_file.getbuffer())
                
                # Save to database
                conn = sqlite3.connect(grader.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO assignments (name, description, total_points, rubric, solution_notebook)
                    VALUES (?, ?, ?, ?, ?)
                ''', (assignment_name, description, total_points, json.dumps(rubric), solution_path))
                
                conn.commit()
                conn.close()
                
                st.success(f"Assignment '{assignment_name}' created successfully!")
                
            except json.JSONDecodeError:
                st.error("Invalid JSON format in rubric. Please check your syntax.")
            except Exception as e:
                st.error(f"Error creating assignment: {str(e)}")

def upload_submissions_page(grader):
    st.header("📤 Upload Student Submissions")
    
    # Select assignment
    conn = sqlite3.connect(grader.db_path)
    assignments = pd.read_sql_query("SELECT id, name FROM assignments ORDER BY created_date DESC", conn)
    conn.close()
    
    if assignments.empty:
        st.warning("No assignments found. Please create an assignment first.")
        return
    
    assignment_options = {row['name']: row['id'] for _, row in assignments.iterrows()}
    selected_assignment = st.selectbox("Select Assignment", list(assignment_options.keys()))
    assignment_id = assignment_options[selected_assignment]
    
    st.subheader("Upload Methods")
    upload_method = st.radio("Choose upload method:", ["Batch Upload (ZIP)", "Single File"], index=0)
    
    if upload_method == "Batch Upload (ZIP)":
        upload_batch_submissions(grader, assignment_id)
    else:
        upload_single_submission(grader, assignment_id)

def upload_single_submission(grader, assignment_id):
    st.info("📄 **Single File Upload** - Auto-extracts Canvas ID from filename")
    
    notebook_file = st.file_uploader("Upload Notebook (.ipynb)", type=['ipynb'], key="single_upload")
    
    if notebook_file:
        # Auto-extract Canvas ID and name from filename
        filename = notebook_file.name.replace('.ipynb', '')
        parsed_info = parse_github_classroom_filename(filename)
        
        # Show extracted info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Canvas ID:** {parsed_info['id']}")
        with col2:
            st.info(f"**Name:** {parsed_info['name']}")
        
        # Allow manual override
        with st.expander("✏️ Override extracted info (optional)"):
            override_id = st.text_input("Canvas ID", value=parsed_info['id'])
            override_name = st.text_input("Student Name", value=parsed_info['name'])
        
        # Use the values (either from expander or defaults)
        if 'override_id' not in locals():
            override_id = parsed_info['id']
            override_name = parsed_info['name']
        
        if st.button("📤 Upload This Submission", type="primary"):
            try:
                import nbformat
                
                # Read notebook to check for duplicates
                notebook_content = notebook_file.getvalue()
                nb = nbformat.reads(notebook_content.decode('utf-8'), as_version=4)
                
                # Save notebook
                submission_dir = os.path.join(grader.submissions_dir, str(assignment_id))
                os.makedirs(submission_dir, exist_ok=True)
                
                safe_name = override_name.replace(' ', '_')
                notebook_path = os.path.join(submission_dir, f"{safe_name}_{override_id}.ipynb")
                
                with open(notebook_path, "wb") as f:
                    f.write(notebook_content)
                
                # Save to database
                conn = sqlite3.connect(grader.db_path)
                cursor = conn.cursor()
                
                # Check if student exists
                cursor.execute('SELECT id FROM students WHERE student_id = ?', (override_id,))
                existing = cursor.fetchone()
                
                if existing:
                    student_db_id = existing[0]
                    st.info(f"🔗 Linked to existing student: {override_name}")
                else:
                    # Create new student
                    cursor.execute('''
                        INSERT INTO students (student_id, name, email)
                        VALUES (?, ?, ?)
                    ''', (override_id, override_name, f"{override_id}@university.edu"))
                    student_db_id = cursor.lastrowid
                    st.success(f"👤 Created new student: {override_name}")
                
                # Check for duplicate submission
                cursor.execute('''
                    SELECT id FROM submissions 
                    WHERE student_id = ? AND assignment_id = ?
                ''', (student_db_id, assignment_id))
                
                if cursor.fetchone():
                    st.warning(f"⚠️ {override_name} already has a submission for this assignment. Updating...")
                    cursor.execute('''
                        UPDATE submissions 
                        SET notebook_path = ?, submission_date = CURRENT_TIMESTAMP
                        WHERE student_id = ? AND assignment_id = ?
                    ''', (notebook_path, student_db_id, assignment_id))
                else:
                    # Add new submission
                    cursor.execute('''
                        INSERT INTO submissions (assignment_id, student_id, notebook_path)
                        VALUES (?, ?, ?)
                    ''', (assignment_id, student_db_id, notebook_path))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Submission uploaded for {override_name} (Canvas ID: {override_id})")
                
            except Exception as e:
                st.error(f"❌ Error uploading submission: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

def upload_batch_submissions(grader, assignment_id):
    st.info("📁 **Bulk Upload Instructions:**")
    st.write("- Upload a ZIP file containing .ipynb notebooks")
    st.write("- Notebooks should contain student names in the first markdown cell")
    st.write("- Format: **Student Name:** [Name] or Student Name: Name")
    st.write("- Filenames will be used as backup student IDs")
    
    zip_file = st.file_uploader("Upload ZIP file", type=['zip'])
    
    if zip_file:
        if st.button("Process Batch Upload"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.container()
            
            try:
                import zipfile
                import tempfile
                import nbformat
                import re
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extract ZIP
                    status_text.text("📦 Extracting ZIP file...")
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Find all notebooks
                    notebook_files = list(Path(temp_dir).rglob("*.ipynb"))
                    total_files = len(notebook_files)
                    
                    if total_files == 0:
                        st.error("❌ No .ipynb files found in the ZIP file")
                        return
                    
                    # Process notebooks
                    submission_dir = os.path.join(grader.submissions_dir, str(assignment_id))
                    os.makedirs(submission_dir, exist_ok=True)
                    
                    conn = sqlite3.connect(grader.db_path)
                    cursor = conn.cursor()
                    
                    uploaded_count = 0
                    skipped_count = 0
                    linked_count = 0
                    new_student_count = 0
                    errors = []
                    content_hashes = {}
                    
                    for i, file_path in enumerate(notebook_files):
                        progress_bar.progress((i + 1) / total_files)
                        status_text.text(f"📝 Processing {file_path.name}... ({i+1}/{total_files})")
                        
                        try:
                            # Extract student info from notebook
                            with open(file_path, 'r', encoding='utf-8') as f:
                                nb = nbformat.read(f, as_version=4)
                            
                            student_info = extract_student_info_from_notebook(nb)
                            student_name = student_info.get('name', 'Unknown')
                            
                            # Parse Canvas filename format - FIRST part is Canvas ID (primary identifier)
                            filename_id = file_path.stem
                            parsed_info = parse_github_classroom_filename(filename_id)
                            
                            # PRIORITY 1: Use Canvas ID from filename (most reliable)
                            if parsed_info and parsed_info['id']:
                                student_id = parsed_info['id']
                                # Use parsed name if available, otherwise use name from notebook
                                if parsed_info['name']:
                                    student_name = parsed_info['name']
                                elif student_name == 'Unknown':
                                    student_name = parsed_info['name']
                            # PRIORITY 2: Use info from notebook
                            elif student_info.get('id') != 'Unknown':
                                student_id = student_info.get('id')
                            # FALLBACK: Use filename
                            else:
                                student_id = filename_id
                            
                            # Check for duplicates and match to existing students
                            content_hash = hash_notebook_content(nb)
                            clean_student_id = student_id
                            
                            # First, try to find existing student by Canvas ID (student_id)
                            cursor.execute('SELECT id, name, student_id FROM students WHERE student_id = ?', (clean_student_id,))
                            existing_student = cursor.fetchone()
                            
                            if existing_student:
                                existing_student_db_id, existing_name, existing_canvas_id = existing_student
                                
                                # Check if this student already has a submission for this assignment
                                cursor.execute('''
                                    SELECT id FROM submissions 
                                    WHERE student_id = ? AND assignment_id = ?
                                ''', (existing_student_db_id, assignment_id))
                                
                                existing_submission = cursor.fetchone()
                                if existing_submission:
                                    with results_container:
                                        st.write(f"⚠️ Skipping duplicate: {existing_name} (Canvas ID: {existing_canvas_id}) already submitted")
                                    skipped_count += 1
                                    continue
                                
                                # Student exists but no submission for this assignment - use existing student
                                student_db_id = existing_student_db_id
                                with results_container:
                                    st.write(f"🔗 Linking to existing student: {existing_name} (Canvas ID: {existing_canvas_id})")
                                linked_count += 1
                            
                            else:
                                # Try to find by name (in case student_id changed)
                                cursor.execute('SELECT id, student_id FROM students WHERE name = ?', (student_name,))
                                existing_by_name = cursor.fetchone()
                                
                                if existing_by_name:
                                    existing_student_db_id, existing_student_id = existing_by_name
                                    
                                    # Check for submission
                                    cursor.execute('''
                                        SELECT id FROM submissions 
                                        WHERE student_id = ? AND assignment_id = ?
                                    ''', (existing_student_db_id, assignment_id))
                                    
                                    existing_submission = cursor.fetchone()
                                    if existing_submission:
                                        with results_container:
                                            st.write(f"⚠️ Skipping duplicate: {student_name} (existing ID: {existing_student_id}) already submitted")
                                        skipped_count += 1
                                        continue
                                    
                                    # Update student_id if it changed
                                    if existing_student_id != clean_student_id:
                                        cursor.execute('UPDATE students SET student_id = ? WHERE id = ?', 
                                                     (clean_student_id, existing_student_db_id))
                                        with results_container:
                                            st.write(f"📝 Updated student ID: {student_name} ({existing_student_id} → {clean_student_id})")
                                    
                                    student_db_id = existing_student_db_id
                                    # Use the updated ID if it was changed, otherwise use existing
                                    display_id = clean_student_id if existing_student_id != clean_student_id else existing_student_id
                                    with results_container:
                                        st.write(f"🔗 Linking to existing student: {student_name} (Canvas ID: {display_id})")
                                    linked_count += 1
                                
                                else:
                                    # New student - will be created below
                                    student_db_id = None
                            
                            # Check for identical content
                            if content_hash in content_hashes:
                                with results_container:
                                    st.write(f"⚠️ Skipping identical content: {student_name} (same as {content_hashes[content_hash]})")
                                skipped_count += 1
                                continue
                            
                            content_hashes[content_hash] = student_name
                            
                            # Create student record only if not found above
                            if student_db_id is None and student_name != 'Unknown':
                                cursor.execute('''
                                    INSERT INTO students (student_id, name, email)
                                    VALUES (?, ?, ?)
                                ''', (clean_student_id, student_name, f"{clean_student_id}@university.edu"))
                                student_db_id = cursor.lastrowid
                                
                                with results_container:
                                    st.write(f"👤 Created new student: {student_name} (ID: {clean_student_id})")
                                new_student_count += 1
                            
                            elif student_db_id is None:
                                # Fallback for unknown students
                                cursor.execute('''
                                    INSERT INTO students (student_id, name, email)
                                    VALUES (?, ?, ?)
                                ''', (filename_id, 'Unknown Student', f"{filename_id}@university.edu"))
                                student_db_id = cursor.lastrowid
                            
                            # Copy notebook with better naming
                            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', student_name.replace(' ', '_'))
                            notebook_filename = f"{safe_name}_{clean_student_id}.ipynb" if student_name != 'Unknown' else f"{filename_id}.ipynb"
                            notebook_path = os.path.join(submission_dir, notebook_filename)
                            shutil.copy2(file_path, notebook_path)
                            
                            # Add to submissions
                            cursor.execute('''
                                INSERT INTO submissions (assignment_id, student_id, notebook_path)
                                VALUES (?, ?, ?)
                            ''', (assignment_id, student_db_id, notebook_path))
                            
                            uploaded_count += 1
                            
                            with results_container:
                                st.write(f"✅ {student_name} ({student_id})")
                        
                        except Exception as e:
                            error_msg = f"❌ {file_path.name}: {str(e)}"
                            errors.append(error_msg)
                            with results_container:
                                st.write(error_msg)
                    
                    # Get database summary before closing connection
                    cursor.execute('SELECT COUNT(*) FROM students')
                    total_students = cursor.fetchone()[0]
                    
                    conn.commit()
                    conn.close()
                    
                    # Final results
                    status_text.text("✅ Batch upload completed!")
                    st.success(f"📊 **Upload Results:** {uploaded_count} submissions processed successfully!")
                    
                    # Show detailed summary
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("✅ Uploaded", uploaded_count)
                    with col2:
                        st.metric("🔗 Linked", linked_count)
                    with col3:
                        st.metric("👤 New Students", new_student_count)
                    with col4:
                        st.metric("⚠️ Skipped", skipped_count)
                    
                    if errors:
                        with st.expander(f"❌ Errors ({len(errors)})", expanded=True):
                            for error in errors:
                                st.write(error)
                    
                    # Student management summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if new_student_count > 0:
                            st.info(f"👤 **New Students:** {new_student_count}")
                    with col2:
                        if linked_count > 0:
                            st.info(f"🔗 **Linked Existing:** {linked_count}")
                    with col3:
                        if skipped_count > 0:
                            st.warning(f"⚠️ **Skipped:** {skipped_count}")
                    
                    if errors:
                        st.error(f"❌ **Errors:** {len(errors)} files had issues:")
                        for error in errors:
                            st.write(error)
                    
                    # Show content diversity analysis
                    if len(content_hashes) > 1:
                        st.info(f"📈 **Content Diversity:** Found {len(content_hashes)} unique submissions")
                    elif len(content_hashes) == 1:
                        st.warning("⚠️ **Content Warning:** All submissions appear to be identical")
                    
                    # Database summary
                    st.info(f"📚 **Total Students in Database:** {total_students}")
                    
            except Exception as e:
                st.error(f"❌ Error processing batch upload: {str(e)}")
                import traceback
                st.error(f"Details: {traceback.format_exc()}")

def extract_student_info_from_notebook(nb):
    """Extract student information from notebook - same logic as detailed_analyzer"""
    import re
    
    student_info = {
        'name': 'Unknown',
        'id': 'Unknown'
    }
    
    # Look for student info in first few cells
    for i, cell in enumerate(nb.cells[:5]):
        if cell.cell_type == 'markdown':
            content = cell.source
            
            # Look for name patterns
            name_patterns = [
                r'\*\*Student Name:\*\*\s*\[?([^\]\n]+)\]?',
                r'Student Name:\s*\[?([^\]\n]+)\]?',
                r'\*\*Name:\*\*\s*\[?([^\]\n]+)\]?',
                r'Name:\s*\[?([^\]\n]+)\]?',
                r'student[:\s]+([^\n\]]+)',
                r'name[:\s]+([^\n\]]+)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if name.lower() not in ['your name here', 'name', 'student name', '[your name here]', 'unknown']:
                        student_info['name'] = name
                        break
            
            # Look for ID patterns
            id_patterns = [
                r'\*\*Student ID:\*\*\s*\[?([^\]\n]+)\]?',
                r'Student ID:\s*\[?([^\]\n]+)\]?',
                r'ID:\s*\[?([^\]\n]+)\]?',
            ]
            
            for pattern in id_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    student_id = match.group(1).strip()
                    if student_id.lower() not in ['your id here', 'id', 'student id', '[your id here]', 'unknown']:
                        student_info['id'] = student_id
                        break
    
    return student_info

def parse_github_classroom_filename(filename):
    """Parse Canvas/GitHub Classroom filename to extract student name and Canvas user ID
    
    Canvas filename formats:
    - guadarramafrancisco_178108_11544892_Guadarrama_Francisco_homework_lesson_2
    - 152822_aguirrejulissa_11544283_homework_lesson_1
    
    CRITICAL: The FIRST part before the first underscore is the Canvas ID (primary identifier)
    """
    import re
    
    try:
        # Split by underscores
        parts = filename.split('_')
        
        if len(parts) >= 3:
            # CRITICAL: First part is ALWAYS the Canvas ID (username or numeric)
            # This is the primary identifier for matching students
            canvas_id = parts[0]
            
            # Try to extract a readable name from later parts
            # Look for capitalized name parts (e.g., "Guadarrama_Francisco")
            name_parts = []
            for part in parts[1:]:
                # Stop at common keywords
                if part.lower() in ['homework', 'lesson', 'assignment', 'late']:
                    break
                # Skip numeric IDs
                if part.isdigit():
                    continue
                # Add capitalized parts that look like names
                if part and part[0].isupper():
                    name_parts.append(part)
            
            # If we found name parts, use them; otherwise use canvas_id
            if name_parts:
                student_name = ' '.join(name_parts)
            else:
                # Convert canvas_id to readable name (e.g., "guadarramafrancisco" -> "Guadarrama Francisco")
                student_name = canvas_id.replace('_', ' ').title()
            
            return {
                'id': canvas_id,  # Primary identifier
                'name': student_name
            }
            
            # Handle Canvas LATE submissions
            if 'LATE' in parts:
                late_index = parts.index('LATE')
                # Canvas user ID should still be first, even with LATE marker
                if parts[0].isdigit():
                    student_id = parts[0]  # Canvas user ID is first
                    # Username might be after LATE or before it
                    if late_index > 1:
                        username = parts[1]  # Username before LATE
                    elif late_index + 1 < len(parts):
                        username = parts[late_index + 1]  # Username after LATE
                else:
                    # Fallback for complex LATE formats
                    numeric_ids = [part for part in parts if part.isdigit() and len(part) > 3]
                    student_id = numeric_ids[0] if numeric_ids else 'LATE'
            
            # Check if there are explicit name parts later in the filename
            name_parts = []
            for i, part in enumerate(parts[3:], 3):  # Skip username, id, submission_id
                if (part.isalpha() and 
                    len(part) > 2 and 
                    part not in ['homework', 'lesson', 'LATE', 'assignment', 'ipynb'] and
                    not part.isdigit()):
                    # Check if it looks like a name (has some capitals or is reasonable length)
                    if any(c.isupper() for c in part) or len(part) > 3:
                        name_parts.append(part.title())
            
            # If we found explicit name parts, use those
            if len(name_parts) >= 2:
                parsed_name = ' '.join(name_parts[:2])  # Take first two name parts
                return {'name': parsed_name, 'id': student_id}
            elif len(name_parts) == 1:
                return {'name': name_parts[0], 'id': student_id}
            
            # For Canvas LATE submissions, construct name from parts before LATE marker
            if 'LATE' in parts:
                late_index = parts.index('LATE')
                # Use parts before LATE as name components
                name_components = [part for part in parts[:late_index] if part.isalpha()]
                if len(name_components) >= 2:
                    parsed_name = ' '.join(name_components).title()
                elif len(name_components) == 1:
                    parsed_name = name_components[0].title()
                else:
                    parsed_name = parse_username_to_name(username)
            else:
                # Otherwise, try to parse the username (lastnamefirstname format)
                parsed_name = parse_username_to_name(username)
            
            return {'name': parsed_name, 'id': student_id}
        
        # Fallback for simpler formats
        return {'name': filename.replace('_', ' ').title(), 'id': 'unknown'}
        
    except Exception:
        return {'name': None, 'id': None}

def parse_username_to_name(username):
    """Parse username like 'aguirrejulissa' to 'Julissa Aguirre'"""
    import re
    
    try:
        # Common lastname endings that help identify the split point
        common_endings = ['ez', 'son', 'sen', 'man', 'er', 'el', 'al', 'os', 'is', 'on', 'an']
        
        # Try to find a split point based on common lastname endings
        for i in range(4, len(username)-2):
            prefix = username[:i]
            suffix = username[i:]
            
            # Check if prefix ends with common lastname ending
            if any(prefix.lower().endswith(ending) for ending in common_endings):
                return f"{suffix.title()} {prefix.title()}"
        
        # Try to find split based on capital letters (if any)
        capitals = [i for i, c in enumerate(username) if c.isupper()]
        if len(capitals) >= 2:
            split_point = capitals[1]
            return f"{username[split_point:].title()} {username[:split_point].title()}"
        
        # Try common split patterns for typical name lengths
        if len(username) >= 8:
            # Try different split points and pick the most reasonable
            possible_splits = []
            
            for split in range(3, len(username)-2):
                first_part = username[:split]
                second_part = username[split:]
                
                # Prefer splits where both parts are reasonable name lengths
                if 3 <= len(first_part) <= 10 and 3 <= len(second_part) <= 10:
                    possible_splits.append((split, first_part, second_part))
            
            if possible_splits:
                # Pick the split closest to the middle
                mid_point = len(username) // 2
                best_split = min(possible_splits, key=lambda x: abs(x[0] - mid_point))
                return f"{best_split[2].title()} {best_split[1].title()}"
        
        # Final fallback: just capitalize the username
        return username.title()
        
    except Exception:
        return username.title() if username else 'Unknown'

def hash_notebook_content(nb):
    """Create a hash of notebook content to detect duplicates"""
    import hashlib
    
    # Extract meaningful content (code + markdown)
    content_parts = []
    
    for cell in nb.cells:
        if cell.cell_type in ['code', 'markdown']:
            # Clean up the content
            content = cell.source.strip()
            if content and not content.startswith('[YOUR NAME HERE]'):
                content_parts.append(content)
    
    # Create hash of combined content
    combined_content = '\\n'.join(content_parts)
    return hashlib.md5(combined_content.encode()).hexdigest()[:8]