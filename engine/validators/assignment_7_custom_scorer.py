#!/usr/bin/env python3
"""
Custom scorer for Assignment 7 that provides nuanced partial credit
for common adaptation issues with Version 2 data
"""

import re
from typing import Dict, Any


class Assignment7CustomScorer:
    """
    Provides custom scoring logic for Assignment 7 that accounts for:
    - Partial date parsing (missing some formats)
    - CustomerID workarounds (no customer names in data)
    - Date display formatting issues
    - NA handling in calculations
    """
    
    def __init__(self):
        self.adjustments = []
    
    def adjust_score(self, section_id: str, section_result: Dict, code: str, nb) -> Dict[str, Any]:
        """
        Apply custom scoring adjustments for specific sections
        
        Returns:
            Dict with adjusted score and explanation
        """
        if section_id == 'part4_date_operations':
            return self._adjust_date_parsing_score(section_result, code, nb)
        elif section_id == 'part6_combined_operations':
            return self._adjust_customer_name_score(section_result, code, nb)
        elif section_id == 'part7_business_intelligence':
            return self._adjust_dashboard_score(section_result, code, nb)
        else:
            return section_result
    
    def _adjust_date_parsing_score(self, section_result: Dict, code: str, nb) -> Dict:
        """
        Adjust score for date parsing based on approach used
        
        Scoring:
        - parse_date_time with all 3 formats (mdy HM, dmy HMS, ymd_HMS): 100%
        - parse_date_time with 2/3 formats: 85%
        - mdy_hm only: 70%
        - ymd only: 40%
        """
        base_points = section_result['points']
        
        # Check what date parsing approach was used
        has_parse_date_time = bool(re.search(r'parse_date_time\s*\(', code))
        has_mdy = bool(re.search(r'\bmdy\s*\(', code))
        has_ymd = bool(re.search(r'\bymd\s*\(', code))
        
        # Check for format orders in parse_date_time
        if has_parse_date_time:
            # Look for the orders parameter
            orders_match = re.search(r'orders\s*=\s*c\s*\((.*?)\)', code, re.DOTALL)
            if orders_match:
                orders_str = orders_match.group(1)
                
                # Count how many formats are included
                has_mdy_format = bool(re.search(r'["\']mdy\s+HM["\']', orders_str, re.IGNORECASE))
                has_dmy_format = bool(re.search(r'["\']dmy\s+HMS["\']', orders_str, re.IGNORECASE))
                has_ymd_format = bool(re.search(r'["\']ymd[_\s]*HMS["\']', orders_str, re.IGNORECASE))
                
                format_count = sum([has_mdy_format, has_dmy_format, has_ymd_format])
                
                if format_count == 3:
                    # Perfect! All formats handled
                    multiplier = 1.0
                    explanation = "Used parse_date_time() with all 3 date formats"
                elif format_count == 2:
                    # Good! Most formats handled (Anathalia's case)
                    multiplier = 0.85
                    explanation = "Used parse_date_time() with 2/3 formats (some data loss acceptable)"
                    self.adjustments.append({
                        'section': 'Date Parsing',
                        'issue': 'Missing ymd_HMS format for ISO dates',
                        'impact': '22% data loss (33/150 dates)',
                        'credit': '85%'
                    })
                else:
                    # Partial - only one format
                    multiplier = 0.70
                    explanation = "Used parse_date_time() with 1 format only (significant data loss)"
            else:
                # parse_date_time without orders parameter
                multiplier = 0.60
                explanation = "Used parse_date_time() without specifying orders"
        elif has_mdy:
            # Used mdy() - lesson method but loses data
            multiplier = 0.70
            explanation = "Used mdy() - lesson method but loses 40% of data"
        elif has_ymd:
            # Used ymd() - doesn't match data format
            multiplier = 0.40
            explanation = "Used ymd() - doesn't match data format"
        else:
            # No date parsing found
            multiplier = 0.0
            explanation = "No date parsing function found"
        
        adjusted_score = base_points * multiplier
        
        return {
            **section_result,
            'score': adjusted_score,
            'adjustment_applied': True,
            'adjustment_explanation': explanation,
            'original_score': section_result['score']
        }
    
    def _adjust_customer_name_score(self, section_result: Dict, code: str, nb) -> Dict:
        """
        Adjust score for customer name extraction
        
        Scoring:
        - Synthetic names (paste("Customer", CustomerID)): 100%
        - Join with feedback table: 100%
        - Use CustomerID directly: 60%
        - Extract digits from CustomerID: 30%
        """
        base_points = section_result['points']
        
        # Check approach used
        has_synthetic_names = bool(re.search(r'paste\s*\(["\']Customer["\']', code, re.IGNORECASE))
        has_join = bool(re.search(r'(left_join|inner_join|merge)\s*\(', code))
        uses_customerid_directly = bool(re.search(r'CustomerID', code))
        extracts_digits = bool(re.search(r'str_extract\s*\(\s*CustomerID.*?\\d', code))
        
        if has_synthetic_names or has_join:
            multiplier = 1.0
            explanation = "Proper workaround for missing customer names"
        elif extracts_digits:
            # Anathalia's case - extracts digits from CustomerID
            multiplier = 0.30
            explanation = "Extracts digits from CustomerID (functional but incorrect logic)"
            self.adjustments.append({
                'section': 'Customer Names',
                'issue': 'Extracting CustomerID digits instead of creating names',
                'impact': 'First names are numbers (26, 21, 12)',
                'credit': '30%'
            })
        elif uses_customerid_directly:
            multiplier = 0.60
            explanation = "Uses CustomerID directly (acceptable workaround)"
        else:
            multiplier = 0.0
            explanation = "No customer name handling found"
        
        adjusted_score = base_points * multiplier
        
        return {
            **section_result,
            'score': adjusted_score,
            'adjustment_applied': True,
            'adjustment_explanation': explanation,
            'original_score': section_result['score']
        }
    
    def _adjust_dashboard_score(self, section_result: Dict, code: str, nb) -> Dict:
        """
        Adjust score for business intelligence dashboard
        
        Checks:
        - Most common category calculation (correct method vs first value)
        - Date display formatting (formatted vs numeric)
        - Weekend percentage calculation (NA handling)
        """
        base_points = section_result['points']
        deductions = []
        
        # Check most common category calculation
        wrong_category_method = bool(re.search(r'category_clean\s*\[\s*1\s*\]', code))
        if wrong_category_method:
            deductions.append({
                'issue': 'Takes first category instead of most common',
                'points': 2
            })
            self.adjustments.append({
                'section': 'Dashboard - Category',
                'issue': 'Used [1] instead of count() and arrange()',
                'impact': 'Shows "Tv" instead of "Electronics"',
                'credit': '0% for this calculation'
            })
        
        # Check date display formatting
        wrong_date_display = bool(re.search(r'min\s*\(\s*na\.omit\s*\(\s*as\.Date', code))
        if wrong_date_display:
            deductions.append({
                'issue': 'Dates display as numeric epoch days',
                'points': 1
            })
            self.adjustments.append({
                'section': 'Dashboard - Dates',
                'issue': 'Dates show as epoch days (19797) instead of formatted',
                'impact': 'Unreadable date range',
                'credit': '50% for date display'
            })
        
        # Check weekend percentage NA handling
        missing_na_rm = bool(re.search(r'sum\s*\(\s*[^)]*is_weekend[^)]*\)\s*/.*\*\s*100', code))
        has_na_rm = bool(re.search(r'na\.rm\s*=\s*TRUE', code))
        if missing_na_rm and not has_na_rm:
            deductions.append({
                'issue': 'Weekend calculation doesn\'t handle NAs',
                'points': 0.6
            })
            self.adjustments.append({
                'section': 'Dashboard - Weekend %',
                'issue': 'Missing na.rm=TRUE in calculation',
                'impact': 'Affected by NA values from failed date parsing',
                'credit': '80% for this calculation'
            })
        
        total_deduction = sum(d['points'] for d in deductions)
        adjusted_score = max(0, base_points - total_deduction)
        
        explanation = f"Dashboard score adjusted: {len(deductions)} issues found"
        
        return {
            **section_result,
            'score': adjusted_score,
            'adjustment_applied': True,
            'adjustment_explanation': explanation,
            'deductions': deductions,
            'original_score': section_result['score']
        }
    
    def get_adjustment_summary(self) -> str:
        """Get a summary of all adjustments made"""
        if not self.adjustments:
            return "No adjustments needed - perfect work!"
        
        summary = "Score Adjustments Applied:\n"
        summary += "="*80 + "\n"
        for adj in self.adjustments:
            summary += f"\n{adj['section']}:\n"
            summary += f"  Issue: {adj['issue']}\n"
            summary += f"  Impact: {adj['impact']}\n"
            summary += f"  Credit: {adj['credit']}\n"
        
        return summary
