"""
Assignment 6 Systematic Validator
Performs thorough, evidence-based grading by checking actual code and outputs
"""

import json
import re
from typing import Dict, List, Tuple, Any


class Assignment6SystematicValidator:
    """Systematic validator that checks actual code presence and outputs"""
    
    def __init__(self, rubric_path: str = "rubrics/assignment_6_rubric.json"):
        with open(rubric_path, 'r') as f:
            self.rubric = json.load(f)
        
        # Required variables from rubric
        self.required_variables = self.rubric['autograder_checks']['required_variables']
        
        # Section definitions with points
        self.sections = {
            "part1_import": {
                "name": "Part 1: Data Import",
                "points": 5,
                "vars": ["customers", "orders", "order_items", "products", "suppliers"],
                "functions": ["read_csv", "nrow", "ncol", "head"]
            },
            "part2_1_inner": {
                "name": "Part 2.1: Inner Join",
                "points": 3,
                "vars": ["customer_orders"],
                "functions": ["inner_join"]
            },
            "part2_2_left": {
                "name": "Part 2.2: Left Join",
                "points": 3,
                "vars": ["customer_orders_left"],
                "functions": ["left_join"]
            },
            "part2_3_right": {
                "name": "Part 2.3: Right Join",
                "points": 3,
                "vars": ["customer_orders_right"],
                "functions": ["right_join"]
            },
            "part2_4_full": {
                "name": "Part 2.4: Full Join",
                "points": 3,
                "vars": ["customer_orders_full"],
                "functions": ["full_join"]
            },
            "part3_1_orders_items": {
                "name": "Part 3.1: Orders + Items",
                "points": 2,
                "vars": ["orders_items"],
                "functions": ["inner_join"]
            },
            "part3_2_add_customers": {
                "name": "Part 3.2: Add Customers",
                "points": 2,
                "vars": ["orders_customers_items"],
                "functions": ["inner_join"]
            },
            "part3_3_add_products": {
                "name": "Part 3.3: Add Products",
                "points": 2,
                "vars": ["complete_order_data"],
                "functions": ["inner_join"]
            },
            "part3_4_add_suppliers": {
                "name": "Part 3.4: Add Suppliers",
                "points": 2,
                "vars": ["complete_data"],
                "functions": ["inner_join"]
            },
            "part4_1_customers_no_orders": {
                "name": "Part 4.1: Customers No Orders",
                "points": 2,
                "vars": ["customers_no_orders"],
                "functions": ["anti_join"]
            },
            "part4_2_orphaned_orders": {
                "name": "Part 4.2: Orphaned Orders",
                "points": 2,
                "vars": ["orphaned_orders"],
                "functions": ["anti_join"]
            },
            "part4_3_products_never_ordered": {
                "name": "Part 4.3: Products Never Ordered",
                "points": 2,
                "vars": ["products_never_ordered"],
                "functions": ["anti_join"]
            },
            "part4_4_active_customers": {
                "name": "Part 4.4: Active Customers",
                "points": 2,
                "vars": ["active_customers"],
                "functions": ["semi_join"]
            },
            "part5_1_customer_metrics": {
                "name": "Part 5.1: Customer Metrics",
                "points": 2,
                "vars": ["customer_metrics"],
                "functions": ["group_by", "summarise"]
            },
            "part5_2_product_metrics": {
                "name": "Part 5.2: Product Metrics",
                "points": 2,
                "vars": ["product_metrics"],
                "functions": ["group_by", "summarise"]
            },
            "part5_3_supplier_metrics": {
                "name": "Part 5.3: Supplier Metrics",
                "points": 2,
                "vars": ["supplier_metrics"],
                "functions": ["group_by", "summarise"]
            },
            "part5_4_regional_analysis": {
                "name": "Part 5.4: Regional Analysis",
                "points": 2,
                "vars": ["regional_analysis"],
                "functions": ["group_by", "summarise"]
            },
            "part6_1_top_customers": {
                "name": "Part 6.1: Top Customers",
                "points": 1,
                "vars": ["top_customers"],
                "functions": ["quantile", "filter"]
            },
            "part6_2_product_combinations": {
                "name": "Part 6.2: Product Combinations",
                "points": 1,
                "vars": ["product_combinations"],
                "functions": ["inner_join", "filter"]
            },
            "part6_3_critical_suppliers": {
                "name": "Part 6.3: Critical Suppliers",
                "points": 1,
                "vars": ["critical_suppliers"],
                "functions": ["arrange"]
            },
            "part6_4_market_expansion": {
                "name": "Part 6.4: Market Expansion",
                "points": 1,
                "vars": ["market_expansion"],
                "functions": ["filter", "arrange"]
            }
        }
    
    def validate_notebook(self, notebook_path: str) -> Dict[str, Any]:
        """
        Systematically validate a notebook
        Returns detailed scoring breakdown
        """
        with open(notebook_path, 'r') as f:
            notebook = json.load(f)
        
        # Extract all code
        all_code = self._extract_all_code(notebook)
        
        # Count cells and outputs
        cell_stats = self._count_cells_and_outputs(notebook)
        
        # Check required variables
        variable_check = self._check_required_variables(all_code)
        
        # Check each section
        section_scores = self._check_all_sections(all_code)
        
        # Calculate component scores
        technical_score = self._calculate_technical_score(cell_stats)
        join_score = self._calculate_join_score(section_scores)
        understanding_score = self._calculate_understanding_score(variable_check, section_scores)
        insights_score = self._calculate_insights_score(notebook)
        
        # Calculate final score
        final_score = technical_score + join_score + understanding_score + insights_score
        
        return {
            "final_score": final_score,
            "max_score": 100,
            "percentage": final_score,
            "grade": self._get_grade(final_score),
            "components": {
                "technical_execution": {
                    "score": technical_score,
                    "max": 40,
                    "details": cell_stats
                },
                "join_operations": {
                    "score": join_score,
                    "max": 40,
                    "details": section_scores
                },
                "data_understanding": {
                    "score": understanding_score,
                    "max": 10
                },
                "analysis_insights": {
                    "score": insights_score,
                    "max": 10
                }
            },
            "variable_check": variable_check,
            "section_breakdown": section_scores,
            "cell_stats": cell_stats
        }
    
    def _extract_all_code(self, notebook: Dict) -> str:
        """Extract all code from notebook"""
        all_code = ""
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                all_code += ''.join(cell['source']) + "\n"
        return all_code
    
    def _count_cells_and_outputs(self, notebook: Dict) -> Dict:
        """Count total cells and cells with outputs"""
        total_cells = 0
        cells_with_output = 0
        cells_without_output = []
        
        for idx, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                total_cells += 1
                has_output = len(cell.get('outputs', [])) > 0
                if has_output:
                    cells_with_output += 1
                else:
                    source_preview = ''.join(cell['source'])[:80].replace('\n', ' ')
                    cells_without_output.append({
                        'cell_num': idx + 1,
                        'preview': source_preview
                    })
        
        return {
            "total_cells": total_cells,
            "cells_with_output": cells_with_output,
            "cells_without_output": len(cells_without_output),
            "execution_rate": cells_with_output / total_cells if total_cells > 0 else 0,
            "unexecuted_cells": cells_without_output
        }
    
    def _check_required_variables(self, all_code: str) -> Dict:
        """Check if all required variables exist"""
        found_vars = {}
        missing_vars = []
        
        for var in self.required_variables:
            # Look for variable <- assignment
            pattern = rf'\b{re.escape(var)}\s*<-'
            if re.search(pattern, all_code):
                found_vars[var] = True
            else:
                found_vars[var] = False
                missing_vars.append(var)
        
        return {
            "total_required": len(self.required_variables),
            "found": sum(found_vars.values()),
            "missing": missing_vars,
            "all_found": len(missing_vars) == 0,
            "details": found_vars
        }
    
    def _check_all_sections(self, all_code: str) -> Dict:
        """Check each section for completion"""
        section_results = {}
        
        for section_id, section_info in self.sections.items():
            # Check if variables exist
            vars_found = all([
                re.search(rf'\b{re.escape(v)}\s*<-', all_code) 
                for v in section_info["vars"]
            ])
            
            # Check if functions used
            funcs_found = all([
                f in all_code 
                for f in section_info["functions"]
            ])
            
            # Determine completion status
            if vars_found and funcs_found:
                status = "complete"
                points_earned = section_info["points"]
            elif vars_found:
                status = "partial"
                points_earned = section_info["points"] * 0.5
            else:
                status = "incomplete"
                points_earned = 0
            
            section_results[section_id] = {
                "name": section_info["name"],
                "status": status,
                "points_possible": section_info["points"],
                "points_earned": points_earned,
                "vars_found": vars_found,
                "funcs_found": funcs_found,
                "variables": section_info["vars"],
                "functions": section_info["functions"]
            }
        
        return section_results
    
    def _calculate_technical_score(self, cell_stats: Dict) -> float:
        """Calculate technical execution score (40 points max)"""
        base_score = 40
        unexecuted_penalty = cell_stats["cells_without_output"] * 2
        score = max(0, base_score - unexecuted_penalty)
        return score
    
    def _calculate_join_score(self, section_scores: Dict) -> float:
        """Calculate join operations score (40 points max)"""
        # Sum up all section points (raw total is 45)
        total_earned = sum(s["points_earned"] for s in section_scores.values())
        # Scale to 40 points
        scaled_score = (total_earned / 45) * 40
        return scaled_score
    
    def _calculate_understanding_score(self, variable_check: Dict, section_scores: Dict) -> float:
        """Calculate data understanding score (10 points max)"""
        # Check if all 6 join types used
        join_types_used = {
            "inner_join": False,
            "left_join": False,
            "right_join": False,
            "full_join": False,
            "anti_join": False,
            "semi_join": False
        }
        
        # Check which sections are complete
        if section_scores.get("part2_1_inner", {}).get("status") == "complete":
            join_types_used["inner_join"] = True
        if section_scores.get("part2_2_left", {}).get("status") == "complete":
            join_types_used["left_join"] = True
        if section_scores.get("part2_3_right", {}).get("status") == "complete":
            join_types_used["right_join"] = True
        if section_scores.get("part2_4_full", {}).get("status") == "complete":
            join_types_used["full_join"] = True
        if section_scores.get("part4_1_customers_no_orders", {}).get("status") == "complete":
            join_types_used["anti_join"] = True
        if section_scores.get("part4_4_active_customers", {}).get("status") == "complete":
            join_types_used["semi_join"] = True
        
        # Score based on join types used
        join_types_count = sum(join_types_used.values())
        
        if join_types_count == 6:
            score = 9  # Excellent
        elif join_types_count >= 5:
            score = 8  # Very good
        elif join_types_count >= 4:
            score = 7  # Good
        elif join_types_count >= 3:
            score = 6  # Adequate
        else:
            score = 4  # Poor
        
        return score
    
    def _calculate_insights_score(self, notebook: Dict) -> float:
        """Calculate analysis insights score (10 points max)"""
        # Look for Part 7 summary section
        summary_text = ""
        for cell in notebook['cells']:
            if cell['cell_type'] == 'markdown':
                content = ''.join(cell['source'])
                if 'Part 7' in content or 'Summary' in content or 'Analysis Summary' in content:
                    # Get next few cells
                    idx = notebook['cells'].index(cell)
                    for i in range(idx, min(idx + 10, len(notebook['cells']))):
                        if notebook['cells'][i]['cell_type'] == 'markdown':
                            summary_text += ''.join(notebook['cells'][i]['source'])
        
        # Score based on content quality
        word_count = len(summary_text.split())
        
        # Check for key elements
        has_join_findings = any(word in summary_text.lower() for word in ['join', 'inner', 'left', 'right', 'full'])
        has_data_quality = any(word in summary_text.lower() for word in ['orphaned', 'missing', 'quality', 'integrity'])
        has_business_insights = any(word in summary_text.lower() for word in ['customer', 'product', 'supplier', 'revenue', 'sales'])
        has_recommendations = any(word in summary_text.lower() for word in ['recommend', 'suggest', 'should', 'strategy'])
        
        score = 5  # Base score
        
        if word_count > 300:
            score += 1
        if has_join_findings:
            score += 1
        if has_data_quality:
            score += 1
        if has_business_insights:
            score += 1
        if has_recommendations:
            score += 1
        
        return min(score, 10)
    
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
    
    def generate_detailed_report(self, validation_result: Dict) -> str:
        """Generate a detailed text report"""
        report = []
        report.append("=" * 80)
        report.append("SYSTEMATIC VALIDATION REPORT")
        report.append("=" * 80)
        
        # Overall score
        report.append(f"\nFINAL SCORE: {validation_result['final_score']:.1f}/100 ({validation_result['percentage']:.1f}%)")
        report.append(f"GRADE: {validation_result['grade']}")
        
        # Component breakdown
        report.append("\n" + "=" * 80)
        report.append("COMPONENT BREAKDOWN")
        report.append("=" * 80)
        
        for comp_name, comp_data in validation_result['components'].items():
            report.append(f"\n{comp_name.upper().replace('_', ' ')}: {comp_data['score']:.1f}/{comp_data['max']}")
        
        # Cell execution stats
        report.append("\n" + "=" * 80)
        report.append("CELL EXECUTION STATISTICS")
        report.append("=" * 80)
        stats = validation_result['cell_stats']
        report.append(f"Total code cells: {stats['total_cells']}")
        report.append(f"Cells with output: {stats['cells_with_output']}")
        report.append(f"Execution rate: {stats['execution_rate']*100:.1f}%")
        
        if stats['unexecuted_cells']:
            report.append(f"\nUnexecuted cells ({len(stats['unexecuted_cells'])}):")
            for cell in stats['unexecuted_cells'][:5]:  # Show first 5
                report.append(f"  Cell {cell['cell_num']}: {cell['preview']}")
        
        # Variable check
        report.append("\n" + "=" * 80)
        report.append("REQUIRED VARIABLES CHECK")
        report.append("=" * 80)
        var_check = validation_result['variable_check']
        report.append(f"Found: {var_check['found']}/{var_check['total_required']}")
        
        if var_check['missing']:
            report.append(f"\nMissing variables ({len(var_check['missing'])}):")
            for var in var_check['missing']:
                report.append(f"  ❌ {var}")
        else:
            report.append("\n✅ ALL REQUIRED VARIABLES FOUND!")
        
        # Section breakdown
        report.append("\n" + "=" * 80)
        report.append("SECTION-BY-SECTION BREAKDOWN")
        report.append("=" * 80)
        
        for section_id, section_data in validation_result['section_breakdown'].items():
            status_icon = "✅" if section_data['status'] == "complete" else "⚠️" if section_data['status'] == "partial" else "❌"
            report.append(f"\n{status_icon} {section_data['name']}: {section_data['points_earned']:.1f}/{section_data['points_possible']}")
            report.append(f"   Variables: {', '.join(section_data['variables'])} - {'✅' if section_data['vars_found'] else '❌'}")
            report.append(f"   Functions: {', '.join(section_data['functions'])} - {'✅' if section_data['funcs_found'] else '❌'}")
        
        return "\n".join(report)


def validate_student_submission(notebook_path: str, rubric_path: str = "rubrics/assignment_6_rubric.json") -> Dict:
    """
    Main validation function
    """
    validator = Assignment6SystematicValidator(rubric_path)
    result = validator.validate_notebook(notebook_path)
    return result


if __name__ == "__main__":
    # Test with Kathryn's submission
    result = validate_student_submission("submissions/12/Emerickkathrynj_emerickkathrynj.ipynb")
    
    validator = Assignment6SystematicValidator()
    report = validator.generate_detailed_report(result)
    print(report)
    
    print("\n" + "=" * 80)
    print(f"FINAL VERDICT: {result['percentage']:.1f}% - Grade {result['grade']}")
    print("=" * 80)
