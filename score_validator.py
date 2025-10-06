#!/usr/bin/env python3
"""
Score Validator - Enforces strict scoring rules
Prevents AI from giving inflated scores
"""

def validate_and_adjust_scores(code_analysis: dict, feedback: dict, student_code: str, template_code: str = "") -> tuple:
    """
    Validate scores and adjust if AI was too generous
    Returns (adjusted_code_analysis, adjusted_feedback)
    """
    print("="*80)
    print("🔍 SCORE VALIDATOR CALLED")
    print("="*80)
    
    # Count TODO sections that are ACTUALLY incomplete (no working code after them)
    incomplete_todos = 0
    lines = student_code.split('\n')
    
    for i, line in enumerate(lines):
        if '# YOUR CODE HERE' in line or '# TODO' in line:
            # Check if there's actual code in the next 5 lines
            has_code = False
            for j in range(i+1, min(i+6, len(lines))):
                next_line = lines[j].strip()
                # Check if it's actual code (not just comments or empty)
                if next_line and not next_line.startswith('#') and next_line != '':
                    has_code = True
                    break
            
            if not has_code:
                incomplete_todos += 1
    
    print(f"🔍 VALIDATOR: Found {incomplete_todos} truly incomplete TODO sections (no code after them)")
    print(f"🔍 VALIDATOR: Student code length: {len(student_code)} chars, Template code length: {len(template_code) if template_code else 0} chars")
    
    # If template provided, compare to see what was added
    if template_code and len(template_code) > 100:
        # Compare code length - if student code is barely longer than template, it's incomplete
        student_lines = len([l for l in student_code.split('\n') if l.strip() and not l.strip().startswith('#')])
        template_lines = len([l for l in template_code.split('\n') if l.strip() and not l.strip().startswith('#')])
        
        if student_lines < template_lines * 1.1:  # Less than 10% more code than template
            print(f"⚠️ VALIDATOR: Student added minimal code ({student_lines} vs {template_lines} template lines)")
            incomplete_todos = max(incomplete_todos, 8)  # Treat as mostly incomplete
    
    # Enforce maximum scores based on completion
    if incomplete_todos >= 10:
        # Essentially just the template
        max_score = 20
        reason = f"Found {incomplete_todos} incomplete TODO sections - this is essentially the template"
    elif incomplete_todos >= 5:
        max_score = 50
        reason = f"Found {incomplete_todos} incomplete TODO sections"
    elif incomplete_todos >= 3:
        max_score = 70
        reason = f"Found {incomplete_todos} incomplete TODO sections"
    else:
        max_score = 100
        reason = None
    
    # Adjust code analysis scores
    original_technical = code_analysis.get('technical_score', 0)
    if original_technical > max_score:
        print(f"⚠️ VALIDATOR: Reducing technical_score from {original_technical} to {max_score}")
        print(f"   Reason: {reason}")
        code_analysis['technical_score'] = max_score
        code_analysis['syntax_correctness'] = min(code_analysis.get('syntax_correctness', 0), max_score)
        code_analysis['logic_correctness'] = min(code_analysis.get('logic_correctness', 0), max_score)
        code_analysis['effort_and_completion'] = min(code_analysis.get('effort_and_completion', 0), max_score)
        
        # Add validator note
        if 'technical_observations' not in code_analysis:
            code_analysis['technical_observations'] = []
        code_analysis['technical_observations'].insert(0, 
            f"⚠️ VALIDATOR ADJUSTMENT: Score capped at {max_score}% due to incomplete work. {reason}")
    
    # Adjust feedback scores
    original_overall = feedback.get('overall_score', 0)
    if original_overall > max_score:
        print(f"⚠️ VALIDATOR: Reducing overall_score from {original_overall} to {max_score}")
        feedback['overall_score'] = max_score
        feedback['business_understanding'] = min(feedback.get('business_understanding', 0), max_score)
        feedback['communication_clarity'] = min(feedback.get('communication_clarity', 0), max_score)
        feedback['methodology_appropriateness'] = min(feedback.get('methodology_appropriateness', 0), max_score)
    
    # NEW: Check for UNDERGRADING (AI being too harsh)
    # If student has substantial code and outputs, but AI gave low score, boost it
    student_code_lines = len([l for l in student_code.split('\n') if l.strip() and not l.strip().startswith('#')])
    has_outputs = '# OUTPUT:' in student_code or 'output_type' in student_code.lower()
    
    # If student has lots of code (>100 lines) and outputs, they did substantial work
    if student_code_lines > 100 and has_outputs:
        # More aggressive boost - if AI can't parse but outputs exist, assume good work
        min_technical_score = 85  # Increased from 75 to 85
        min_overall_score = 85    # Increased from 75 to 85
        
        if code_analysis.get('technical_score', 0) < min_technical_score:
            old_score = code_analysis.get('technical_score', 0)
            print(f"⚠️ VALIDATOR: UNDERGRADING DETECTED!")
            print(f"   Student has {student_code_lines} lines of code with outputs")
            print(f"   Boosting technical_score from {old_score} to {min_technical_score}")
            code_analysis['technical_score'] = min_technical_score
            code_analysis['syntax_correctness'] = max(code_analysis.get('syntax_correctness', 0), min_technical_score)
            code_analysis['logic_correctness'] = max(code_analysis.get('logic_correctness', 0), min_technical_score)
            code_analysis['effort_and_completion'] = max(code_analysis.get('effort_and_completion', 0), min_technical_score)
            
            if 'technical_observations' not in code_analysis:
                code_analysis['technical_observations'] = []
            code_analysis['technical_observations'].insert(0,
                f"✅ VALIDATOR ADJUSTMENT: Score boosted to {min_technical_score}% - substantial work with outputs detected")
        
        if feedback.get('overall_score', 0) < min_overall_score:
            old_score = feedback.get('overall_score', 0)
            print(f"   Boosting overall_score from {old_score} to {min_overall_score}")
            feedback['overall_score'] = min_overall_score
            feedback['business_understanding'] = max(feedback.get('business_understanding', 0), min_overall_score)
            feedback['communication_clarity'] = max(feedback.get('communication_clarity', 0), min_overall_score)
            feedback['data_interpretation'] = max(feedback.get('data_interpretation', 0), min_overall_score)
            feedback['methodology_appropriateness'] = max(feedback.get('methodology_appropriateness', 0), min_overall_score)
            feedback['reflection_quality'] = max(feedback.get('reflection_quality', 0), min_overall_score)
    
    return code_analysis, feedback
