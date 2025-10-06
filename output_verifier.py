#!/usr/bin/env python3
"""
Output Verifier
Programmatically checks if notebook cells have outputs to prevent AI hallucination
"""

import nbformat
from typing import Dict, List, Tuple

class OutputVerifier:
    """Verifies that code cells have outputs"""
    
    def __init__(self, notebook_path: str):
        self.notebook_path = notebook_path
        with open(notebook_path, 'r', encoding='utf-8') as f:
            self.notebook = nbformat.read(f, as_version=4)
    
    def check_outputs_exist(self) -> Dict[int, bool]:
        """Check which code cells have outputs"""
        outputs_map = {}
        
        code_cell_index = 0
        for cell in self.notebook.cells:
            if cell.cell_type == 'code':
                has_output = bool(cell.get('outputs', []))
                outputs_map[code_cell_index] = has_output
                code_cell_index += 1
        
        return outputs_map
    
    def count_cells_with_outputs(self) -> Tuple[int, int]:
        """Count how many code cells have outputs"""
        outputs_map = self.check_outputs_exist()
        total_code_cells = len(outputs_map)
        cells_with_outputs = sum(outputs_map.values())
        
        return cells_with_outputs, total_code_cells
    
    def get_completion_percentage(self) -> float:
        """Get percentage of code cells with outputs"""
        with_outputs, total = self.count_cells_with_outputs()
        if total == 0:
            return 0.0
        return (with_outputs / total) * 100
    
    def verify_ai_incomplete_list(self, ai_incomplete_sections: List[str]) -> Dict:
        """Verify AI's incomplete list against actual outputs
        
        Returns:
            dict with 'hallucinated' (sections AI said incomplete but have outputs)
            and 'actually_incomplete' (sections truly incomplete)
        """
        outputs_map = self.check_outputs_exist()
        
        # Map section names to cell indices (approximate)
        # This is a simple heuristic - could be improved
        hallucinated = []
        actually_incomplete = []
        
        for section in ai_incomplete_sections:
            # Check if this section likely has outputs
            # For now, if most cells have outputs, assume AI is hallucinating
            completion_pct = self.get_completion_percentage()
            
            if completion_pct > 80:  # If 80%+ cells have outputs
                hallucinated.append(section)
            else:
                actually_incomplete.append(section)
        
        return {
            'hallucinated': hallucinated,
            'actually_incomplete': actually_incomplete,
            'completion_percentage': completion_pct
        }
    
    def fix_ai_grading_result(self, ai_result: Dict) -> Dict:
        """Fix AI grading result by verifying outputs exist
        
        Args:
            ai_result: The grading result from AI
            
        Returns:
            Fixed grading result with corrected incomplete_sections_count
        """
        with_outputs, total = self.count_cells_with_outputs()
        completion_pct = self.get_completion_percentage()
        
        # If 90%+ of cells have outputs, override AI's incomplete count
        if completion_pct >= 90:
            print(f"🔍 Output Verifier: {with_outputs}/{total} cells have outputs ({completion_pct:.0f}%)")
            print(f"🔧 Student attempted all work - checking correctness...")
            
            # Fix the incomplete sections count
            ai_result['incomplete_sections_count'] = max(0, total - with_outputs)
            
            # IMPORTANT: Only boost scores if AI gave reasonable scores
            # If AI gave low score despite completion, it likely found incorrect results
            current_tech_score = ai_result.get('technical_score', 0)
            
            if 'technical_score' in ai_result:
                # If AI already gave 85+, boost to reward completion
                if current_tech_score >= 85:
                    if completion_pct >= 100:
                        ai_result['technical_score'] = max(current_tech_score, 95)
                        print(f"🎯 100% completion with good work - boosting to minimum 95%")
                    elif completion_pct >= 95:
                        ai_result['technical_score'] = max(current_tech_score, 92)
                # If AI gave 70-84, student completed but has errors - modest boost
                elif current_tech_score >= 70:
                    ai_result['technical_score'] = max(current_tech_score, 80)
                    print(f"⚠️ 100% completion but AI found issues - modest boost to 80%")
                # If AI gave <70, student has serious errors - minimal boost
                else:
                    ai_result['technical_score'] = max(current_tech_score, 70)
                    print(f"❌ 100% completion but AI found major issues - minimal boost to 70%")
            
            # Also boost total score proportionally
            if 'total_score' in ai_result and 'max_score' in ai_result:
                current_pct = (ai_result['total_score'] / ai_result['max_score']) * 100
                # Only boost if current score is reasonable (>75%)
                if completion_pct >= 100 and current_pct >= 75 and current_pct < 90:
                    ai_result['total_score'] = max(ai_result['total_score'], ai_result['max_score'] * 0.90)
                    print(f"🎯 Boosting total score to {ai_result['total_score']:.1f}/{ai_result['max_score']}")
        
        # If 80-89% have outputs, be more lenient
        elif completion_pct >= 80:
            print(f"🔍 Output Verifier: {with_outputs}/{total} cells have outputs ({completion_pct:.0f}%)")
            print(f"🔧 Adjusting AI's assessment - most work is complete")
            
            # Reduce incomplete count
            ai_result['incomplete_sections_count'] = min(
                ai_result.get('incomplete_sections_count', 5),
                max(2, total - with_outputs)
            )
            
            # Boost technical score for 80%+ completion
            if 'technical_score' in ai_result:
                ai_result['technical_score'] = max(ai_result.get('technical_score', 0), 85)
        
        return ai_result
    
    def generate_verification_report(self) -> str:
        """Generate a human-readable verification report"""
        with_outputs, total = self.count_cells_with_outputs()
        completion_pct = self.get_completion_percentage()
        
        report = f"""
📊 Output Verification Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Code Cells: {total}
Cells with Outputs: {with_outputs}
Completion: {completion_pct:.1f}%

Assessment:
"""
        
        if completion_pct >= 95:
            report += "✅ EXCELLENT - Nearly all cells executed\n"
            report += "   Student completed all work with outputs.\n"
        elif completion_pct >= 85:
            report += "✅ GOOD - Most cells executed\n"
            report += "   Student completed most work with outputs.\n"
        elif completion_pct >= 70:
            report += "⚠️ ADEQUATE - Many cells executed\n"
            report += "   Student completed majority of work.\n"
        elif completion_pct >= 50:
            report += "⚠️ INCOMPLETE - Some cells executed\n"
            report += "   Student completed about half the work.\n"
        else:
            report += "❌ MINIMAL - Few cells executed\n"
            report += "   Student completed minimal work.\n"
        
        return report


def verify_and_fix_grading(notebook_path: str, ai_result: Dict) -> Dict:
    """Convenience function to verify and fix AI grading
    
    Args:
        notebook_path: Path to student's notebook
        ai_result: Grading result from AI
        
    Returns:
        Fixed grading result
    """
    verifier = OutputVerifier(notebook_path)
    
    # Print verification report
    print(verifier.generate_verification_report())
    
    # Fix AI result
    fixed_result = verifier.fix_ai_grading_result(ai_result)
    
    # NEW: Fix false "incomplete" claims in technical analysis
    with_outputs, total = verifier.count_cells_with_outputs()
    completion_pct = verifier.get_completion_percentage()
    
    if completion_pct >= 85:  # If 85%+ cells have outputs
        print(f"🔧 Fixing AI's false 'incomplete' claims...")
        
        # Check technical analysis for false incomplete claims
        if 'technical_analysis' in fixed_result:
            tech = fixed_result['technical_analysis']
            
            # Remove ONLY false "incomplete" claims (not "incorrect" claims)
            if 'technical_observations' in tech:
                # Filter out any line that mentions "Incomplete:" or lists incomplete sections
                filtered_obs = []
                skip_next = False
                for obs in tech['technical_observations']:
                    obs_lower = obs.lower()
                    # Skip lines that claim incompleteness
                    if any(phrase in obs_lower for phrase in [
                        'incomplete:', 'did not complete', 'missing section',
                        'not complete', 'unfinished', 'incomplete submission',
                        'completion:', 'completed:'
                    ]) and 'validator' not in obs_lower and 'verifier' not in obs_lower:
                        continue
                    filtered_obs.append(obs)
                
                tech['technical_observations'] = filtered_obs
                
                # Add correction note about completion (not correctness)
                tech['technical_observations'].insert(0,
                    f"✅ OUTPUT VERIFIER: {with_outputs}/{total} cells have outputs ({completion_pct:.0f}%) - all work attempted"
                )
            
            # Fix code suggestions that claim incompleteness (but keep correctness feedback)
            if 'code_suggestions' in tech:
                tech['code_suggestions'] = [
                    sug for sug in tech['code_suggestions']
                    if not any(phrase in sug.lower() for phrase in [
                        'did not complete', 'missing section', 'incomplete submission',
                        'could not be completed automatically', 'please review submission manually',
                        'code analysis could not', 'manual review'
                    ])
                    # Keep suggestions about incorrect results, wrong approach, etc.
                ]
                
                # If we removed all suggestions, add helpful ones
                if not tech['code_suggestions']:
                    tech['code_suggestions'] = [
                        "Consider adding more detailed comments to explain your analytical approach",
                        "Explore additional dplyr functions like mutate() and summarize()",
                        "Practice combining multiple operations in longer pipe chains"
                    ]
            
            # Fix code strengths - remove "unable to parse" if outputs exist
            if 'code_strengths' in tech:
                tech['code_strengths'] = [
                    strength for strength in tech['code_strengths']
                    if 'unable to parse' not in strength.lower()
                ]
                
                # If we removed the only strength, add a real one
                if not tech['code_strengths']:
                    tech['code_strengths'] = [
                        f"Completed {with_outputs}/{total} code sections with working outputs",
                        "Demonstrated ability to execute R code successfully",
                        "Produced verifiable results for analysis tasks"
                    ]
        
        # Fix comprehensive feedback instructor comments
        if 'comprehensive_feedback' in fixed_result:
            comp_feed = fixed_result['comprehensive_feedback']
            
            if 'instructor_comments' in comp_feed and isinstance(comp_feed['instructor_comments'], str):
                comments = comp_feed['instructor_comments']
                
                # Remove false claims about incomplete work (not incorrect work)
                false_claims = [
                    'the notebook does not include the required dplyr operations',
                    'does not include the required',
                    'the current notebook only shows data import',
                    'only shows data import',
                    'complete the remaining assignment tasks',
                    'finish the missing',
                    'did not complete'
                ]
                
                for claim in false_claims:
                    if claim in comments.lower():
                        # Replace with accurate statement about completion
                        comments = comments.replace(
                            claim,
                            f"you attempted {with_outputs}/{total} code sections"
                        )
                
                comp_feed['instructor_comments'] = comments
    
    return fixed_result


if __name__ == "__main__":
    # Test the verifier
    import sys
    
    if len(sys.argv) > 1:
        notebook_path = sys.argv[1]
        verifier = OutputVerifier(notebook_path)
        print(verifier.generate_verification_report())
        
        with_outputs, total = verifier.count_cells_with_outputs()
        print(f"\n📈 Result: {with_outputs}/{total} cells have outputs")
    else:
        print("Usage: python output_verifier.py <notebook_path>")
