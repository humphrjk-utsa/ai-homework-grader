#!/usr/bin/env python3
"""
Test the new validator with the Assignment 6 case
"""

from score_validator import validate_and_adjust_scores

# Simulate the Assignment 6 submission
student_code = """
# Part 5.2: Product Metrics
# REQUIRED variable name: product_metrics
# Your code here:

# Required output for autograding:
cat("Product Analysis Summary: ")
cat("Total products analyzed:", nrow(product_metrics), " ")
# Output: Error: object 'product_metrics' not found

# Part 6.3: Critical Suppliers
critical_suppliers <- supplier_metrics %>%
  mutate(Critical_Score = Total_Revenue * Products_Supplied)
# Output: Error: object 'Total_Revenue' not found
"""

# Simulate AI's analysis (it gave 85%)
code_analysis = {
    'technical_score': 85,
    'syntax_correctness': 85,
    'logic_correctness': 85,
    'effort_and_completion': 85,
    'technical_observations': []
}

feedback = {
    'overall_score': 85,
    'business_understanding': 85,
    'communication_clarity': 85
}

# Simulate rubric with required variables
rubric = {
    'autograder_checks': {
        'required_variables': [
            'customers', 'orders', 'customer_orders',
            'product_metrics',  # MISSING
            'supplier_metrics',
            'critical_suppliers'
        ]
    }
}

print("="*80)
print("TESTING NEW VALIDATOR WITH OUTPUT COMPARISON")
print("="*80)
print(f"\nBEFORE VALIDATION:")
print(f"  Technical Score: {code_analysis['technical_score']}%")
print(f"  Overall Score: {feedback['overall_score']}%")

# Simulate output comparison (student outputs don't match solution)
output_comparison = {
    'total_cells': 12,
    'matching_cells': 8,  # Only 8 out of 12 match
    'match_rate': 66.7,   # 66.7% match rate
    'accuracy_score': 66.7
}

print(f"\nOUTPUT COMPARISON:")
print(f"  Match Rate: {output_comparison['match_rate']:.1f}%")
print(f"  Matching Cells: {output_comparison['matching_cells']}/{output_comparison['total_cells']}")

# Run validator
code_analysis_adj, feedback_adj = validate_and_adjust_scores(
    code_analysis, 
    feedback, 
    student_code,
    "",  # no template
    rubric,
    output_comparison  # NEW: pass output comparison
)

print(f"\nAFTER VALIDATION:")
print(f"  Technical Score: {code_analysis_adj['technical_score']}%")
print(f"  Overall Score: {feedback_adj['overall_score']}%")

if 'technical_observations' in code_analysis_adj:
    print(f"\nValidator Notes:")
    for note in code_analysis_adj['technical_observations']:
        print(f"  - {note}")

print("\n" + "="*80)
print("EXPECTED RESULT:")
print("  Score should be capped at 75% due to:")
print("  - 2 errors detected → cap at 80%")
print("  - 5 missing required variables → cap at 75%")
print("  - 66.7% output match rate → cap at 80%")
print("  Most restrictive rule wins: 75%")
print("="*80)
