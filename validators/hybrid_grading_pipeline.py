#!/usr/bin/env python3
"""
Hybrid Grading Pipeline
Combines deterministic validation with AI-powered feedback

Pipeline:
1. Systematic Validator → Objective scores (Python regex/checks)
2. Qwen Coder → Code evaluation and fix recommendations
3. GPT-OSS-120B → Narrative feedback and insights
"""

import json
import requests
from typing import Dict, List, Any, Tuple
from pathlib import Path
from validators.assignment_6_systematic_validator import Assignment6SystematicValidator
from validators.smart_output_validator import SmartOutputValidator


class HybridGradingPipeline:
    """
    Combines systematic validation with AI models for comprehensive grading
    """
    
    def __init__(
        self,
        solution_notebook_path: str = "data/raw/homework_lesson_6_joins_SOLUTION.ipynb",
        rubric_path: str = "rubrics/assignment_6_rubric.json",
        use_distributed_mlx: bool = True
    ):
        self.systematic_validator = Assignment6SystematicValidator(rubric_path)
        self.output_validator = None
        
        # Initialize output validator if solution exists
        if Path(solution_notebook_path).exists() and Path(rubric_path).exists():
            self.output_validator = SmartOutputValidator(solution_notebook_path, rubric_path)
        
        # Use distributed MLX client instead of Ollama
        self.use_distributed_mlx = use_distributed_mlx
        if use_distributed_mlx:
            import sys
            sys.path.append('models')
            from distributed_mlx_client import DistributedMLXClient
            
            # Load config
            import json
            with open('distributed_config.json', 'r') as f:
                config = json.load(f)
            
            self.mlx_client = DistributedMLXClient(
                qwen_server_url=config['urls']['qwen_server'],
                gemma_server_url=config['urls']['gemma_server']
            )
            print("✅ Using Distributed MLX (Mac Studio 1 + 2)")
        else:
            self.mlx_client = None
            print("⚠️ MLX client not initialized")
    
    def grade_submission(self, notebook_path: str) -> Dict[str, Any]:
        """
        Complete grading pipeline
        
        Returns:
            {
                'objective_score': 91.0,
                'adjusted_score': 89.0,  # After output validation
                'grade': 'B',
                'validation_details': {...},
                'output_validation': {...},  # NEW: Output comparison
                'code_evaluation': {...},  # From Qwen
                'narrative_feedback': {...}  # From GPT-OSS
            }
        """
        print(f"\n{'='*80}")
        print(f"HYBRID GRADING PIPELINE")
        print(f"{'='*80}")
        print(f"Notebook: {notebook_path}\n")
        
        # STEP 1: Systematic Validation (Deterministic)
        print("Step 1/4: Running systematic validation...")
        validation_result = self.systematic_validator.validate_notebook(notebook_path)
        
        print(f"  ✅ Objective Score: {validation_result['final_score']:.1f}/100")
        print(f"  ✅ Variables Found: {validation_result['variable_check']['found']}/25")
        print(f"  ✅ Sections Complete: {sum(1 for s in validation_result['section_breakdown'].values() if s['status'] == 'complete')}/21")
        
        # STEP 1.5: Output Validation (Compare with solution)
        output_validation = None
        adjusted_score = validation_result['final_score']
        
        if self.output_validator:
            print("\nStep 1.5/4: Validating outputs against solution...")
            output_validation = self.output_validator.validate_student_outputs(notebook_path)
            
            print(f"  ✅ Output Match: {output_validation['overall_match']*100:.1f}%")
            print(f"  ✅ Checks Passed: {output_validation['passed_checks']}/{output_validation['total_checks']}")
            print(f"  ✅ Score Adjustment: {output_validation['score_adjustment']} points")
            
            # Apply adjustment
            adjusted_score = max(0, validation_result['final_score'] + output_validation['score_adjustment'])
        else:
            print("\nStep 1.5/4: Skipping output validation (no solution notebook)")
        
        # STEP 2 & 3: AI Analysis (Parallel if using MLX)
        if self.mlx_client:
            print("\nStep 2-3/4: Running parallel AI analysis (Qwen + GPT-OSS)...")
            code_evaluation, narrative_feedback = self._run_parallel_ai_analysis(
                notebook_path, validation_result, output_validation
            )
            print(f"  ✅ Code analysis complete (Qwen on Mac Studio 2)")
            print(f"  ✅ Feedback generated (GPT-OSS on Mac Studio 1)")
        else:
            print("\nStep 2/4: Skipping AI analysis (MLX not available)")
            code_evaluation = {'raw_response': 'AI analysis not available'}
            narrative_feedback = {'raw_response': 'AI feedback not available'}
        
        # Recalculate grade with adjusted score
        final_grade = self._get_grade(adjusted_score)
        
        # Combine results
        final_result = {
            'objective_score': validation_result['final_score'],
            'adjusted_score': adjusted_score,
            'grade': final_grade,
            'validation_details': validation_result,
            'output_validation': output_validation,
            'code_evaluation': code_evaluation,
            'narrative_feedback': narrative_feedback,
            'timestamp': str(Path(notebook_path).stat().st_mtime)
        }
        
        print(f"\n{'='*80}")
        print(f"FINAL GRADE: {final_result['grade']} ({final_result['adjusted_score']:.1f}%)")
        if output_validation:
            print(f"  (Base: {validation_result['final_score']:.1f}, Adjustment: {output_validation['score_adjustment']})")
        print(f"{'='*80}\n")
        
        return final_result
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _qwen_evaluate_code(self, notebook_path: str, validation_result: Dict, output_validation: Dict = None) -> Dict:
        """
        Use Qwen Coder to evaluate code quality and suggest fixes
        """
        # Load notebook
        with open(notebook_path, 'r') as f:
            notebook = json.load(f)
        
        # Extract code cells
        code_cells = []
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                code_cells.append(''.join(cell['source']))
        
        all_code = '\n\n'.join(code_cells)
        
        # Identify issues from validation
        issues = self._extract_issues(validation_result)
        
        # Build prompt for Qwen
        prompt = self._build_qwen_prompt(all_code, issues, validation_result)
        
        # Call Qwen
        qwen_response = self._call_llm(
            endpoint=self.qwen_endpoint,
            model=self.qwen_model,
            prompt=prompt,
            temperature=0.3  # Lower for code evaluation
        )
        
        return {
            'raw_response': qwen_response,
            'issues_analyzed': len(issues),
            'recommendations': self._parse_qwen_recommendations(qwen_response)
        }
    
    def _gpt_generate_feedback(
        self,
        notebook_path: str,
        validation_result: Dict,
        code_evaluation: Dict,
        output_validation: Dict = None
    ) -> Dict:
        """
        Use GPT-OSS-120B to generate narrative feedback
        """
        # Build prompt for GPT-OSS
        prompt = self._build_gpt_prompt(validation_result, code_evaluation)
        
        # Call GPT-OSS
        gpt_response = self._call_llm(
            endpoint=self.gpt_endpoint,
            model=self.gpt_model,
            prompt=prompt,
            temperature=0.7  # Higher for creative feedback
        )
        
        return {
            'raw_response': gpt_response,
            'sections': self._parse_gpt_feedback(gpt_response)
        }
    
    def _extract_issues(self, validation_result: Dict) -> List[Dict]:
        """Extract issues from validation result"""
        issues = []
        
        # Unexecuted cells
        if validation_result['cell_stats']['cells_without_output'] > 0:
            issues.append({
                'type': 'unexecuted_cells',
                'severity': 'medium',
                'count': validation_result['cell_stats']['cells_without_output'],
                'details': validation_result['cell_stats']['unexecuted_cells']
            })
        
        # Missing variables
        if validation_result['variable_check']['missing']:
            issues.append({
                'type': 'missing_variables',
                'severity': 'high',
                'variables': validation_result['variable_check']['missing']
            })
        
        # Incomplete sections
        incomplete_sections = [
            s for s in validation_result['section_breakdown'].values()
            if s['status'] != 'complete'
        ]
        if incomplete_sections:
            issues.append({
                'type': 'incomplete_sections',
                'severity': 'high',
                'sections': incomplete_sections
            })
        
        return issues
    
    def _build_qwen_prompt(self, code: str, issues: List[Dict], validation_result: Dict, output_validation: Dict = None) -> str:
        """Build prompt for Qwen Coder - focused on output analysis"""
        
        # Build output discrepancies section
        output_section = ""
        if output_validation and output_validation.get('discrepancies'):
            output_section = "\nOUTPUT DISCREPANCIES:\n"
            for disc in output_validation['discrepancies']:
                output_section += f"\nVariable: {disc['variable']}\n"
                output_section += f"  Issue: {disc['issue']}\n"
                output_section += f"  Student Output: {disc['student_value']}\n"
                output_section += f"  Expected Output: {disc['solution_value']}\n"
        
        prompt = f"""You are an expert R programming instructor analyzing student code for a data joins assignment.

OBJECTIVE VALIDATION:
- Variables Found: {validation_result['variable_check']['found']}/25
- Sections Complete: {sum(1 for s in validation_result['section_breakdown'].values() if s['status'] == 'complete')}/21
- Base Score: {validation_result['final_score']:.1f}/100

{output_section}

STUDENT CODE (relevant sections):
```r
{code[:5000]}
```

YOUR TASK AS CODE ANALYZER:
1. **Analyze Output Discrepancies**: For each output mismatch, identify the root cause in the code
2. **Explain Why**: What in the code logic causes the wrong output?
3. **Provide Fixes**: Give specific code corrections with examples
4. **Assess Code Quality**: Comment on style, efficiency, best practices

Format your response as:

## Output Analysis
[For each discrepancy, explain what in the code causes it]

## Root Causes
### Discrepancy 1: [Variable Name]
**Code Issue:** [What in the code is wrong]
**Why This Happens:** [Explain the logic error]
**Fix:**
```r
# Corrected code
[specific fix]
```

### Discrepancy 2: ...

## Code Quality Notes
[Overall code quality, style, efficiency]

## Recommendations
[Specific suggestions to improve the code]

Be specific and technical. Focus on helping the student understand WHY their outputs don't match.
"""
        return prompt
    
    def _build_gpt_prompt(self, validation_result: Dict, code_evaluation: Dict, output_validation: Dict = None) -> str:
        """Build prompt for GPT-OSS-120B - Feedback Coordinator"""
        
        score = validation_result['final_score']
        adjusted_score = score
        if output_validation:
            adjusted_score = score + output_validation.get('score_adjustment', 0)
        
        grade = self._get_grade(adjusted_score)
        
        # Build output validation summary
        output_summary = ""
        if output_validation:
            match_pct = output_validation['overall_match'] * 100
            output_summary = f"""
OUTPUT VALIDATION:
- Output Match: {match_pct:.1f}%
- Checks Passed: {output_validation['passed_checks']}/{output_validation['total_checks']}
- Score Adjustment: {output_validation['score_adjustment']} points
- Discrepancies: {len(output_validation.get('discrepancies', []))}
"""
        
        prompt = f"""You are a supportive instructor coordinating feedback for a student's data analysis assignment.

You have received analysis from a technical code reviewer (Qwen Coder). Your job is to synthesize everything into clear, encouraging, educational feedback.

OBJECTIVE RESULTS:
- Base Score: {score:.1f}/100
- Adjusted Score: {adjusted_score:.1f}/100
- Final Grade: {grade}
- Variables Found: {validation_result['variable_check']['found']}/25
- Sections Complete: {sum(1 for s in validation_result['section_breakdown'].values() if s['status'] == 'complete')}/21
{output_summary}

TECHNICAL ANALYSIS FROM CODE REVIEWER:
{code_evaluation['raw_response'][:2000]}

YOUR TASK AS FEEDBACK COORDINATOR:
1. **Synthesize**: Combine objective scores + technical analysis into coherent feedback
2. **Clarify**: Translate technical issues into student-friendly language
3. **Encourage**: Maintain positive, growth-oriented tone
4. **Guide**: Provide clear, actionable next steps
5. **Educate**: Connect issues to learning objectives

Format your response as:

## Overall Assessment
[2-3 sentences: What did they do well? What needs work? Overall impression]

## What You Did Well
[Celebrate specific strengths - be concrete]

## Areas for Improvement
[Explain issues in clear, supportive language]
[For output discrepancies: "Your code produced X but expected Y because..."]

## How to Fix It
[Step-by-step guidance based on technical analysis]
[Make it actionable and specific]

## Next Steps
[What should they do next? Practice? Review? Revise?]

## Encouragement
[Warm, motivating closing that acknowledges effort and progress]

TONE GUIDELINES:
- Be warm and supportive, not harsh
- Focus on learning, not just grades
- Acknowledge effort and progress
- Frame mistakes as learning opportunities
- Be specific with praise and guidance
- End on an encouraging note

Remember: You're helping them learn, not just grading them.
"""
        return prompt
    
    def _run_parallel_ai_analysis(
        self,
        notebook_path: str,
        validation_result: Dict,
        output_validation: Dict = None
    ) -> Tuple[Dict, Dict]:
        """Run Qwen and GPT-OSS in parallel using distributed MLX"""
        
        # Load notebook
        with open(notebook_path, 'r') as f:
            notebook = json.load(f)
        
        # Extract code
        code_cells = []
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                code_cells.append(''.join(cell['source']))
        all_code = '\n\n'.join(code_cells[:20])  # First 20 cells
        
        # Extract issues
        issues = self._extract_issues(validation_result)
        
        # Build prompts
        qwen_prompt = self._build_qwen_prompt(all_code, issues, validation_result, output_validation)
        gpt_prompt = self._build_gpt_prompt(validation_result, {'raw_response': 'Analyzing...'}, output_validation)
        
        # Run in parallel
        print("  🚀 Sending requests to both Mac Studios...")
        result = self.mlx_client.generate_parallel_sync(qwen_prompt, gpt_prompt)
        
        code_evaluation = {
            'raw_response': result.get('code_analysis', 'No response'),
            'recommendations': []
        }
        
        narrative_feedback = {
            'raw_response': result.get('feedback', 'No response'),
            'sections': {}
        }
        
        # Update GPT prompt with actual Qwen results
        if result.get('code_analysis'):
            gpt_prompt_final = self._build_gpt_prompt(validation_result, code_evaluation, output_validation)
            print("  🔄 Refining feedback with Qwen analysis...")
            final_feedback = self.mlx_client.generate_feedback(gpt_prompt_final, max_tokens=1500)
            if final_feedback:
                narrative_feedback['raw_response'] = final_feedback
        
        return code_evaluation, narrative_feedback
    
    def _parse_qwen_recommendations(self, response: str) -> List[Dict]:
        """Parse Qwen's recommendations into structured format"""
        # Simple parsing - you can make this more sophisticated
        recommendations = []
        
        lines = response.split('\n')
        current_rec = None
        
        for line in lines:
            if line.startswith('### Issue'):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {'title': line, 'content': []}
            elif current_rec:
                current_rec['content'].append(line)
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations
    
    def _parse_gpt_feedback(self, response: str) -> Dict:
        """Parse GPT-OSS feedback into sections"""
        sections = {
            'overall': '',
            'strengths': '',
            'areas_for_growth': '',
            'recommendations': '',
            'encouragement': ''
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            if '## Overall Assessment' in line:
                current_section = 'overall'
            elif '## Strengths' in line:
                current_section = 'strengths'
            elif '## Areas for Growth' in line:
                current_section = 'areas_for_growth'
            elif '## Recommendations' in line:
                current_section = 'recommendations'
            elif '## Encouragement' in line:
                current_section = 'encouragement'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'
        
        return sections
    
    def generate_comprehensive_report(self, result: Dict, output_path: str):
        """Generate a comprehensive report combining all results"""
        
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE GRADING REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Objective Score
        report.append(f"FINAL GRADE: {result['grade']} ({result['objective_score']:.1f}/100)")
        report.append("")
        
        # Component Breakdown
        report.append("=" * 80)
        report.append("OBJECTIVE SCORING (Systematic Validator)")
        report.append("=" * 80)
        report.append("")
        
        validation = result['validation_details']
        for comp_name, comp_data in validation['components'].items():
            report.append(f"{comp_name.upper().replace('_', ' ')}: {comp_data['score']:.1f}/{comp_data['max']}")
        
        report.append("")
        report.append(f"Variables Found: {validation['variable_check']['found']}/25")
        report.append(f"Sections Complete: {sum(1 for s in validation['section_breakdown'].values() if s['status'] == 'complete')}/21")
        report.append(f"Execution Rate: {validation['cell_stats']['execution_rate']*100:.1f}%")
        report.append("")
        
        # Code Evaluation (Qwen)
        report.append("=" * 80)
        report.append("CODE EVALUATION (Qwen Coder)")
        report.append("=" * 80)
        report.append("")
        report.append(result['code_evaluation']['raw_response'])
        report.append("")
        
        # Narrative Feedback (GPT-OSS)
        report.append("=" * 80)
        report.append("INSTRUCTOR FEEDBACK (GPT-OSS-120B)")
        report.append("=" * 80)
        report.append("")
        report.append(result['narrative_feedback']['raw_response'])
        report.append("")
        
        # Save report
        report_text = '\n'.join(report)
        with open(output_path, 'w') as f:
            f.write(report_text)
        
        print(f"✅ Comprehensive report saved to: {output_path}")
        
        return report_text


def grade_with_hybrid_pipeline(
    notebook_path: str,
    output_dir: str = "grading_results_hybrid",
    qwen_endpoint: str = "http://localhost:11434/api/generate",
    gpt_endpoint: str = "http://localhost:11434/api/generate"
):
    """
    Grade a submission using the hybrid pipeline
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Initialize pipeline
    pipeline = HybridGradingPipeline(
        qwen_endpoint=qwen_endpoint,
        gpt_endpoint=gpt_endpoint
    )
    
    # Grade submission
    result = pipeline.grade_submission(notebook_path)
    
    # Generate comprehensive report
    student_name = Path(notebook_path).stem
    report_path = output_path / f"{student_name}_comprehensive_report.txt"
    pipeline.generate_comprehensive_report(result, str(report_path))
    
    # Save JSON result
    json_path = output_path / f"{student_name}_result.json"
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"✅ JSON result saved to: {json_path}")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid grading pipeline")
    parser.add_argument("--file", required=True, help="Notebook to grade")
    parser.add_argument("--output", default="grading_results_hybrid", help="Output directory")
    parser.add_argument("--qwen-endpoint", default="http://localhost:11434/api/generate", help="Qwen endpoint")
    parser.add_argument("--gpt-endpoint", default="http://localhost:11434/api/generate", help="GPT-OSS endpoint")
    
    args = parser.parse_args()
    
    result = grade_with_hybrid_pipeline(
        notebook_path=args.file,
        output_dir=args.output,
        qwen_endpoint=args.qwen_endpoint,
        gpt_endpoint=args.gpt_endpoint
    )
    
    print("\n" + "=" * 80)
    print("GRADING COMPLETE")
    print("=" * 80)
    print(f"Final Grade: {result['grade']} ({result['objective_score']:.1f}%)")
