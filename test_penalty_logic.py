#!/usr/bin/env python3
"""
Test the penalty logic directly
"""

def calculate_adjusted_score(base_score, score_adjustment):
    """Simulate the adjusted score calculation from grader_v2"""
    if score_adjustment:
        # Smart penalty application:
        if base_score < 30:
            # Student hasn't done much work - don't double-penalize for missing outputs
            adjusted_score = base_score
        else:
            # Student did substantial work - penalize for incorrect outputs
            if score_adjustment < 0:
                max_penalty = min(abs(score_adjustment), base_score * 0.5)  # Max 50% penalty
                adjusted_score = max(0, base_score - max_penalty)
            else:
                adjusted_score = base_score + score_adjustment
    else:
        adjusted_score = base_score
    
    return adjusted_score

print("="*80)
print("TESTING PENALTY LOGIC")
print("="*80)

test_cases = [
    {"base": 12, "adjustment": -15, "desc": "Low scorer with harsh penalty"},
    {"base": 25, "adjustment": -15, "desc": "Low scorer (just under 30%)"},
    {"base": 35, "adjustment": -15, "desc": "Medium scorer with harsh penalty"},
    {"base": 86.9, "adjustment": -2, "desc": "High scorer with small penalty"},
    {"base": 98.7, "adjustment": 0, "desc": "Perfect scorer"},
    {"base": 50, "adjustment": -20, "desc": "Medium scorer with 20pt penalty (should cap at 25)"},
]

print("\nTest Cases:")
print("-" * 80)

for test in test_cases:
    adjusted = calculate_adjusted_score(test['base'], test['adjustment'])
    print(f"\n{test['desc']}")
    print(f"  Base Score: {test['base']:.1f}%")
    print(f"  Adjustment: {test['adjustment']:+.1f} points")
    print(f"  Adjusted Score: {adjusted:.1f}%")
    
    # Check for issues
    if adjusted < 0:
        print(f"  ❌ NEGATIVE SCORE!")
    elif test['base'] < 30 and adjusted != test['base']:
        print(f"  ❌ Low scorer got penalized!")
    elif test['base'] >= 30 and test['adjustment'] < 0:
        penalty_applied = test['base'] - adjusted
        max_allowed = test['base'] * 0.5
        if penalty_applied > max_allowed + 0.1:  # Allow small rounding
            print(f"  ❌ Penalty exceeded 50% cap!")
        else:
            print(f"  ✅ Penalty capped correctly ({penalty_applied:.1f} <= {max_allowed:.1f})")
    else:
        print(f"  ✅ Correct")

print("\n" + "="*80)
