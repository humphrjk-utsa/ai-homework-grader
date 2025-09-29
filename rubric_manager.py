import json
import sqlite3
import streamlit as st
from pathlib import Path

class RubricManager:
    """Utility class for managing assignment rubrics"""
    
    def __init__(self, grader):
        self.grader = grader
    
    def load_rubric_from_file(self, file_path):
        """Load rubric from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rubric_data = json.load(f)
            return rubric_data, None
        except FileNotFoundError:
            return None, f"Rubric file not found: {file_path}"
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON in rubric file: {str(e)}"
        except Exception as e:
            return None, f"Error loading rubric file: {str(e)}"
    
    def get_assignment_rubric(self, assignment_id):
        """Get rubric for a specific assignment from database"""
        try:
            conn = sqlite3.connect(self.grader.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT rubric FROM assignments WHERE id = ?", (assignment_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return json.loads(result[0]), None
            return {}, "No rubric found for this assignment"
        except Exception as e:
            return {}, f"Error loading rubric: {str(e)}"
    
    def update_assignment_rubric(self, assignment_id, rubric_data):
        """Update rubric for a specific assignment"""
        try:
            conn = sqlite3.connect(self.grader.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE assignments SET rubric = ? WHERE id = ?", 
                (json.dumps(rubric_data), assignment_id)
            )
            conn.commit()
            conn.close()
            return True, "Rubric updated successfully"
        except Exception as e:
            return False, f"Error updating rubric: {str(e)}"
    
    def validate_rubric_structure(self, rubric_data):
        """Validate that rubric has required structure"""
        errors = []
        
        if not isinstance(rubric_data, dict):
            errors.append("Rubric must be a JSON object")
            return errors
        
        # Check for required sections
        if "assignment_info" not in rubric_data:
            errors.append("Missing 'assignment_info' section")
        else:
            info = rubric_data["assignment_info"]
            if "total_points" not in info:
                errors.append("Missing 'total_points' in assignment_info")
            if "title" not in info:
                errors.append("Missing 'title' in assignment_info")
        
        if "rubric_elements" not in rubric_data:
            errors.append("Missing 'rubric_elements' section")
        else:
            elements = rubric_data["rubric_elements"]
            if not isinstance(elements, dict):
                errors.append("'rubric_elements' must be an object")
            else:
                total_points = 0
                for element_name, element_data in elements.items():
                    if not isinstance(element_data, dict):
                        errors.append(f"Element '{element_name}' must be an object")
                        continue
                    
                    if "max_points" not in element_data:
                        errors.append(f"Element '{element_name}' missing 'max_points'")
                    else:
                        try:
                            points = float(element_data["max_points"])
                            total_points += points
                        except (ValueError, TypeError):
                            errors.append(f"Element '{element_name}' has invalid 'max_points'")
                    
                    if "description" not in element_data:
                        errors.append(f"Element '{element_name}' missing 'description'")
                
                # Check if total points match
                if "assignment_info" in rubric_data and "total_points" in rubric_data["assignment_info"]:
                    expected_total = rubric_data["assignment_info"]["total_points"]
                    if abs(total_points - expected_total) > 0.1:
                        errors.append(f"Total points mismatch: elements sum to {total_points}, but assignment_info says {expected_total}")
        
        return errors
    
    def get_rubric_summary(self, rubric_data):
        """Get a summary of rubric for display"""
        if not rubric_data:
            return "No rubric data"
        
        try:
            info = rubric_data.get("assignment_info", {})
            elements = rubric_data.get("rubric_elements", {})
            
            summary = {
                "title": info.get("title", "Unknown Assignment"),
                "total_points": info.get("total_points", 0),
                "element_count": len(elements),
                "elements": []
            }
            
            for name, data in elements.items():
                summary["elements"].append({
                    "name": name,
                    "points": data.get("max_points", 0),
                    "description": data.get("description", "No description")
                })
            
            return summary
        except Exception as e:
            return f"Error parsing rubric: {str(e)}"
    
    def create_default_rubric(self, assignment_name, total_points=37.5):
        """Create a default rubric structure"""
        return {
            "assignment_info": {
                "title": assignment_name,
                "total_points": total_points,
                "learning_objectives": [
                    "Complete assignment requirements",
                    "Demonstrate understanding of concepts",
                    "Write clean, executable code"
                ]
            },
            "grading_strategy": {
                "automated_testing": total_points * 0.6,
                "manual_review": total_points * 0.4
            },
            "rubric_elements": {
                "code_execution": {
                    "max_points": total_points * 0.3,
                    "weight": total_points * 0.3,
                    "category": "automated",
                    "description": "Code executes without errors and produces expected output",
                    "criteria": {
                        "excellent": {
                            "points": f"{total_points * 0.27}-{total_points * 0.3}",
                            "description": "All code executes perfectly with correct output"
                        },
                        "good": {
                            "points": f"{total_points * 0.21}-{total_points * 0.26}",
                            "description": "Most code executes with minor issues"
                        },
                        "satisfactory": {
                            "points": f"{total_points * 0.15}-{total_points * 0.2}",
                            "description": "Some code executes but with significant issues"
                        },
                        "needs_improvement": {
                            "points": f"0-{total_points * 0.14}",
                            "description": "Code fails to execute or produces incorrect output"
                        }
                    }
                },
                "requirements_completion": {
                    "max_points": total_points * 0.3,
                    "weight": total_points * 0.3,
                    "category": "automated",
                    "description": "All assignment requirements completed correctly",
                    "criteria": {
                        "excellent": {
                            "points": f"{total_points * 0.27}-{total_points * 0.3}",
                            "description": "All requirements completed thoroughly"
                        },
                        "good": {
                            "points": f"{total_points * 0.21}-{total_points * 0.26}",
                            "description": "Most requirements completed with minor gaps"
                        },
                        "satisfactory": {
                            "points": f"{total_points * 0.15}-{total_points * 0.2}",
                            "description": "Some requirements completed"
                        },
                        "needs_improvement": {
                            "points": f"0-{total_points * 0.14}",
                            "description": "Few or no requirements completed"
                        }
                    }
                },
                "analysis_quality": {
                    "max_points": total_points * 0.4,
                    "weight": total_points * 0.4,
                    "category": "manual",
                    "description": "Quality of analysis, reasoning, and written responses",
                    "criteria": {
                        "excellent": {
                            "points": f"{total_points * 0.36}-{total_points * 0.4}",
                            "description": "Excellent analysis with clear reasoning and insights"
                        },
                        "good": {
                            "points": f"{total_points * 0.28}-{total_points * 0.35}",
                            "description": "Good analysis with some insights"
                        },
                        "satisfactory": {
                            "points": f"{total_points * 0.2}-{total_points * 0.27}",
                            "description": "Basic analysis with limited insights"
                        },
                        "needs_improvement": {
                            "points": f"0-{total_points * 0.19}",
                            "description": "Poor or missing analysis"
                        }
                    }
                }
            },
            "submission_requirements": {
                "file_format": "Jupyter notebook (.ipynb)",
                "naming_convention": "LastName_FirstName_assignment_name.ipynb",
                "required_elements": [
                    "All code cells executed with visible output",
                    "Written responses completed",
                    "Student name filled in header"
                ]
            },
            "grade_scale": {
                "A": f"{total_points * 0.9}-{total_points} points (90-100%)",
                "B": f"{total_points * 0.8}-{total_points * 0.89} points (80-89%)",
                "C": f"{total_points * 0.7}-{total_points * 0.79} points (70-79%)",
                "D": f"{total_points * 0.6}-{total_points * 0.69} points (60-69%)",
                "F": f"Below {total_points * 0.6} points (Below 60%)"
            }
        }

def load_predefined_rubrics():
    """Load any predefined rubric files from the rubrics directory"""
    rubrics_dir = Path("homework_grader/rubrics")
    predefined_rubrics = {}
    
    if rubrics_dir.exists():
        for rubric_file in rubrics_dir.glob("*.json"):
            try:
                with open(rubric_file, 'r', encoding='utf-8') as f:
                    rubric_data = json.load(f)
                # Use a more friendly name
                friendly_name = rubric_file.stem.replace("assignment_", "Assignment ").replace("_rubric", "")
                predefined_rubrics[friendly_name] = rubric_data
            except Exception as e:
                st.warning(f"Could not load rubric {rubric_file.name}: {str(e)}")
    
    return predefined_rubrics