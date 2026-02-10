#!/usr/bin/env python3
"""
Score Validator - Enforces strict scoring rules
Prevents AI from giving inflated scores
Now with smarter validation that checks for errors and required variables
"""

def validate_and_adjust_scores(code_analysis: dict, feedback: dict, student_code: str, template_code: str = "", rubric: dict = None, output_comparison: dict = None) -> tuple:
    """
    Validate scores and adjust if AI was too generous
    Now includes output comparison validation
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
    
    # SMART VALIDATION: Check for quality indicators before boosting
    student_code_lines = len([l for l in student_code.split('\n') if l.strip() and not l.strip().startswith('#')])
    has_outputs = '# OUTPUT:' in student_code or 'output_type' in student_code.lower() or '# A tibble:' in student_code
    
    # Check for error indicators that mean work is incomplete
    error_indicators = [
        'Error:',
        'Error in',
        'object not found',
        'could not find function',
        'undefined columns',
        'argument is missing',
        'subscript out of bounds'
    ]
    
    # Errors to IGNORE (not student's fault)
    ignore_errors = [
        'Error in parse(text = input): <text>:1:1: unexpected',  # Markdown in code cell (Jupyter issue)
        'Unknown or uninitialised column',  # Warning, not critical error
    ]
    
    # Count errors, but exclude ignorable ones
    error_count = 0
    for indicator in error_indicators:
        count = student_code.count(indicator)
        # Check if this error should be ignored
        should_ignore = any(ignore_pattern in student_code for ignore_pattern in ignore_errors)
        if not should_ignore:
            error_count += count
    
    has_errors = error_count > 0
    
    # Check for required variables if rubric provided
    missing_required_vars = []
    if rubric and 'autograder_checks' in rubric and 'required_variables' in rubric['autograder_checks']:
        required_vars = rubric['autograder_checks']['required_variables']
        for var in required_vars:
            # Check if variable is created (more flexible matching)
            # Look for: "var_name <-" or "var_name<-" or "var_name =" or variable mentioned in output
            var_patterns = [
                f"{var} <-",
                f"{var}<-",
                f"{var} =",
                f"{var}=",
                f"# {var}",  # Variable mentioned in comments/output
                f"${var}",  # Variable accessed
                f"print({var})",  # Variable printed
                f"nrow({var})",  # Variable used
            ]
            
            # Check if any pattern exists
            var_exists = any(pattern in student_code for pattern in var_patterns)
            
            # Also check if variable name appears multiple times (likely created and used)
            var_count = student_code.count(var)
            if var_count >= 3:  # If mentioned 3+ times, probably exists
                var_exists = True
            
            if not var_exists:
                missing_required_vars.append(var)
    
    print(f"🔍 VALIDATOR QUALITY CHECK:")
    print(f"   Code lines: {student_code_lines}")
    print(f"   Has outputs: {has_outputs}")
    print(f"   Error count: {error_count}")
    print(f"   Missing required variables: {len(missing_required_vars)}")
    if missing_required_vars:
        print(f"   Missing vars: {', '.join(missing_required_vars[:5])}")
    
    # RULE 1: If multiple errors detected, cap score
    if error_count >= 3:
        max_score_with_errors = 70
        print(f"⚠️ VALIDATOR: Detected {error_count} errors - capping at {max_score_with_errors}%")
        if code_analysis.get('technical_score', 0) > max_score_with_errors:
            code_analysis['technical_score'] = max_score_with_errors
            code_analysis['logic_correctness'] = min(code_analysis.get('logic_correctness', 0), max_score_with_errors)
            
            if 'technical_observations' not in code_analysis:
                code_analysis['technical_observations'] = []
            code_analysis['technical_observations'].insert(0,
                f"⚠️ VALIDATOR: Score capped at {max_score_with_errors}% - detected {error_count} errors in output")
    
    elif error_count >= 1:
        max_score_with_errors = 80
        print(f"⚠️ VALIDATOR: Detected {error_count} error(s) - capping at {max_score_with_errors}%")
        if code_analysis.get('technical_score', 0) > max_score_with_errors:
            code_analysis['technical_score'] = max_score_with_errors
            code_analysis['logic_correctness'] = min(code_analysis.get('logic_correctness', 0), max_score_with_errors)
            
            if 'technical_observations' not in code_analysis:
                code_analysis['technical_observations'] = []
            code_analysis['technical_observations'].insert(0,
                f"⚠️ VALIDATOR: Score capped at {max_score_with_errors}% - detected {error_count} error(s) in output")
    
    # RULE 2: If many required variables missing, cap score (but be reasonable)
    if missing_required_vars and len(missing_required_vars) >= 5:
        # Only cap if MANY variables missing (5+)
        max_score_missing_vars = 80
        print(f"⚠️ VALIDATOR: {len(missing_required_vars)} required variables missing - capping at {max_score_missing_vars}%")
        if code_analysis.get('technical_score', 0) > max_score_missing_vars:
            code_analysis['technical_score'] = max_score_missing_vars
            code_analysis['effort_and_completion'] = min(code_analysis.get('effort_and_completion', 0), max_score_missing_vars)
            
            if 'technical_observations' not in code_analysis:
                code_analysis['technical_observations'] = []
            code_analysis['technical_observations'].insert(0,
                f"⚠️ VALIDATOR: Score capped at {max_score_missing_vars}% - {len(missing_required_vars)} required variables not created")
    elif missing_required_vars and len(missing_required_vars) >= 3:
        # Moderate number missing (3-4) - smaller penalty
        print(f"ℹ️ VALIDATOR: {len(missing_required_vars)} required variables may be missing (could be false positives)")
        # Don't cap, just note it
    
    # RULE 3: Only boost if substantial work AND no errors AND no missing required vars
    # This prevents false negatives where AI can't parse but work is good
    if (student_code_lines > 150 and has_outputs and 
        error_count == 0 and len(missing_required_vars) <= 1):
        
        # Conservative boost - only if AI was clearly too harsh
        min_technical_score = 70  # Conservative minimum
        
        if code_analysis.get('technical_score', 0) < 50:  # Only boost if AI gave very low score
            old_score = code_analysis.get('technical_score', 0)
            print(f"✅ VALIDATOR: Possible undergrading detected")
            print(f"   Student has {student_code_lines} lines, outputs, no errors, minimal missing vars")
            print(f"   Boosting technical_score from {old_score} to {min_technical_score}")
            code_analysis['technical_score'] = min_technical_score
            
            if 'technical_observations' not in code_analysis:
                code_analysis['technical_observations'] = []
            code_analysis['technical_observations'].insert(0,
                f"✅ VALIDATOR: Score adjusted to {min_technical_score}% - substantial work detected but verify completeness")
    
    # RULE 4: Validate against output comparison if available (BEFORE trusting AI score)
    if output_comparison:
        match_rate = output_comparison.get('match_rate', 0)
        print(f"🔬 VALIDATOR: Output comparison match rate: {match_rate:.1f}%")
        
        # If outputs don't match, cap the score
        if match_rate < 40:
            # Very low match rate - outputs are wrong
            max_score_outputs = 50
            if code_analysis.get('technical_score', 0) > max_score_outputs:
                print(f"⚠️ VALIDATOR: Output match rate is {match_rate:.1f}% - capping at {max_score_outputs}%")
                code_analysis['technical_score'] = max_score_outputs
                code_analysis['logic_correctness'] = min(code_analysis.get('logic_correctness', 0), max_score_outputs)
                
                if 'technical_observations' not in code_analysis:
                    code_analysis['technical_observations'] = []
                code_analysis['technical_observations'].insert(0,
                    f"⚠️ VALIDATOR: Score capped at {max_score_outputs}% - output comparison shows only {match_rate:.1f}% match with solution")
        
        elif match_rate < 60:
            # Low match rate - many outputs wrong
            max_score_outputs = 70
            if code_analysis.get('technical_score', 0) > max_score_outputs:
                print(f"⚠️ VALIDATOR: Output match rate is {match_rate:.1f}% - capping at {max_score_outputs}%")
                code_analysis['technical_score'] = max_score_outputs
                code_analysis['logic_correctness'] = min(code_analysis.get('logic_correctness', 0), max_score_outputs)
                
                if 'technical_observations' not in code_analysis:
                    code_analysis['technical_observations'] = []
                code_analysis['technical_observations'].insert(0,
                    f"⚠️ VALIDATOR: Score capped at {max_score_outputs}% - output comparison shows only {match_rate:.1f}% match with solution")
        
        elif match_rate < 75:
            # Moderate match rate - some outputs wrong
            max_score_outputs = 80
            if code_analysis.get('technical_score', 0) > max_score_outputs:
                print(f"⚠️ VALIDATOR: Output match rate is {match_rate:.1f}% - capping at {max_score_outputs}%")
                code_analysis['technical_score'] = max_score_outputs
                
                if 'technical_observations' not in code_analysis:
                    code_analysis['technical_observations'] = []
                code_analysis['technical_observations'].insert(0,
                    f"⚠️ VALIDATOR: Score capped at {max_score_outputs}% - output comparison shows {match_rate:.1f}% match with solution")
        
        elif match_rate >= 90:
            # High match rate - outputs are correct
            print(f"✅ VALIDATOR: Output match rate is {match_rate:.1f}% - outputs are correct")
            # Don't cap, but note the good match
            if 'technical_observations' not in code_analysis:
                code_analysis['technical_observations'] = []
            code_analysis['technical_observations'].append(
                f"✅ Output comparison: {match_rate:.1f}% match with solution - outputs are correct")
    
    # RULE 5: Trust the AI's analysis if it's in reasonable range (50-90%) AND no other issues
    # Don't boost if AI already gave 50%+ - it probably saw something we didn't
    current_score = code_analysis.get('technical_score', 0)
    if 50 <= current_score <= 90 and not output_comparison:
        print(f"✅ VALIDATOR: AI score of {current_score}% is reasonable - no adjustment needed")
    elif 50 <= current_score <= 90 and output_comparison:
        match_rate = output_comparison.get('match_rate', 0)
        print(f"✅ VALIDATOR: AI score of {current_score}% with {match_rate:.1f}% output match - validated")
    
    return code_analysis, feedback
