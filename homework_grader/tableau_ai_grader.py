"""
Tableau AI Grader
Integrates with Qwen and GPT-OSS servers for comprehensive Tableau grading
"""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import requests
from datetime import datetime

from homework_grader.tableau_parser import TableauWorkbookParser
from homework_grader.tableau_grader import TableauGrader


class TableauAIGrader:
    """Grade Tableau workbooks using technical validation + dual AI analysis"""
    
    def __init__(
        self,
        qwen_url: str = "http://10.55.0.2:5002",
        gpt_oss_url: str = "http://10.55.0.1:5001"
    ):
        self.qwen_url = qwen_url
        self.gpt_oss_url = gpt_oss_url
        
    def generate_qwen_prompt(
        self,
        student_analysis: Dict,
        solution_analysis: Dict,
        requirements: Dict,
        rubric: Dict
    ) -> str:
        """Generate prompt for Qwen (technical analysis)"""
        
        prompt = f"""You are an expert Tableau instructor analyzing a student's workbook for technical correctness.

ASSIGNMENT REQUIREMENTS:
{json.dumps(requirements, indent=2)}

SOLUTION WORKBOOK (Correct Implementation):
Worksheets: {[ws['name'] for ws in solution_analysis['worksheets']]}
Dashboards: {[db['name'] for db in solution_analysis['dashboards']]}
Calculated Fields:
{json.dumps(solution_analysis['calculated_fields'], indent=2)}

STUDENT WORKBOOK:
Worksheets: {[ws['name'] for ws in student_analysis['worksheets']]}
Dashboards: {[db['name'] for db in student_analysis['dashboards']]}
Calculated Fields:
{json.dumps(student_analysis['calculated_fields'], indent=2)}

TECHNICAL EVALUATION CRITERIA:
1. Calculated Field Correctness
   - Are formulas syntactically correct?
   - Do they match the solution logic?
   - Are aggregations appropriate?
   - Is there division by zero protection?
   - Are there any logic errors?

2. Component Completeness
   - Are all required worksheets present?
   - Are all required dashboards present?
   - Are all required calculations present?

3. Technical Implementation Quality
   - Efficient formula design
   - Proper use of Tableau functions
   - Appropriate field types

GRADING RUBRIC:
{json.dumps(rubric, indent=2)}

Provide a technical assessment with:
1. Technical Score (0-{rubric['total_points']})
2. Specific issues found in calculations
3. What was done correctly
4. What needs improvement
5. Specific formula corrections if needed

Be precise and technical. Focus on correctness and implementation quality.

Format your response as:
TECHNICAL_SCORE: [score]
CALCULATION_ANALYSIS: [detailed analysis]
STRENGTHS: [what was done well]
IMPROVEMENTS: [specific areas to improve]
"""
        return prompt
    
    def generate_gpt_oss_prompt(
        self,
        student_analysis: Dict,
        solution_analysis: Dict,
        requirements: Dict,
        rubric: Dict,
        assignment_description: str
    ) -> str:
        """Generate prompt for GPT-OSS (pedagogical feedback)"""
        
        prompt = f"""You are a supportive Tableau instructor providing constructive feedback on a student's dashboard assignment.

ASSIGNMENT: {assignment_description}

LEARNING OBJECTIVES:
- Create effective data visualizations
- Build professional dashboards
- Use calculated fields appropriately
- Tell a story with data

SOLUTION WORKBOOK STRUCTURE:
Worksheets: {[ws['name'] for ws in solution_analysis['worksheets']]}
Dashboards: {[db['name'] for db in solution_analysis['dashboards']]}
Key Calculations: {[calc['name'] for calc in solution_analysis['calculated_fields']]}

STUDENT WORKBOOK STRUCTURE:
Worksheets: {[ws['name'] for ws in student_analysis['worksheets']]}
Dashboards: {[db['name'] for db in student_analysis['dashboards']]}
Calculations: {[calc['name'] for calc in student_analysis['calculated_fields']]}

Dashboard Composition:
{json.dumps(student_analysis['dashboards'], indent=2)}

GRADING RUBRIC:
{json.dumps(rubric, indent=2)}

Provide encouraging, pedagogical feedback on:

1. Dashboard Design & Organization
   - Is the dashboard well-organized?
   - Are appropriate visualizations used?
   - Does it tell a clear story?

2. Calculated Field Usage
   - Are calculations used appropriately?
   - Do they serve the analysis goals?
   - Are they named clearly?

3. Overall Effectiveness
   - Does the dashboard meet the assignment goals?
   - Is it professional and polished?
   - What business insights can be derived?

4. Areas for Growth
   - What could be improved?
   - What should the student focus on next?
   - Specific suggestions for enhancement

Be encouraging and specific. Focus on learning and improvement.
Acknowledge what was done well before suggesting improvements.

Format your response as:
OVERALL_SCORE: [score out of {rubric['total_points']}]
DASHBOARD_FEEDBACK: [feedback on design and organization]
STRENGTHS: [specific things done well]
AREAS_FOR_IMPROVEMENT: [constructive suggestions]
ENCOURAGEMENT: [positive closing remarks]
"""
        return prompt
    
    def call_qwen(self, prompt: str, timeout: int = 180) -> Optional[str]:
        """Call Qwen server for technical analysis"""
        try:
            response = requests.post(
                f"{self.qwen_url}/generate",
                json={"prompt": prompt, "max_tokens": 2000},
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"❌ Qwen error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Qwen timeout")
            return None
        except Exception as e:
            print(f"❌ Qwen error: {e}")
            return None
    
    def call_gpt_oss(self, prompt: str, timeout: int = 200) -> Optional[str]:
        """Call GPT-OSS server for pedagogical feedback"""
        try:
            response = requests.post(
                f"{self.gpt_oss_url}/generate",
                json={"prompt": prompt, "max_tokens": 2000},
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"❌ GPT-OSS error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ GPT-OSS timeout")
            return None
        except Exception as e:
            print(f"❌ GPT-OSS error: {e}")
            return None
    
    def grade_workbook(
        self,
        student_twbx_path: str,
        assignment_config: Dict,
        use_parallel: bool = True
    ) -> Dict:
        """
        Complete grading workflow with technical validation + dual AI
        
        Args:
            student_twbx_path: Path to student's TWBX file
            assignment_config: Assignment configuration from manager
            use_parallel: Use parallel AI processing
            
        Returns:
            Complete grading result
        """
        start_time = datetime.now()
        
        # Parse student workbook
        print("📊 Parsing student workbook...")
        student_parser = TableauWorkbookParser(student_twbx_path)
        student_analysis = student_parser.analyze_workbook()
        
        if 'error' in student_analysis:
            return {
                'error': 'Failed to parse student workbook',
                'details': student_analysis['error']
            }
        
        # Load solution analysis
        solution_analysis = assignment_config['solution_analysis']
        requirements = assignment_config['requirements']
        rubric = assignment_config['rubric']
        
        # Technical validation
        print("🔍 Running technical validation...")
        grader = TableauGrader(assignment_config)
        grader.analysis = student_analysis  # Set analysis directly
        
        technical_score, technical_details = grader.calculate_technical_score()
        component_check = grader.check_required_components()
        
        # Generate AI prompts
        print("🤖 Generating AI prompts...")
        qwen_prompt = self.generate_qwen_prompt(
            student_analysis, solution_analysis, requirements, rubric
        )
        gpt_oss_prompt = self.generate_gpt_oss_prompt(
            student_analysis, solution_analysis, requirements, rubric,
            assignment_config.get('description', '')
        )
        
        # AI Analysis
        qwen_response = None
        gpt_oss_response = None
        
        if use_parallel and assignment_config['grading_settings'].get('parallel_grading', True):
            print("⚡ Running parallel AI analysis...")
            with ThreadPoolExecutor(max_workers=2) as executor:
                qwen_future = executor.submit(self.call_qwen, qwen_prompt)
                gpt_oss_future = executor.submit(self.call_gpt_oss, gpt_oss_prompt)
                
                try:
                    qwen_response = qwen_future.result(timeout=180)
                    gpt_oss_response = gpt_oss_future.result(timeout=200)
                except TimeoutError:
                    print("⚠️ AI analysis timeout")
        else:
            print("🔄 Running sequential AI analysis...")
            if assignment_config['grading_settings'].get('use_qwen', True):
                qwen_response = self.call_qwen(qwen_prompt)
            if assignment_config['grading_settings'].get('use_gpt_oss', True):
                gpt_oss_response = self.call_gpt_oss(gpt_oss_prompt)
        
        # Calculate final score
        ai_scores = []
        if qwen_response:
            # Extract score from Qwen response
            qwen_score = self._extract_score(qwen_response, rubric['total_points'])
            if qwen_score is not None:
                ai_scores.append(qwen_score)
        
        if gpt_oss_response:
            # Extract score from GPT-OSS response
            gpt_oss_score = self._extract_score(gpt_oss_response, rubric['total_points'])
            if gpt_oss_score is not None:
                ai_scores.append(gpt_oss_score)
        
        # Final score: average of technical and AI scores
        final_score = technical_score
        if ai_scores:
            final_score = (technical_score + sum(ai_scores)) / (len(ai_scores) + 1)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            'student_file': Path(student_twbx_path).name,
            'assignment': assignment_config['assignment_name'],
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            
            # Scores
            'technical_score': technical_score,
            'qwen_score': self._extract_score(qwen_response, rubric['total_points']) if qwen_response else None,
            'gpt_oss_score': self._extract_score(gpt_oss_response, rubric['total_points']) if gpt_oss_response else None,
            'final_score': final_score,
            'max_points': rubric['total_points'],
            'percentage': (final_score / rubric['total_points']) * 100,
            
            # Analysis
            'student_analysis': student_analysis,
            'technical_details': technical_details,
            'component_check': component_check,
            
            # AI Feedback
            'qwen_feedback': qwen_response,
            'gpt_oss_feedback': gpt_oss_response,
            
            # Metadata
            'grading_method': 'parallel' if use_parallel else 'sequential',
            'ai_models_used': {
                'qwen': qwen_response is not None,
                'gpt_oss': gpt_oss_response is not None
            }
        }
        
        print(f"\n✅ Grading complete in {duration:.1f}s")
        print(f"   Final Score: {final_score:.1f}/{rubric['total_points']} ({result['percentage']:.1f}%)")
        
        return result
    
    def _extract_score(self, response: str, max_points: float) -> Optional[float]:
        """Extract numerical score from AI response"""
        if not response:
            return None
        
        # Look for patterns like "TECHNICAL_SCORE: 25" or "OVERALL_SCORE: 30"
        import re
        patterns = [
            r'(?:TECHNICAL_SCORE|OVERALL_SCORE):\s*(\d+\.?\d*)',
            r'Score:\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:out of|/)\s*' + str(max_points)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                return min(score, max_points)  # Cap at max
        
        return None


def test_ai_grader():
    """Test the AI grader with sample files"""
    from homework_grader.tableau_assignment_manager import TableauAssignmentManager
    
    # Load assignment
    manager = TableauAssignmentManager()
    config = manager.load_assignment('executive_sales_dashboard')
    
    if not config:
        print("❌ Assignment not found. Run tableau_assignment_manager.py first")
        return
    
    # Grade a submission
    grader = TableauAIGrader()
    result = grader.grade_workbook(
        "data/processed/Book1Executive Sales Performance Dashboard.twbx",
        config,
        use_parallel=True
    )
    
    # Save result
    output_path = Path("data/processed/tableau_ai_grading_result.json")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Result saved to: {output_path}")


if __name__ == "__main__":
    test_ai_grader()
