"""
Tableau Assignment Manager
Create and manage Tableau assignment configurations with solution files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from homework_grader.tableau_parser import TableauWorkbookParser


class TableauAssignmentManager:
    """Manage Tableau assignment configurations and solution files"""
    
    def __init__(self, assignments_dir: str = "assignments/tableau"):
        self.assignments_dir = Path(assignments_dir)
        self.assignments_dir.mkdir(parents=True, exist_ok=True)
        
    def create_assignment(
        self,
        assignment_name: str,
        solution_twbx_path: str,
        requirements: Dict,
        rubric: Dict,
        description: str = ""
    ) -> Dict:
        """
        Create a new Tableau assignment configuration
        
        Args:
            assignment_name: Name of the assignment
            solution_twbx_path: Path to instructor's solution TWBX
            requirements: Dict of required components
            rubric: Grading rubric
            description: Assignment description
            
        Returns:
            Assignment configuration dict
        """
        # Parse solution workbook
        parser = TableauWorkbookParser(solution_twbx_path)
        solution_analysis = parser.analyze_workbook()
        
        if 'error' in solution_analysis:
            raise ValueError(f"Failed to parse solution: {solution_analysis['error']}")
        
        # Create assignment directory
        assignment_id = assignment_name.lower().replace(' ', '_')
        assignment_dir = self.assignments_dir / assignment_id
        assignment_dir.mkdir(exist_ok=True)
        
        # Copy solution file
        solution_dest = assignment_dir / "solution.twbx"
        import shutil
        shutil.copy2(solution_twbx_path, solution_dest)
        
        # Create configuration
        config = {
            'assignment_id': assignment_id,
            'assignment_name': assignment_name,
            'assignment_type': 'tableau',
            'description': description,
            'created_at': datetime.now().isoformat(),
            
            # Paths
            'solution_path': str(solution_dest),
            'config_path': str(assignment_dir / 'config.json'),
            
            # Solution analysis
            'solution_analysis': solution_analysis,
            
            # Requirements
            'requirements': requirements,
            
            # Rubric
            'rubric': rubric,
            
            # Grading settings
            'grading_settings': {
                'use_qwen': True,
                'use_gpt_oss': True,
                'parallel_grading': True,
                'technical_points': rubric.get('total_points', 37.5)
            }
        }
        
        # Save configuration
        config_path = assignment_dir / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Created assignment: {assignment_name}")
        print(f"   Location: {assignment_dir}")
        print(f"   Solution worksheets: {len(solution_analysis['worksheets'])}")
        print(f"   Solution dashboards: {len(solution_analysis['dashboards'])}")
        print(f"   Solution calculations: {len(solution_analysis['calculated_fields'])}")
        
        return config
    
    def load_assignment(self, assignment_id: str) -> Optional[Dict]:
        """Load an existing assignment configuration"""
        config_path = self.assignments_dir / assignment_id / 'config.json'
        
        if not config_path.exists():
            print(f"❌ Assignment not found: {assignment_id}")
            return None
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config
    
    def list_assignments(self) -> List[Dict]:
        """List all Tableau assignments"""
        assignments = []
        
        for assignment_dir in self.assignments_dir.iterdir():
            if assignment_dir.is_dir():
                config_path = assignment_dir / 'config.json'
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    assignments.append({
                        'id': config['assignment_id'],
                        'name': config['assignment_name'],
                        'created': config['created_at'],
                        'worksheets': len(config['solution_analysis']['worksheets']),
                        'dashboards': len(config['solution_analysis']['dashboards'])
                    })
        
        return assignments
    
    def update_requirements(self, assignment_id: str, requirements: Dict) -> bool:
        """Update assignment requirements"""
        config = self.load_assignment(assignment_id)
        if not config:
            return False
        
        config['requirements'] = requirements
        config['updated_at'] = datetime.now().isoformat()
        
        config_path = self.assignments_dir / assignment_id / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated requirements for: {config['assignment_name']}")
        return True
    
    def update_rubric(self, assignment_id: str, rubric: Dict) -> bool:
        """Update assignment rubric"""
        config = self.load_assignment(assignment_id)
        if not config:
            return False
        
        config['rubric'] = rubric
        config['updated_at'] = datetime.now().isoformat()
        
        config_path = self.assignments_dir / assignment_id / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated rubric for: {config['assignment_name']}")
        return True
    
    def generate_requirements_from_solution(self, solution_analysis: Dict) -> Dict:
        """Auto-generate requirements based on solution workbook"""
        requirements = {
            'required_worksheets': [ws['name'] for ws in solution_analysis['worksheets']],
            'required_dashboards': [db['name'] for db in solution_analysis['dashboards']],
            'required_calculations': [calc['name'] for calc in solution_analysis['calculated_fields']],
            'min_worksheets': len(solution_analysis['worksheets']),
            'min_dashboards': len(solution_analysis['dashboards']),
            'min_calculated_fields': len(solution_analysis['calculated_fields'])
        }
        return requirements
    
    def generate_default_rubric(self, requirements: Dict) -> Dict:
        """Generate a default rubric based on requirements"""
        rubric = {
            'total_points': 37.5,
            'categories': {
                'required_components': {
                    'points': 15,
                    'description': 'All required worksheets, dashboards, and calculations present',
                    'criteria': [
                        f"Required worksheets: {', '.join(requirements.get('required_worksheets', []))}",
                        f"Required dashboards: {', '.join(requirements.get('required_dashboards', []))}",
                        f"Required calculations: {', '.join(requirements.get('required_calculations', []))}"
                    ]
                },
                'technical_implementation': {
                    'points': 12.5,
                    'description': 'Calculated fields are correct and well-implemented',
                    'criteria': [
                        'Formulas are syntactically correct',
                        'Appropriate aggregations used',
                        'Division by zero protection where needed',
                        'Logic matches requirements'
                    ]
                },
                'dashboard_design': {
                    'points': 10,
                    'description': 'Dashboard is well-organized and effective',
                    'criteria': [
                        'Appropriate chart types for data',
                        'Logical layout and organization',
                        'Effective use of filters',
                        'Professional presentation'
                    ]
                }
            }
        }
        return rubric


def create_example_assignment():
    """Example: Create a sample Tableau assignment"""
    manager = TableauAssignmentManager()
    
    # Define requirements (can be auto-generated or custom)
    requirements = {
        'required_worksheets': ['Sales by Region', 'Profit Trend', 'Top Products'],
        'required_dashboards': ['Executive Dashboard'],
        'required_calculations': ['Profit Margin', 'YoY Growth'],
        'min_worksheets': 3,
        'min_dashboards': 1,
        'min_calculated_fields': 2,
        'flexible_matching': True  # Allow similar names
    }
    
    # Define rubric
    rubric = {
        'total_points': 37.5,
        'categories': {
            'required_components': {
                'points': 15,
                'description': 'All required components present'
            },
            'calculated_fields': {
                'points': 12.5,
                'description': 'Calculations are correct and well-implemented'
            },
            'dashboard_design': {
                'points': 10,
                'description': 'Dashboard is effective and professional'
            }
        }
    }
    
    # Create assignment
    config = manager.create_assignment(
        assignment_name="Executive Sales Dashboard",
        solution_twbx_path="data/processed/Book1Executive Sales Performance Dashboard.twbx",
        requirements=requirements,
        rubric=rubric,
        description="Create an executive dashboard showing sales performance metrics"
    )
    
    return config


if __name__ == "__main__":
    # Test the manager
    config = create_example_assignment()
    print("\n" + "="*60)
    print("📋 ASSIGNMENT CREATED")
    print("="*60)
    print(json.dumps(config, indent=2))
