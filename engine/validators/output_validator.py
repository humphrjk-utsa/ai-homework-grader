#!/usr/bin/env python3
"""
Output Validator
Compares student notebook outputs with solution notebook outputs
Allows for reasonable variation while ensuring correctness
"""

import json
import re
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path


class OutputValidator:
    """
    Validates student outputs against solution outputs
    Handles numerical tolerance, row count variations, etc.
    """
    
    def __init__(
        self,
        solution_notebook_path: str,
        numerical_tolerance: float = 0.01,  # 1% tolerance for numerical values
        row_count_tolerance: int = 5,        # Allow ±5 rows difference
        allow_extra_columns: bool = True     # Allow students to add extra columns
    ):
        self.solution_notebook_path = solution_notebook_path
        self.numerical_tolerance = numerical_tolerance
        self.row_count_tolerance = row_count_tolerance
        self.allow_extra_columns = allow_extra_columns
        
        # Load solution notebook
        with open(solution_notebook_path, 'r') as f:
            self.solution_notebook = json.load(f)
        
        # Extract solution outputs
        self.solution_outputs = self._extract_outputs(self.solution_notebook)
    
    def validate_student_outputs(self, student_notebook_path: str) -> Dict[str, Any]:
        """
        Compare student outputs with solution outputs
        
        Returns:
            {
                'overall_match': 0.95,  # 95% match
                'section_results': {...},
                'issues': [...],
                'score_adjustment': -2  # Points to deduct
            }
        """
        # Load student notebook
        with open(student_notebook_path, 'r') as f:
            student_notebook = json.load(f)
        
        # Extract student outputs
        student_outputs = self._extract_outputs(student_notebook)
        
        # Compare outputs section by section
        section_results = {}
        issues = []
        
        # Define expected outputs for each section
        expected_outputs = self._define_expected_outputs()
        
        for section_id, expectations in expected_outputs.items():
            result = self._validate_section(
                section_id=section_id,
                expectations=expectations,
                student_outputs=student_outputs,
                solution_outputs=self.solution_outputs
            )
            section_results[section_id] = result
            
            if not result['passed']:
                issues.extend(result['issues'])
        
        # Calculate overall match percentage
        total_checks = sum(len(r['checks']) for r in section_results.values())
        passed_checks = sum(sum(1 for c in r['checks'] if c['passed']) for r in section_results.values())
        overall_match = passed_checks / total_checks if total_checks > 0 else 0
        
        # Calculate score adjustment
        score_adjustment = self._calculate_score_adjustment(overall_match, issues)
        
        return {
            'overall_match': overall_match,
            'section_results': section_results,
            'issues': issues,
            'score_adjustment': score_adjustment,
            'total_checks': total_checks,
            'passed_checks': passed_checks
        }
    
    def _extract_outputs(self, notebook: Dict) -> Dict[int, List[str]]:
        """Extract text outputs from all cells"""
        outputs = {}
        
        for idx, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                cell_outputs = []
                for output in cell.get('outputs', []):
                    # Extract text from different output types
                    if 'text' in output:
                        cell_outputs.append(''.join(output['text']))
                    elif 'data' in output:
                        if 'text/plain' in output['data']:
                            cell_outputs.append(''.join(output['data']['text/plain']))
                
                if cell_outputs:
                    outputs[idx] = cell_outputs
        
        return outputs
    
    def _define_expected_outputs(self) -> Dict[str, Dict]:
        """
        Define what to check for each section
        """
        return {
            'part1_data_import': {
                'description': 'Data import and dimensions',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'customers',
                        'expected': 100,
                        'tolerance': 0
                    },
                    {
                        'type': 'row_count',
                        'variable': 'orders',
                        'expected': 250,
                        'tolerance': 0
                    },
                    {
                        'type': 'row_count',
                        'variable': 'order_items',
                        'expected': 400,
                        'tolerance': 0
                    },
                    {
                        'type': 'row_count',
                        'variable': 'products',
                        'expected': 50,
                        'tolerance': 0
                    },
                    {
                        'type': 'row_count',
                        'variable': 'suppliers',
                        'expected': 10,
                        'tolerance': 0
                    }
                ]
            },
            'part2_inner_join': {
                'description': 'Inner join results',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'customer_orders',
                        'expected': 200,
                        'tolerance': 5
                    }
                ]
            },
            'part2_left_join': {
                'description': 'Left join results',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'customer_orders_left',
                        'expected': 200,
                        'tolerance': 5
                    },
                    {
                        'type': 'count_value',
                        'description': 'customers without orders',
                        'expected': 0,
                        'tolerance': 2
                    }
                ]
            },
            'part2_right_join': {
                'description': 'Right join results',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'customer_orders_right',
                        'expected': 250,
                        'tolerance': 5
                    },
                    {
                        'type': 'count_value',
                        'description': 'orders with invalid customers',
                        'expected': 50,
                        'tolerance': 5
                    }
                ]
            },
            'part2_full_join': {
                'description': 'Full join results',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'customer_orders_full',
                        'expected': 250,
                        'tolerance': 5
                    }
                ]
            },
            'part3_multi_table': {
                'description': 'Multi-table join progression',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'orders_items',
                        'expected': 400,
                        'tolerance': 5
                    },
                    {
                        'type': 'row_count',
                        'variable': 'orders_customers_items',
                        'expected': 310,
                        'tolerance': 10
                    },
                    {
                        'type': 'row_count',
                        'variable': 'complete_order_data',
                        'expected': 310,
                        'tolerance': 10
                    },
                    {
                        'type': 'row_count',
                        'variable': 'complete_data',
                        'expected': 310,
                        'tolerance': 10
                    }
                ]
            },
            'part4_data_quality': {
                'description': 'Data quality analysis',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'customers_no_orders',
                        'expected': 0,
                        'tolerance': 2
                    },
                    {
                        'type': 'row_count',
                        'variable': 'orphaned_orders',
                        'expected': 50,
                        'tolerance': 5
                    },
                    {
                        'type': 'row_count',
                        'variable': 'products_never_ordered',
                        'expected': 0,
                        'tolerance': 2
                    },
                    {
                        'type': 'row_count',
                        'variable': 'active_customers',
                        'expected': 100,
                        'tolerance': 5
                    }
                ]
            },
            'part5_customer_metrics': {
                'description': 'Customer metrics analysis',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'customer_metrics',
                        'expected': 94,
                        'tolerance': 10
                    },
                    {
                        'type': 'numerical_value',
                        'description': 'top customer total spent',
                        'expected': 8471.51,
                        'tolerance_percent': 5
                    }
                ]
            },
            'part5_product_metrics': {
                'description': 'Product metrics analysis',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'product_metrics',
                        'expected': 50,
                        'tolerance': 5
                    },
                    {
                        'type': 'numerical_value',
                        'description': 'top product revenue',
                        'expected': 11763.16,
                        'tolerance_percent': 5
                    }
                ]
            },
            'part5_supplier_metrics': {
                'description': 'Supplier metrics analysis',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'supplier_metrics',
                        'expected': 10,
                        'tolerance': 0
                    },
                    {
                        'type': 'numerical_value',
                        'description': 'max products per supplier',
                        'expected': 10,
                        'tolerance_percent': 0
                    }
                ]
            },
            'part5_regional_analysis': {
                'description': 'Regional analysis',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'regional_analysis',
                        'expected': 5,
                        'tolerance': 0
                    },
                    {
                        'type': 'numerical_value',
                        'description': 'highest city sales',
                        'expected': 72277.52,
                        'tolerance_percent': 5
                    }
                ]
            },
            'part6_top_customers': {
                'description': 'Top 10% customers',
                'checks': [
                    {
                        'type': 'row_count',
                        'variable': 'top_customers',
                        'expected': 10,
                        'tolerance': 2
                    },
                    {
                        'type': 'numerical_value',
                        'description': 'top 10% threshold',
                        'expected': 4931.51,
                        'tolerance_percent': 5
                    }
                ]
            }
        }
    
    def _validate_section(
        self,
        section_id: str,
        expectations: Dict,
        student_outputs: Dict,
        solution_outputs: Dict
    ) -> Dict:
        """Validate a single section"""
        
        checks = []
        issues = []
        
        for check in expectations['checks']:
            check_result = self._perform_check(check, student_outputs)
            checks.append(check_result)
            
            if not check_result['passed']:
                issues.append({
                    'section': section_id,
                    'check': check,
                    'result': check_result
                })
        
        passed = all(c['passed'] for c in checks)
        
        return {
            'description': expectations['description'],
            'passed': passed,
            'checks': checks,
            'issues': issues
        }
    
    def _perform_check(self, check: Dict, student_outputs: Dict) -> Dict:
        """Perform a single check"""
        
        check_type = check['type']
        
        if check_type == 'row_count':
            return self._check_row_count(check, student_outputs)
        elif check_type == 'count_value':
            return self._check_count_value(check, student_outputs)
        elif check_type == 'numerical_value':
            return self._check_numerical_value(check, student_outputs)
        else:
            return {
                'passed': False,
                'message': f"Unknown check type: {check_type}"
            }
    
    def _check_row_count(self, check: Dict, student_outputs: Dict) -> Dict:
        """Check if row count matches expected value"""
        
        variable = check['variable']
        expected = check['expected']
        tolerance = check.get('tolerance', self.row_count_tolerance)
        
        # Search for row count in outputs
        found_value = None
        for cell_outputs in student_outputs.values():
            for output in cell_outputs:
                # Look for patterns like "310 rows" or "nrow: 310" or "Rows: 310"
                patterns = [
                    # Generic patterns
                    rf'Rows:\s*(\d+)',  # "Rows: 310"
                    rf'(\d+)\s*rows',   # "310 rows"
                    rf'(\d+)\s*x\s*\d+',  # "310 x 15"
                    
                    # Variable-specific patterns
                    rf'{variable}.*?(\d+)\s*rows',
                    rf'nrow.*?{variable}.*?(\d+)',
                    rf'{variable}.*?(\d+)\s*x\s*\d+',
                    
                    # Step patterns
                    rf'Step \d+ - .*?(\d+)\s*rows',
                    rf'Step \d+ - Add .*?(\d+)\s*rows',
                    
                    # Result patterns
                    rf'Inner Join Result:\s*(\d+)',
                    rf'Total rows:\s*(\d+)',
                    rf'Result:\s*(\d+)\s*rows',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, output, re.IGNORECASE)
                    if match:
                        found_value = int(match.group(1))
                        break
                
                if found_value is not None:
                    break
            
            if found_value is not None:
                break
        
        if found_value is None:
            return {
                'passed': False,
                'message': f"Could not find row count for {variable}",
                'expected': expected,
                'found': None
            }
        
        # Check if within tolerance
        diff = abs(found_value - expected)
        passed = diff <= tolerance
        
        return {
            'passed': passed,
            'message': f"{variable}: {found_value} rows (expected {expected} ±{tolerance})",
            'expected': expected,
            'found': found_value,
            'difference': diff,
            'tolerance': tolerance
        }
    
    def _check_count_value(self, check: Dict, student_outputs: Dict) -> Dict:
        """Check a count value (like 'customers without orders: 0')"""
        
        description = check['description']
        expected = check['expected']
        tolerance = check.get('tolerance', 2)
        
        # Search for the count in outputs
        found_value = None
        for cell_outputs in student_outputs.values():
            for output in cell_outputs:
                # Look for patterns - try multiple variations
                patterns = [
                    rf'{description}.*?(\d+)',
                    rf'{description}:\s*(\d+)',
                    # Handle variations like "Customers with No Orders: 0"
                    rf'Customers with No Orders:\s*(\d+)',
                    rf'Customers without orders:\s*(\d+)',
                    rf'Orders with invalid customer IDs:\s*(\d+)',
                    rf'Orders without valid customers:\s*(\d+)',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, output, re.IGNORECASE)
                    if match:
                        found_value = int(match.group(1))
                        break
                
                if found_value is not None:
                    break
            
            if found_value is not None:
                break
        
        if found_value is None:
            return {
                'passed': False,
                'message': f"Could not find count for '{description}'",
                'expected': expected,
                'found': None
            }
        
        # Check if within tolerance
        diff = abs(found_value - expected)
        passed = diff <= tolerance
        
        return {
            'passed': passed,
            'message': f"{description}: {found_value} (expected {expected} ±{tolerance})",
            'expected': expected,
            'found': found_value,
            'difference': diff,
            'tolerance': tolerance
        }
    
    def _check_numerical_value(self, check: Dict, student_outputs: Dict) -> Dict:
        """Check a numerical value (like revenue, threshold, etc.)"""
        
        description = check['description']
        expected = check['expected']
        tolerance_percent = check.get('tolerance_percent', self.numerical_tolerance * 100)
        
        # Search for the value in outputs
        found_value = None
        for cell_outputs in student_outputs.values():
            for output in cell_outputs:
                # Look for patterns like "top customer total spent: $ 8471.51"
                patterns = [
                    rf'{description}.*?\$?\s*([\d,]+\.?\d*)',
                    rf'{description}.*?(\d+\.?\d*)',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, output, re.IGNORECASE)
                    if match:
                        value_str = match.group(1).replace(',', '')
                        try:
                            found_value = float(value_str)
                            break
                        except ValueError:
                            continue
                
                if found_value is not None:
                    break
            
            if found_value is not None:
                break
        
        if found_value is None:
            return {
                'passed': False,
                'message': f"Could not find value for '{description}'",
                'expected': expected,
                'found': None
            }
        
        # Check if within tolerance percentage
        tolerance_amount = expected * (tolerance_percent / 100)
        diff = abs(found_value - expected)
        passed = diff <= tolerance_amount
        
        return {
            'passed': passed,
            'message': f"{description}: {found_value:.2f} (expected {expected:.2f} ±{tolerance_percent}%)",
            'expected': expected,
            'found': found_value,
            'difference': diff,
            'tolerance_percent': tolerance_percent
        }
    
    def _calculate_score_adjustment(self, overall_match: float, issues: List[Dict]) -> int:
        """
        Calculate score adjustment based on output validation
        
        Returns negative number (points to deduct)
        """
        if overall_match >= 0.95:
            return 0  # Perfect or near-perfect
        elif overall_match >= 0.90:
            return -2  # Minor issues
        elif overall_match >= 0.80:
            return -5  # Some issues
        elif overall_match >= 0.70:
            return -10  # Significant issues
        else:
            return -15  # Major issues
    
    def generate_report(self, validation_result: Dict) -> str:
        """Generate a detailed report"""
        
        report = []
        report.append("=" * 80)
        report.append("OUTPUT VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall results
        overall_match = validation_result['overall_match']
        report.append(f"Overall Match: {overall_match*100:.1f}%")
        report.append(f"Checks Passed: {validation_result['passed_checks']}/{validation_result['total_checks']}")
        report.append(f"Score Adjustment: {validation_result['score_adjustment']} points")
        report.append("")
        
        # Section-by-section results
        report.append("=" * 80)
        report.append("SECTION RESULTS")
        report.append("=" * 80)
        report.append("")
        
        for section_id, result in validation_result['section_results'].items():
            status = "✅" if result['passed'] else "❌"
            report.append(f"{status} {section_id}: {result['description']}")
            
            for check in result['checks']:
                check_status = "  ✅" if check['passed'] else "  ❌"
                report.append(f"{check_status} {check['message']}")
            
            report.append("")
        
        # Issues summary
        if validation_result['issues']:
            report.append("=" * 80)
            report.append("ISSUES FOUND")
            report.append("=" * 80)
            report.append("")
            
            for issue in validation_result['issues']:
                report.append(f"Section: {issue['section']}")
                report.append(f"  Expected: {issue['result']['expected']}")
                report.append(f"  Found: {issue['result']['found']}")
                report.append(f"  Message: {issue['result']['message']}")
                report.append("")
        
        return "\n".join(report)


def validate_outputs(
    student_notebook_path: str,
    solution_notebook_path: str,
    numerical_tolerance: float = 0.05,
    row_count_tolerance: int = 5
) -> Dict:
    """
    Convenience function to validate outputs
    """
    validator = OutputValidator(
        solution_notebook_path=solution_notebook_path,
        numerical_tolerance=numerical_tolerance,
        row_count_tolerance=row_count_tolerance
    )
    
    result = validator.validate_student_outputs(student_notebook_path)
    
    return result


if __name__ == "__main__":
    # Test with Kathryn's submission
    validator = OutputValidator(
        solution_notebook_path="data/solutions/assignment_6_solution.ipynb"
    )
    
    result = validator.validate_student_outputs(
        "submissions/12/Emerickkathrynj_emerickkathrynj.ipynb"
    )
    
    report = validator.generate_report(result)
    print(report)
