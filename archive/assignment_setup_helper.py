import streamlit as st
import json

class AssignmentSetupHelper:
    """Helper for setting up assignments with proper language detection and rubrics"""
    
    @staticmethod
    def suggest_rubric_template(assignment_name, language_type):
        """Suggest rubric template based on assignment type and language"""
        
        assignment_lower = assignment_name.lower()
        
        if language_type == "R":
            return AssignmentSetupHelper._get_r_rubric_template(assignment_lower)
        elif language_type == "SQL":
            return AssignmentSetupHelper._get_sql_rubric_template(assignment_lower)
        else:
            return AssignmentSetupHelper._get_generic_rubric_template()
    
    @staticmethod
    def _get_r_rubric_template(assignment_name):
        """Generate R-specific rubric template"""
        
        base_rubric = {
            "data_import": {
                "points": 15,
                "description": "Correctly imports and loads required datasets"
            },
            "data_manipulation": {
                "points": 25,
                "description": "Properly manipulates data using appropriate R functions"
            },
            "code_quality": {
                "points": 15,
                "description": "Clean, well-commented, and efficient R code"
            },
            "results_accuracy": {
                "points": 25,
                "description": "Produces correct results and outputs"
            },
            "reflection": {
                "points": 20,
                "description": "Thoughtful analysis and interpretation of results"
            }
        }
        
        # Customize based on assignment type
        if "visualization" in assignment_name or "plot" in assignment_name:
            base_rubric["visualization"] = {
                "points": 20,
                "description": "Creates appropriate and well-labeled visualizations"
            }
            # Reduce other categories to accommodate
            base_rubric["data_manipulation"]["points"] = 20
            base_rubric["reflection"]["points"] = 15
        
        elif "statistical" in assignment_name or "analysis" in assignment_name:
            base_rubric["statistical_methods"] = {
                "points": 20,
                "description": "Correctly applies statistical methods and interprets results"
            }
            base_rubric["data_manipulation"]["points"] = 20
            base_rubric["reflection"]["points"] = 15
        
        elif "tidyverse" in assignment_name or "dplyr" in assignment_name:
            base_rubric["tidyverse_usage"] = {
                "points": 15,
                "description": "Effective use of tidyverse functions and pipe operators"
            }
            base_rubric["data_manipulation"]["points"] = 20
        
        return base_rubric
    
    @staticmethod
    def _get_sql_rubric_template(assignment_name):
        """Generate SQL-specific rubric template"""
        
        base_rubric = {
            "query_syntax": {
                "points": 25,
                "description": "Correct SQL syntax and query structure"
            },
            "query_logic": {
                "points": 25,
                "description": "Logical approach to solving the problem"
            },
            "results_accuracy": {
                "points": 25,
                "description": "Query produces correct and complete results"
            },
            "code_quality": {
                "points": 15,
                "description": "Well-formatted, commented, and efficient queries"
            },
            "reflection": {
                "points": 10,
                "description": "Understanding of query logic and results"
            }
        }
        
        # Customize based on assignment type
        if "join" in assignment_name:
            base_rubric["join_usage"] = {
                "points": 20,
                "description": "Correct use of JOIN operations and table relationships"
            }
            base_rubric["query_logic"]["points"] = 20
            base_rubric["reflection"]["points"] = 5
        
        elif "aggregate" in assignment_name or "group" in assignment_name:
            base_rubric["aggregation"] = {
                "points": 20,
                "description": "Proper use of aggregate functions and GROUP BY"
            }
            base_rubric["query_logic"]["points"] = 20
            base_rubric["reflection"]["points"] = 5
        
        elif "subquery" in assignment_name or "advanced" in assignment_name:
            base_rubric["query_complexity"] = {
                "points": 15,
                "description": "Handles complex query requirements effectively"
            }
            base_rubric["query_logic"]["points"] = 20
        
        return base_rubric
    
    @staticmethod
    def _get_generic_rubric_template():
        """Generic rubric for mixed or unknown assignment types"""
        return {
            "problem_understanding": {
                "points": 20,
                "description": "Demonstrates clear understanding of the problem"
            },
            "technical_execution": {
                "points": 30,
                "description": "Correctly implements technical solution"
            },
            "code_quality": {
                "points": 20,
                "description": "Clean, well-organized, and documented code"
            },
            "results_accuracy": {
                "points": 20,
                "description": "Produces accurate and complete results"
            },
            "reflection": {
                "points": 10,
                "description": "Thoughtful analysis and interpretation"
            }
        }
    
    @staticmethod
    def show_assignment_setup_wizard():
        """Interactive wizard for setting up new assignments"""
        st.subheader("🧙‍♂️ Assignment Setup Wizard")
        
        with st.form("assignment_wizard"):
            col1, col2 = st.columns(2)
            
            with col1:
                assignment_name = st.text_input("Assignment Name", 
                    placeholder="e.g., R Assignment 1 - Data Import")
                
                language_type = st.selectbox("Primary Language", 
                    ["R", "SQL", "Python", "Mixed", "Other"])
                
                assignment_type = st.selectbox("Assignment Type", [
                    "Basic Skills", "Data Analysis", "Visualization", 
                    "Statistical Analysis", "Database Queries", "Advanced Topics"
                ])
            
            with col2:
                total_points = st.number_input("Total Points", 
                    min_value=50, max_value=200, value=100, step=5)
                
                difficulty_level = st.selectbox("Difficulty Level", 
                    ["Beginner", "Intermediate", "Advanced"])
                
                estimated_time = st.selectbox("Estimated Time", 
                    ["1-2 hours", "2-4 hours", "4-6 hours", "6+ hours"])
            
            # Generate rubric button
            generate_rubric = st.form_submit_button("🎯 Generate Rubric Template")
            
            if generate_rubric and assignment_name:
                # Generate suggested rubric
                rubric_template = AssignmentSetupHelper.suggest_rubric_template(
                    assignment_name, language_type
                )
                
                # Adjust points to match total
                current_total = sum(item["points"] for item in rubric_template.values())
                scale_factor = total_points / current_total
                
                for criterion in rubric_template:
                    rubric_template[criterion]["points"] = round(
                        rubric_template[criterion]["points"] * scale_factor
                    )
                
                st.success("✅ Rubric template generated!")
                
                # Display the rubric
                st.subheader("Generated Rubric")
                
                # Allow editing
                edited_rubric = {}
                for criterion, details in rubric_template.items():
                    with st.expander(f"{criterion.replace('_', ' ').title()} ({details['points']} points)"):
                        points = st.number_input(f"Points for {criterion}", 
                            value=details['points'], min_value=0, max_value=50,
                            key=f"points_{criterion}")
                        
                        description = st.text_area(f"Description for {criterion}",
                            value=details['description'], key=f"desc_{criterion}")
                        
                        edited_rubric[criterion] = {
                            "points": points,
                            "description": description
                        }
                
                # Show JSON output
                st.subheader("Rubric JSON (Copy to Assignment)")
                st.code(json.dumps(edited_rubric, indent=2), language="json")
                
                # Training recommendations
                st.subheader("🎓 Training Recommendations")
                
                if language_type in ["R", "SQL"]:
                    st.info(f"""
                    **For {language_type} assignments:**
                    - Use language-specific model training
                    - Focus corrections on {language_type}-specific patterns
                    - Train after collecting 15+ {language_type} submissions
                    """)
                
                if difficulty_level == "Advanced":
                    st.warning("""
                    **Advanced assignment detected:**
                    - Consider assignment-specific model training
                    - Provide detailed corrections for unique concepts
                    - May need 20+ corrections for good accuracy
                    """)
                
                return edited_rubric
        
        return None
    
    @staticmethod
    def show_course_planning_helper():
        """Helper for planning the entire course training strategy"""
        st.subheader("📅 Course Training Planner")
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_assignments = st.number_input("Total Assignments", 
                min_value=1, max_value=50, value=18)
            
            r_assignments = st.number_input("R Assignments", 
                min_value=0, max_value=total_assignments, value=9)
            
            sql_assignments = st.number_input("SQL Assignments", 
                min_value=0, max_value=total_assignments, value=9)
        
        with col2:
            course_weeks = st.number_input("Course Duration (weeks)", 
                min_value=8, max_value=20, value=16)
            
            students_per_section = st.number_input("Students per Section", 
                min_value=10, max_value=200, value=30)
        
        if st.button("📊 Generate Training Plan"):
            # Calculate training timeline
            assignments_per_week = total_assignments / course_weeks
            total_submissions = total_assignments * students_per_section
            
            st.subheader("Training Timeline Recommendations")
            
            # Phase 1: Initial setup
            st.markdown("### Phase 1: Foundation (Weeks 1-3)")
            st.write(f"- Grade first {min(3, total_assignments)} assignments manually")
            st.write(f"- Collect ~{3 * students_per_section} training samples")
            st.write("- Focus on building initial dataset")
            
            # Phase 2: Language training
            if r_assignments > 0 and sql_assignments > 0:
                st.markdown("### Phase 2: Language-Specific Training (Weeks 4-6)")
                st.write(f"- Train R model after {min(3, r_assignments)} R assignments")
                st.write(f"- Train SQL model after {min(3, sql_assignments)} SQL assignments")
                st.write("- Make 15-20 corrections per language")
            
            # Phase 3: Optimization
            st.markdown("### Phase 3: Continuous Improvement (Weeks 7+)")
            st.write("- Weekly model updates with new corrections")
            st.write("- Focus on feedback quality and consistency")
            st.write("- Monitor performance analytics")
            
            # Expected outcomes
            st.subheader("Expected Time Savings")
            
            manual_time_per_assignment = 15  # minutes
            total_manual_time = total_submissions * manual_time_per_assignment / 60  # hours
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Without AI", f"{total_manual_time:.0f} hours", 
                         help="Total manual grading time")
            
            with col_b:
                ai_time_savings = total_manual_time * 0.6  # 60% savings after training
                st.metric("With Trained AI", f"{total_manual_time - ai_time_savings:.0f} hours", 
                         f"-{ai_time_savings:.0f} hours saved")
            
            with col_c:
                st.metric("Time Savings", f"{ai_time_savings/total_manual_time*100:.0f}%", 
                         help="Percentage of time saved")
            
            return {
                'total_assignments': total_assignments,
                'r_assignments': r_assignments, 
                'sql_assignments': sql_assignments,
                'course_weeks': course_weeks,
                'students_per_section': students_per_section,
                'estimated_savings_hours': ai_time_savings
            }
        
        return None