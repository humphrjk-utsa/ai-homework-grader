"""
Tableau Assignment Grader
Integrates with existing AI grading system to evaluate Tableau workbooks
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

from homework_grader.tableau_parser import TableauWorkbookParser


class TableauGrader:
    """Grade Tableau assignments using workbook analysis and AI feedback"""
    
    def __init__(self, assignment_config: Dict):
        """
        Initialize grader with assignment configuration
        
        Args:
            assignment_config: Dict containing:
                - required_worksheets: List of required worksheet names
                - required_dashboards: List of required dashboard names
                - required_calculations: List of required calculated field names
                - min_worksheets: Minimum number of worksheets
                - min_dashboards: Minimum number of dashboards
                - points_breakdown: Dict of point allocations
        """
        self.config = assignment_config
        self.parser = None
        self.analysis = None
        
    def load_workbook(self, twbx_path: str) -> bool:
        """Load and parse a Tableau workbook"""
        try:
            self.parser = TableauWorkbookParser(twbx_path)
            self.analysis = self.parser.analyze_workbook()
            
            if 'error' in self.analysis:
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading workbook: {e}")
            return False
    
    def check_required_components(self) -> Dict:
        """Check if all required components are present"""
        results = {
            'worksheets': {'required': [], 'missing': [], 'extra': []},
            'dashboards': {'required': [], 'missing': [], 'extra': []},
            'calculations': {'required': [], 'missing': [], 'extra': []},
            'passed': True
        }
        
        # Check worksheets
        if 'required_worksheets' in self.config:
            student_worksheets = [ws['name'] for ws in self.analysis['worksheets']]
            required = self.config['required_worksheets']
            
            for req in required:
                if req in student_worksheets:
                    results['worksheets']['required'].append(req)
                else:
                    results['worksheets']['missing'].append(req)
                    results['passed'] = False
            
            results['worksheets']['extra'] = [ws for ws in student_worksheets if ws not in required]
        
        # Check dashboards
        if 'required_dashboards' in self.config:
            student_dashboards = [db['name'] for db in self.analysis['dashboards']]
            required = self.config['required_dashboards']
            
            for req in required:
                if req in student_dashboards:
                    results['dashboards']['required'].append(req)
                else:
                    results['dashboards']['missing'].append(req)
                    results['passed'] = False
            
            results['dashboards']['extra'] = [db for db in student_dashboards if db not in required]
        
        # Check calculated fields
        if 'required_calculations' in self.config:
            student_calcs = [calc['name'] for calc in self.analysis['calculated_fields']]
            required = self.config['required_calculations']
            
            for req in required:
                if req in student_calcs:
                    results['calculations']['required'].append(req)
                else:
                    results['calculations']['missing'].append(req)
                    results['passed'] = False
            
            results['calculations']['extra'] = [calc for calc in student_calcs if calc not in required]
        
        return results
    
    def check_minimum_requirements(self) -> Dict:
        """Check if minimum component counts are met"""
        results = {
            'worksheets': {'required': 0, 'actual': 0, 'passed': True},
            'dashboards': {'required': 0, 'actual': 0, 'passed': True},
            'passed': True
        }
        
        # Check minimum worksheets
        if 'min_worksheets' in self.config:
            required = self.config['min_worksheets']
            actual = self.analysis['summary']['total_worksheets']
            results['worksheets'] = {
                'required': required,
                'actual': actual,
                'passed': actual >= required
            }
            if not results['worksheets']['passed']:
                results['passed'] = False
        
        # Check minimum dashboards
        if 'min_dashboards' in self.config:
            required = self.config['min_dashboards']
            actual = self.analysis['summary']['total_dashboards']
            results['dashboards'] = {
                'required': required,
                'actual': actual,
                'passed': actual >= required
            }
            if not results['dashboards']['passed']:
                results['passed'] = False
        
        return results
    
    def validate_calculated_fields(self) -> List[Dict]:
        """Validate calculated field formulas"""
        validations = []
        
        for calc in self.analysis['calculated_fields']:
            validation = {
                'name': calc['name'],
                'formula': calc['formula'],
                'issues': []
            }
            
            # Check for common issues
            formula = calc['formula']
            
            # Check for division by zero protection
            if '/' in formula and 'IF' not in formula.upper() and 'ZN' not in formula.upper():
                validation['issues'].append('Missing division by zero protection')
            
            # Check for proper aggregation
            if any(agg in formula.upper() for agg in ['SUM', 'AVG', 'COUNT', 'MIN', 'MAX']):
                validation['has_aggregation'] = True
            else:
                validation['has_aggregation'] = False
            
            validations.append(validation)
        
        return validations
    
    def calculate_technical_score(self) -> Tuple[float, Dict]:
        """Calculate technical score based on workbook structure"""
        max_points = self.config.get('technical_points', 37.5)
        breakdown = self.config.get('points_breakdown', {})
        
        score = 0
        details = {}
        
        # Check required components
        component_check = self.check_required_components()
        component_points = breakdown.get('required_components', 15)
        
        if component_check['passed']:
            score += component_points
            details['required_components'] = f"✅ All required components present (+{component_points})"
        else:
            missing = []
            if component_check['worksheets']['missing']:
                missing.append(f"Worksheets: {', '.join(component_check['worksheets']['missing'])}")
            if component_check['dashboards']['missing']:
                missing.append(f"Dashboards: {', '.join(component_check['dashboards']['missing'])}")
            if component_check['calculations']['missing']:
                missing.append(f"Calculations: {', '.join(component_check['calculations']['missing'])}")
            
            details['required_components'] = f"❌ Missing components: {'; '.join(missing)} (0/{component_points})"
        
        # Check minimum requirements
        min_check = self.check_minimum_requirements()
        min_points = breakdown.get('minimum_requirements', 10)
        
        if min_check['passed']:
            score += min_points
            details['minimum_requirements'] = f"✅ Minimum requirements met (+{min_points})"
        else:
            issues = []
            if not min_check['worksheets']['passed']:
                issues.append(f"Worksheets: {min_check['worksheets']['actual']}/{min_check['worksheets']['required']}")
            if not min_check['dashboards']['passed']:
                issues.append(f"Dashboards: {min_check['dashboards']['actual']}/{min_check['dashboards']['required']}")
            
            details['minimum_requirements'] = f"❌ Below minimum: {'; '.join(issues)} (0/{min_points})"
        
        # Validate calculated fields
        calc_validations = self.validate_calculated_fields()
        calc_points = breakdown.get('calculated_fields', 12.5)
        
        if calc_validations:
            issues_found = sum(1 for v in calc_validations if v['issues'])
            calc_score = calc_points * (1 - (issues_found / len(calc_validations)))
            score += calc_score
            
            if issues_found == 0:
                details['calculated_fields'] = f"✅ All calculations valid (+{calc_points})"
            else:
                details['calculated_fields'] = f"⚠️ {issues_found} calculation issues (+{calc_score:.1f}/{calc_points})"
        else:
            details['calculated_fields'] = f"❌ No calculated fields found (0/{calc_points})"
        
        return score, details
    
    def generate_feedback_prompt(self) -> str:
        """Generate prompt for AI feedback generation"""
        prompt = f"""You are an expert Tableau instructor grading a student's dashboard assignment.

ASSIGNMENT: {self.config.get('assignment_name', 'Tableau Dashboard')}

STUDENT WORKBOOK ANALYSIS:
{json.dumps(self.analysis, indent=2)}

REQUIRED COMPONENTS:
{json.dumps(self.config, indent=2)}

TECHNICAL VALIDATION:
{json.dumps(self.check_required_components(), indent=2)}

Please provide constructive feedback on:
1. Dashboard design and layout
2. Appropriate use of visualizations
3. Calculated field implementation
4. Data storytelling effectiveness
5. Professional presentation quality

Focus on what the student did well and specific areas for improvement.
Be encouraging and pedagogical in your tone.
"""
        return prompt
    
    def grade_workbook(self, twbx_path: str) -> Dict:
        """Complete grading workflow for a Tableau workbook"""
        if not self.load_workbook(twbx_path):
            return {
                'error': 'Failed to load workbook',
                'score': 0,
                'feedback': 'Unable to parse workbook file'
            }
        
        # Calculate technical score
        technical_score, technical_details = self.calculate_technical_score()
        
        # Generate AI feedback prompt
        feedback_prompt = self.generate_feedback_prompt()
        
        result = {
            'filename': Path(twbx_path).name,
            'timestamp': datetime.now().isoformat(),
            'technical_score': technical_score,
            'max_technical_points': self.config.get('technical_points', 37.5),
            'technical_details': technical_details,
            'workbook_analysis': self.analysis,
            'component_check': self.check_required_components(),
            'minimum_check': self.check_minimum_requirements(),
            'calculated_field_validations': self.validate_calculated_fields(),
            'ai_feedback_prompt': feedback_prompt,
            'ready_for_ai_grading': True
        }
        
        return result


# Example assignment configuration
EXAMPLE_ASSIGNMENT_CONFIG = {
    'assignment_name': 'Executive Sales Dashboard',
    'required_worksheets': ['Sales by Region', 'Profit Trend', 'Top Products'],
    'required_dashboards': ['Executive Dashboard'],
    'required_calculations': ['Profit Margin', 'YoY Growth'],
    'min_worksheets': 3,
    'min_dashboards': 1,
    'technical_points': 37.5,
    'points_breakdown': {
        'required_components': 15,
        'minimum_requirements': 10,
        'calculated_fields': 12.5
    }
}


def test_grader():
    """Test the grader with sample workbook"""
    # Simplified config for testing
    config = {
        'assignment_name': 'Sales Dashboard Assignment',
        'min_worksheets': 3,
        'min_dashboards': 1,
        'technical_points': 37.5,
        'points_breakdown': {
            'required_components': 15,
            'minimum_requirements': 10,
            'calculated_fields': 12.5
        }
    }
    
    grader = TableauGrader(config)
    result = grader.grade_workbook("data/processed/Book1Executive Sales Performance Dashboard.twbx")
    
    print("\n" + "="*60)
    print("📊 TABLEAU GRADING RESULT")
    print("="*60)
    print(f"\nFile: {result['filename']}")
    print(f"Technical Score: {result['technical_score']:.1f}/{result['max_technical_points']}")
    print(f"\n📋 TECHNICAL DETAILS:")
    for key, detail in result['technical_details'].items():
        print(f"  {detail}")
    
    print(f"\n✅ Ready for AI grading: {result['ready_for_ai_grading']}")
    print("="*60)
    
    # Save result
    output_path = Path("data/processed/tableau_grading_result.json")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Full result saved to: {output_path}")


if __name__ == "__main__":
    test_grader()
