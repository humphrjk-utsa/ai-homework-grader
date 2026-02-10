#!/usr/bin/env python3
"""
Flexible Partial Credit System
Reads partial credit rules from the rubric JSON instead of hardcoding them
"""

import re
from typing import Dict, Any, List


class FlexiblePartialCreditScorer:
    """
    Applies partial credit based on rules defined in the rubric
    
    Rubric can define partial credit scenarios like:
    {
      "partial_credit_rules": {
        "section_id": {
          "rule_name": {
            "condition": "regex pattern or check",
            "multiplier": 0.85,
            "explanation": "Why this gets 85% credit"
          }
        }
      }
    }
    """
    
    def __init__(self, rubric: Dict):
        """Initialize with rubric containing partial credit rules"""
        self.rubric = rubric
        self.partial_credit_rules = rubric.get('partial_credit_rules', {})
        self.adjustments_made = []
        
        if self.partial_credit_rules:
            print(f"✅ Loaded {len(self.partial_credit_rules)} partial credit rule sets")
    
    def adjust_score(self, section_id: str, section_result: Dict, code: str, nb) -> Dict[str, Any]:
        """
        Apply partial credit rules for a specific section
        
        Returns:
            Updated section_result with adjusted score
        """
        # Check if this section has partial credit rules
        if section_id not in self.partial_credit_rules:
            return section_result
        
        rules = self.partial_credit_rules[section_id]
        base_points = section_result['points']
        
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(
            rules.items(),
            key=lambda x: x[1].get('priority', 999)
        )
        
        # Find the first matching rule (highest priority)
        best_match = None
        best_multiplier = 0
        
        for rule_name, rule_config in sorted_rules:
            if self._check_rule_condition(rule_config, code, nb):
                multiplier = rule_config.get('multiplier', 1.0)
                best_multiplier = multiplier
                best_match = rule_config
                break  # Take first match (highest priority)
        
        # Apply the best matching rule
        if best_match:
            adjusted_score = base_points * best_multiplier
            
            self.adjustments_made.append({
                'section': section_result['name'],
                'rule': best_match.get('explanation', 'Partial credit applied'),
                'multiplier': best_multiplier,
                'original_score': section_result['score'],
                'adjusted_score': adjusted_score
            })
            
            return {
                **section_result,
                'score': adjusted_score,
                'adjustment_applied': True,
                'adjustment_explanation': best_match.get('explanation', 'Partial credit applied'),
                'original_score': section_result['score']
            }
        
        return section_result
    
    def _check_rule_condition(self, rule_config: Dict, code: str, nb) -> bool:
        """
        Check if a rule's condition is met
        
        Supports:
        - regex: Check if pattern exists in code
        - not_regex: Check if pattern does NOT exist
        - all_of: All patterns must exist
        - any_of: At least one pattern must exist
        - not_patterns: Patterns that must NOT exist (works with all condition types)
        """
        condition_type = rule_config.get('condition_type', 'regex')
        
        # First check the main condition
        main_condition_met = False
        
        if condition_type == 'regex':
            pattern = rule_config.get('pattern', '')
            main_condition_met = bool(re.search(pattern, code, re.IGNORECASE | re.DOTALL))
        
        elif condition_type == 'not_regex':
            pattern = rule_config.get('pattern', '')
            main_condition_met = not bool(re.search(pattern, code, re.IGNORECASE | re.DOTALL))
        
        elif condition_type == 'all_of':
            patterns = rule_config.get('patterns', [])
            main_condition_met = all(re.search(p, code, re.IGNORECASE | re.DOTALL) for p in patterns)
        
        elif condition_type == 'any_of':
            patterns = rule_config.get('patterns', [])
            main_condition_met = any(re.search(p, code, re.IGNORECASE | re.DOTALL) for p in patterns)
        
        elif condition_type == 'count_formats':
            # Special case for counting date formats
            main_condition_met = self._count_date_formats(code, rule_config)
        
        # If main condition not met, return False
        if not main_condition_met:
            return False
        
        # Check not_patterns (patterns that must NOT exist)
        not_patterns = rule_config.get('not_patterns', [])
        if not_patterns:
            for pattern in not_patterns:
                if re.search(pattern, code, re.IGNORECASE | re.DOTALL):
                    return False  # Found a pattern that shouldn't exist
        
        return True
    
    def _count_date_formats(self, code: str, rule_config: Dict) -> bool:
        """Count how many date formats are included in parse_date_time"""
        orders_match = re.search(r'orders\s*=\s*c\s*\((.*?)\)', code, re.DOTALL)
        if not orders_match:
            return False
        
        orders_str = orders_match.group(1)
        formats_to_check = rule_config.get('formats', [])
        
        count = sum(1 for fmt in formats_to_check if fmt.lower() in orders_str.lower())
        
        min_count = rule_config.get('min_count', 0)
        max_count = rule_config.get('max_count', 999)
        
        return min_count <= count <= max_count
    
    def get_adjustment_summary(self) -> str:
        """Get a summary of all adjustments made"""
        if not self.adjustments_made:
            return "No partial credit adjustments needed"
        
        summary = "Partial Credit Adjustments:\n"
        summary += "="*80 + "\n"
        for adj in self.adjustments_made:
            summary += f"\n{adj['section']}:\n"
            summary += f"  Rule: {adj['rule']}\n"
            summary += f"  Multiplier: {adj['multiplier']:.0%}\n"
            summary += f"  Score: {adj['original_score']:.1f} → {adj['adjusted_score']:.1f}\n"
        
        return summary
