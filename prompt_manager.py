#!/usr/bin/env python3
"""
Prompt Manager
Manages general and assignment-specific prompts, and generates rubrics using AI
"""

import streamlit as st
import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import requests

class PromptManager:
    """Manages prompts and rubrics for assignments"""
    
    def __init__(self):
        self.prompt_templates_dir = Path("prompt_templates")
        self.assignment_prompts_dir = Path("assignment_prompts")
        self.rubrics_dir = Path("rubrics")
        self.ollama_prompts_dir = Path("prompt_templates/ollama")
        
        # Create directories if they don't exist
        self.prompt_templates_dir.mkdir(exist_ok=True)
        self.assignment_prompts_dir.mkdir(exist_ok=True)
        self.rubrics_dir.mkdir(exist_ok=True)
        self.ollama_prompts_dir.mkdir(exist_ok=True)
    
    def load_general_prompt(self, prompt_type: str) -> str:
        """Load general prompt template"""
        prompt_file = self.prompt_templates_dir / f"general_{prompt_type}_prompt.txt"
        
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()
        else:
            return ""
    
    def save_general_prompt(self, prompt_type: str, content: str):
        """Save general prompt template"""
        prompt_file = self.prompt_templates_dir / f"general_{prompt_type}_prompt.txt"
        
        with open(prompt_file, 'w') as f:
            f.write(content)
    
    def load_assignment_prompt(self, assignment_name: str, prompt_type: str) -> Optional[str]:
        """Load assignment-specific prompt"""
        prompt_file = self.assignment_prompts_dir / f"{assignment_name}_{prompt_type}_prompt.txt"
        
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()
        else:
            return None
    
    def save_assignment_prompt(self, assignment_name: str, prompt_type: str, content: str):
        """Save assignment-specific prompt"""
        prompt_file = self.assignment_prompts_dir / f"{assignment_name}_{prompt_type}_prompt.txt"
        
        with open(prompt_file, 'w') as f:
            f.write(content)
    
    def get_ollama_prompt(self, prompt_type: str, validation_results: Dict = None, **kwargs) -> str:
        """Get Ollama-optimized prompt with validation context"""
        # Load Ollama-specific prompt
        prompt_file = self.ollama_prompts_dir / f"{prompt_type}_prompt.txt"
        
        if not prompt_file.exists():
            # Fallback to general prompt
            return self.get_combined_prompt(kwargs.get('assignment_name', 'Unknown'), prompt_type, **kwargs)
        
        with open(prompt_file, 'r') as f:
            prompt_template = f.read()
        
        # Build validation context string
        if validation_results:
            sys_result = validation_results.get('systematic_results', {})
            output_result = validation_results.get('output_results', {})
            
            var_check = sys_result.get('variable_check', {})
            found_vars = var_check.get('found', 0)
            total_vars = var_check.get('total_required', 0)
            
            output_match = output_result.get('overall_match', 0) * 100 if output_result else 0
            passed_checks = output_result.get('passed_checks', 0) if output_result else 0
            total_checks = output_result.get('total_checks', 0) if output_result else 0
            
            validation_context = f"""
Variables Found: {found_vars}/{total_vars} required variables present
Output Accuracy: {output_match:.0f}% ({passed_checks}/{total_checks} checks passed)
Base Score: {validation_results.get('base_score', 0):.0f}%
Adjusted Score: {validation_results.get('adjusted_score', 0):.0f}%

This means the student HAS completed work. Focus on quality and approach, not completion.
"""
            
            # Add reflection comparison if available
            if validation_results.get('reflection_comparison'):
                validation_context += f"\n{validation_results['reflection_comparison']}"
        else:
            validation_context = "No validation results available."
        
        kwargs['validation_context'] = validation_context
        
        # Format the prompt
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            print(f"⚠️ Missing variable in Ollama prompt: {e}")
            # Return with partial formatting
            for key, value in kwargs.items():
                prompt_template = prompt_template.replace(f"{{{key}}}", str(value))
            return prompt_template
    
    def get_combined_prompt(self, assignment_name: str, prompt_type: str, **kwargs) -> str:
        """Get combined prompt (general + assignment-specific + correction learning)"""
        # Load general prompt
        general_prompt = self.load_general_prompt(prompt_type)
        
        # Load assignment-specific instructions (if exists)
        assignment_specific = self.load_assignment_prompt(assignment_name, prompt_type)
        
        if assignment_specific:
            kwargs['assignment_specific_instructions'] = f"\nASSIGNMENT-SPECIFIC INSTRUCTIONS:\n{assignment_specific}\n"
        else:
            kwargs['assignment_specific_instructions'] = ""
        
        # Add correction learning from previous assignments
        from correction_analyzer import CorrectionAnalyzer
        analyzer = CorrectionAnalyzer()
        
        # Get assignment_id if available
        assignment_id = kwargs.get('assignment_id')
        correction_summary = analyzer.get_correction_summary_for_prompt(assignment_id, limit=5)
        
        if correction_summary:
            kwargs['correction_learning'] = f"\n{correction_summary}\n"
        else:
            kwargs['correction_learning'] = ""
        
        # Format the prompt with provided variables
        try:
            return general_prompt.format(**kwargs)
        except KeyError as e:
            # If correction_learning or other new variables aren't in the template, that's ok
            if str(e) not in ["'correction_learning'"]:
                st.error(f"Missing required variable in prompt: {e}")
            return general_prompt
    
    def generate_rubric_with_ai(self, assignment_description: str, total_points: float, 
                                ollama_url: str = "http://localhost:11434") -> Dict:
        """Generate a rubric using AI based on assignment description"""
        
        prompt = f"""You are an expert in creating grading rubrics for business analytics assignments. 
Create a detailed JSON rubric for the following assignment.

ASSIGNMENT DESCRIPTION:
{assignment_description}

TOTAL POINTS: {total_points}

Create a rubric with these components:
1. Technical Skills (25% of points) - Code quality, syntax, execution
2. Business Understanding (30% of points) - Business context, practical application
3. Analysis & Interpretation (25% of points) - Data analysis, insights, conclusions
4. Communication (20% of points) - Clarity, organization, presentation

For each component, provide:
- Point allocation
- Excellent criteria (90-100%)
- Good criteria (80-89%)
- Satisfactory criteria (70-79%)
- Needs Improvement criteria (<70%)

OUTPUT ONLY THIS JSON STRUCTURE:

{{
    "assignment_name": "Extract from description",
    "total_points": {total_points},
    "components": [
        {{
            "name": "Technical Skills",
            "points": <25% of total>,
            "criteria": {{
                "excellent": "Specific criteria for excellent work",
                "good": "Specific criteria for good work",
                "satisfactory": "Specific criteria for satisfactory work",
                "needs_improvement": "Specific criteria for work needing improvement"
            }}
        }},
        {{
            "name": "Business Understanding",
            "points": <30% of total>,
            "criteria": {{
                "excellent": "Specific criteria",
                "good": "Specific criteria",
                "satisfactory": "Specific criteria",
                "needs_improvement": "Specific criteria"
            }}
        }},
        {{
            "name": "Analysis & Interpretation",
            "points": <25% of total>,
            "criteria": {{
                "excellent": "Specific criteria",
                "good": "Specific criteria",
                "satisfactory": "Specific criteria",
                "needs_improvement": "Specific criteria"
            }}
        }},
        {{
            "name": "Communication",
            "points": <20% of total>,
            "criteria": {{
                "excellent": "Specific criteria",
                "good": "Specific criteria",
                "satisfactory": "Specific criteria",
                "needs_improvement": "Specific criteria"
            }}
        }}
    ],
    "reflection_questions": [
        "Suggested reflection question 1",
        "Suggested reflection question 2",
        "Suggested reflection question 3"
    ]
}}

Output pure JSON only."""

        try:
            # Call Ollama API
            response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": "gemma3:27b-it-q8_0",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 2000
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Extract JSON from response
                if '{' in response_text and '}' in response_text:
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_text = response_text[start:end]
                    
                    rubric = json.loads(json_text)
                    return rubric
                else:
                    return {"error": "No JSON found in response"}
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def save_rubric(self, assignment_name: str, rubric: Dict):
        """Save rubric to file"""
        rubric_file = self.rubrics_dir / f"{assignment_name}_rubric.json"
        
        with open(rubric_file, 'w') as f:
            json.dump(rubric, f, indent=2)
    
    def load_rubric(self, assignment_name: str) -> Optional[Dict]:
        """Load rubric from file"""
        rubric_file = self.rubrics_dir / f"{assignment_name}_rubric.json"
        
        if rubric_file.exists():
            with open(rubric_file, 'r') as f:
                return json.load(f)
        else:
            return None


def render_prompt_manager_ui():
    """Render the prompt manager UI"""
    st.title("🎯 Prompt & Rubric Manager")
    st.markdown("Manage general prompts, assignment-specific instructions, and generate rubrics with AI")
    
    manager = PromptManager()
    
    tab1, tab2, tab3 = st.tabs(["📝 General Prompts", "🎓 Assignment Prompts", "📋 Rubric Generator"])
    
    with tab1:
        st.subheader("General Prompt Templates")
        st.markdown("These prompts are used for all assignments unless overridden by assignment-specific instructions.")
        
        prompt_type = st.selectbox(
            "Select Prompt Type",
            ["code_analysis", "feedback"],
            key="general_prompt_type"
        )
        
        current_prompt = manager.load_general_prompt(prompt_type)
        
        edited_prompt = st.text_area(
            f"Edit {prompt_type.replace('_', ' ').title()} Prompt",
            value=current_prompt,
            height=400,
            help="Use {variable_name} for placeholders like {assignment_title}, {student_code}, etc."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save General Prompt", use_container_width=True):
                manager.save_general_prompt(prompt_type, edited_prompt)
                st.success(f"Saved {prompt_type} prompt!")
        
        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                st.warning("This will reset the prompt to default. Refresh to see changes.")
    
    with tab2:
        st.subheader("Assignment-Specific Instructions")
        st.markdown("Add optional assignment-specific instructions that will be appended to the general prompt.")
        
        # Get list of assignments
        import sqlite3
        conn = sqlite3.connect("grading_database.db")
        assignments = pd.read_sql_query("SELECT name FROM assignments ORDER BY name", conn)
        conn.close()
        
        if len(assignments) > 0:
            assignment_name = st.selectbox(
                "Select Assignment",
                assignments['name'].tolist(),
                key="assignment_select"
            )
            
            prompt_type_assign = st.selectbox(
                "Select Prompt Type",
                ["code_analysis", "feedback"],
                key="assignment_prompt_type"
            )
            
            current_assignment_prompt = manager.load_assignment_prompt(assignment_name, prompt_type_assign)
            
            edited_assignment_prompt = st.text_area(
                f"Assignment-Specific Instructions for {assignment_name}",
                value=current_assignment_prompt or "",
                height=300,
                help="These instructions will be added to the general prompt for this assignment only."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Assignment Instructions", use_container_width=True):
                    manager.save_assignment_prompt(assignment_name, prompt_type_assign, edited_assignment_prompt)
                    st.success(f"Saved instructions for {assignment_name}!")
            
            with col2:
                if st.button("🗑️ Clear Instructions", use_container_width=True):
                    manager.save_assignment_prompt(assignment_name, prompt_type_assign, "")
                    st.success("Cleared instructions!")
                    st.rerun()
            
            # Preview combined prompt
            with st.expander("👁️ Preview Combined Prompt"):
                combined = manager.get_combined_prompt(
                    assignment_name,
                    prompt_type_assign,
                    assignment_title=assignment_name,
                    student_code="[Student code will be inserted here]",
                    solution_code="[Solution code will be inserted here]",
                    student_markdown="[Student markdown will be inserted here]",
                    student_code_summary="[Code summary will be inserted here]"
                )
                st.code(combined, language="text")
        else:
            st.info("No assignments found. Create an assignment first.")
    
    with tab3:
        st.subheader("AI-Powered Rubric Generator")
        st.markdown("Generate a detailed rubric using AI based on your assignment description.")
        
        assignment_desc = st.text_area(
            "Assignment Description",
            height=200,
            placeholder="Describe the assignment objectives, required tasks, learning outcomes, etc.",
            help="Provide a detailed description of what students need to do"
        )
        
        total_points = st.number_input(
            "Total Points",
            min_value=1.0,
            max_value=1000.0,
            value=37.5,
            step=0.5
        )
        
        rubric_assignment_name = st.text_input(
            "Assignment Name (for saving)",
            placeholder="e.g., assignment_2"
        )
        
        if st.button("🤖 Generate Rubric with AI", use_container_width=True):
            if assignment_desc and rubric_assignment_name:
                with st.spinner("Generating rubric with AI..."):
                    rubric = manager.generate_rubric_with_ai(assignment_desc, total_points)
                    
                    if "error" in rubric:
                        st.error(f"Error generating rubric: {rubric['error']}")
                    else:
                        st.success("Rubric generated successfully!")
                        
                        # Display rubric
                        st.json(rubric)
                        
                        # Save button
                        if st.button("💾 Save This Rubric"):
                            manager.save_rubric(rubric_assignment_name, rubric)
                            st.success(f"Rubric saved as {rubric_assignment_name}_rubric.json")
            else:
                st.warning("Please provide both assignment description and name")
        
        # Load existing rubric
        st.markdown("---")
        st.markdown("### Load Existing Rubric")
        
        rubric_files = list(manager.rubrics_dir.glob("*_rubric.json"))
        if rubric_files:
            rubric_names = [f.stem.replace("_rubric", "") for f in rubric_files]
            selected_rubric = st.selectbox("Select Rubric to View", rubric_names)
            
            if st.button("📖 Load Rubric"):
                rubric = manager.load_rubric(selected_rubric)
                if rubric:
                    st.json(rubric)
        else:
            st.info("No rubrics found. Generate one above!")


if __name__ == "__main__":
    import pandas as pd
    st.set_page_config(page_title="Prompt Manager", page_icon="🎯", layout="wide")
    render_prompt_manager_ui()
