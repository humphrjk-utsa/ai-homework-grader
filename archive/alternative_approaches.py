import streamlit as st
import json

class AlternativeApproachHandler:
    """Handle and evaluate alternative valid approaches to assignments"""
    
    @staticmethod
    def get_common_r_alternatives():
        """Common alternative approaches in R programming"""
        return {
            "data_manipulation": {
                "tidyverse_vs_base": {
                    "tidyverse": ["dplyr", "mutate(", "filter(", "select(", "%>%"],
                    "base_r": ["subset(", "transform(", "apply(", "lapply(", "$"],
                    "both_valid": True,
                    "grading_note": "Both tidyverse and base R approaches are acceptable"
                },
                "data_import": {
                    "readr": ["read_csv(", "read_tsv("],
                    "base_r": ["read.csv(", "read.table("],
                    "data_table": ["fread("],
                    "both_valid": True,
                    "grading_note": "Multiple data import methods are valid"
                }
            },
            "visualization": {
                "ggplot_vs_base": {
                    "ggplot2": ["ggplot(", "geom_", "aes("],
                    "base_plots": ["plot(", "hist(", "boxplot(", "barplot("],
                    "both_valid": True,
                    "grading_note": "Both ggplot2 and base R plotting are acceptable"
                }
            },
            "statistical_analysis": {
                "correlation_methods": {
                    "pearson": ["cor(", "cor.test("],
                    "spearman": ["method = 'spearman'"],
                    "kendall": ["method = 'kendall'"],
                    "both_valid": True,
                    "grading_note": "Different correlation methods may be appropriate"
                }
            }
        }
    
    @staticmethod
    def get_common_sql_alternatives():
        """Common alternative approaches in SQL"""
        return {
            "joins": {
                "explicit_vs_implicit": {
                    "explicit": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
                    "implicit": ["WHERE", "FROM table1, table2"],
                    "both_valid": True,
                    "grading_note": "Both explicit and implicit joins can be correct"
                }
            },
            "aggregation": {
                "grouping_approaches": {
                    "group_by_having": ["GROUP BY", "HAVING"],
                    "subqueries": ["SELECT", "FROM (SELECT"],
                    "window_functions": ["OVER(", "PARTITION BY"],
                    "both_valid": True,
                    "grading_note": "Multiple aggregation strategies are valid"
                }
            },
            "filtering": {
                "where_vs_having": {
                    "where_clause": ["WHERE"],
                    "having_clause": ["HAVING"],
                    "context_dependent": True,
                    "grading_note": "Choice depends on whether filtering before or after aggregation"
                }
            }
        }
    
    @staticmethod
    def analyze_approach_differences(student_code, solution_code, language="R"):
        """Analyze differences between student and solution approaches"""
        differences = []
        
        if language == "R":
            alternatives = AlternativeApproachHandler.get_common_r_alternatives()
        elif language == "SQL":
            alternatives = AlternativeApproachHandler.get_common_sql_alternatives()
        else:
            return []
        
        student_lower = student_code.lower()
        solution_lower = solution_code.lower()
        
        for category, methods in alternatives.items():
            for approach_type, details in methods.items():
                if isinstance(details, dict) and "both_valid" in details:
                    # Check which approach student used vs solution
                    student_approach = None
                    solution_approach = None
                    
                    for approach_name, keywords in details.items():
                        if approach_name in ["both_valid", "grading_note", "context_dependent"]:
                            continue
                        
                        if isinstance(keywords, list):
                            if any(keyword.lower() in student_lower for keyword in keywords):
                                student_approach = approach_name
                            if any(keyword.lower() in solution_lower for keyword in keywords):
                                solution_approach = approach_name
                    
                    if student_approach and solution_approach and student_approach != solution_approach:
                        differences.append({
                            "category": category,
                            "type": approach_type,
                            "student_approach": student_approach,
                            "solution_approach": solution_approach,
                            "is_valid": details.get("both_valid", False),
                            "note": details.get("grading_note", "")
                        })
        
        return differences
    
    @staticmethod
    def generate_alternative_approach_feedback(differences):
        """Generate feedback for alternative approaches"""
        if not differences:
            return "Student used similar approach to reference solution."
        
        feedback_parts = []
        
        for diff in differences:
            if diff["is_valid"]:
                feedback_parts.append(
                    f"✅ **{diff['category'].replace('_', ' ').title()}**: "
                    f"You used {diff['student_approach']} while the solution used {diff['solution_approach']}. "
                    f"{diff['note']}."
                )
            else:
                feedback_parts.append(
                    f"⚠️ **{diff['category'].replace('_', ' ').title()}**: "
                    f"Consider why the solution used {diff['solution_approach']} instead of {diff['student_approach']}. "
                    f"{diff['note']}."
                )
        
        return "\n\n".join(feedback_parts)
    
    @staticmethod
    def show_approach_flexibility_settings():
        """Interface for configuring approach flexibility"""
        st.subheader("🔄 Alternative Approach Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**R Programming Flexibility:**")
            
            tidyverse_flexibility = st.slider(
                "Tidyverse vs Base R Acceptance",
                min_value=0, max_value=100, value=90,
                help="How much to accept base R when tidyverse is shown in solution"
            )
            
            plotting_flexibility = st.slider(
                "ggplot2 vs Base Plotting Acceptance", 
                min_value=0, max_value=100, value=85,
                help="How much to accept base plots when ggplot2 is shown"
            )
            
            statistical_flexibility = st.slider(
                "Statistical Method Flexibility",
                min_value=0, max_value=100, value=95,
                help="Accept different valid statistical approaches"
            )
        
        with col2:
            st.markdown("**SQL Flexibility:**")
            
            join_flexibility = st.slider(
                "JOIN Syntax Flexibility",
                min_value=0, max_value=100, value=90,
                help="Accept different valid JOIN approaches"
            )
            
            aggregation_flexibility = st.slider(
                "Aggregation Method Flexibility",
                min_value=0, max_value=100, value=85,
                help="Accept different aggregation strategies"
            )
            
            query_structure_flexibility = st.slider(
                "Query Structure Flexibility",
                min_value=0, max_value=100, value=80,
                help="Accept different but valid query structures"
            )
        
        # Save settings
        if st.button("💾 Save Flexibility Settings"):
            settings = {
                "r_settings": {
                    "tidyverse_flexibility": tidyverse_flexibility,
                    "plotting_flexibility": plotting_flexibility,
                    "statistical_flexibility": statistical_flexibility
                },
                "sql_settings": {
                    "join_flexibility": join_flexibility,
                    "aggregation_flexibility": aggregation_flexibility,
                    "query_structure_flexibility": query_structure_flexibility
                }
            }
            
            # Save to session state or file
            if hasattr(st, 'session_state'):
                st.session_state['approach_flexibility'] = settings
            
            st.success("✅ Flexibility settings saved!")
            
        return {
            "r_settings": {
                "tidyverse_flexibility": tidyverse_flexibility,
                "plotting_flexibility": plotting_flexibility,
                "statistical_flexibility": statistical_flexibility
            },
            "sql_settings": {
                "join_flexibility": join_flexibility,
                "aggregation_flexibility": aggregation_flexibility,
                "query_structure_flexibility": query_structure_flexibility
            }
        }
    
    @staticmethod
    def create_approach_examples():
        """Show examples of valid alternative approaches"""
        st.subheader("📚 Valid Alternative Approaches")
        
        tab1, tab2 = st.tabs(["R Examples", "SQL Examples"])
        
        with tab1:
            st.markdown("### R Programming Alternatives")
            
            with st.expander("Data Manipulation: Tidyverse vs Base R"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Tidyverse Approach:**")
                    st.code("""
library(dplyr)
result <- data %>%
  filter(age > 25) %>%
  select(name, age, salary) %>%
  mutate(salary_k = salary / 1000)
                    """, language="r")
                
                with col2:
                    st.markdown("**Base R Approach:**")
                    st.code("""
# Filter and select
filtered_data <- data[data$age > 25, c("name", "age", "salary")]
# Add new column
filtered_data$salary_k <- filtered_data$salary / 1000
result <- filtered_data
                    """, language="r")
                
                st.success("✅ Both approaches are valid and should receive full credit")
            
            with st.expander("Visualization: ggplot2 vs Base R"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**ggplot2 Approach:**")
                    st.code("""
library(ggplot2)
ggplot(data, aes(x = age, y = salary)) +
  geom_point() +
  labs(title = "Age vs Salary")
                    """, language="r")
                
                with col2:
                    st.markdown("**Base R Approach:**")
                    st.code("""
plot(data$age, data$salary,
     main = "Age vs Salary",
     xlab = "Age", ylab = "Salary")
                    """, language="r")
                
                st.success("✅ Both create valid visualizations")
        
        with tab2:
            st.markdown("### SQL Alternatives")
            
            with st.expander("JOIN Approaches"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Explicit JOIN:**")
                    st.code("""
SELECT e.name, d.department_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.id
WHERE e.salary > 50000;
                    """, language="sql")
                
                with col2:
                    st.markdown("**Implicit JOIN:**")
                    st.code("""
SELECT e.name, d.department_name
FROM employees e, departments d
WHERE e.dept_id = d.id
  AND e.salary > 50000;
                    """, language="sql")
                
                st.success("✅ Both JOIN methods are valid")
            
            with st.expander("Aggregation Strategies"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**GROUP BY Approach:**")
                    st.code("""
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 60000;
                    """, language="sql")
                
                with col2:
                    st.markdown("**Subquery Approach:**")
                    st.code("""
SELECT department, avg_salary
FROM (
  SELECT department, AVG(salary) as avg_salary
  FROM employees
  GROUP BY department
) dept_avg
WHERE avg_salary > 60000;
                    """, language="sql")
                
                st.success("✅ Both aggregation methods work correctly")