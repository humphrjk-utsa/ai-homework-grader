import re
import json

class LanguageDetector:
    """Detect programming language from notebook content"""
    
    @staticmethod
    def detect_language_from_notebook(notebook_path):
        """Detect the primary language used in a notebook"""
        try:
            import nbformat
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            code_content = ""
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    code_content += cell.source + "\n"
            
            return LanguageDetector.detect_language_from_code(code_content)
            
        except Exception:
            return "Unknown"
    
    @staticmethod
    def detect_language_from_code(code_content):
        """Detect language from code content"""
        code_lower = code_content.lower()
        
        # R language indicators
        r_indicators = [
            'library(', 'install.packages(', '<-', 'data.frame(',
            'ggplot(', 'dplyr::', 'tidyr::', 'str(', 'summary(',
            'head(', 'tail(', 'nrow(', 'ncol(', 'colnames(',
            'read.csv(', 'write.csv(', '%>%', 'mutate(', 'filter(',
            'select(', 'arrange(', 'group_by(', 'summarise('
        ]
        
        # SQL indicators
        sql_indicators = [
            'select ', 'from ', 'where ', 'join ', 'inner join',
            'left join', 'right join', 'group by', 'order by',
            'having ', 'insert into', 'update ', 'delete from',
            'create table', 'alter table', 'drop table',
            'union ', 'distinct ', 'count(', 'sum(', 'avg(',
            'max(', 'min('
        ]
        
        # Python indicators
        python_indicators = [
            'import ', 'from ', 'def ', 'class ', 'if __name__',
            'print(', 'len(', 'range(', 'for ', 'while ',
            'pandas', 'numpy', 'matplotlib', 'seaborn',
            'sklearn', '.iloc', '.loc', '.head()', '.tail()'
        ]
        
        # Count indicators
        r_count = sum(1 for indicator in r_indicators if indicator in code_lower)
        sql_count = sum(1 for indicator in sql_indicators if indicator in code_lower)
        python_count = sum(1 for indicator in python_indicators if indicator in code_lower)
        
        # Determine language
        if r_count > sql_count and r_count > python_count:
            return "R"
        elif sql_count > r_count and sql_count > python_count:
            return "SQL"
        elif python_count > r_count and python_count > sql_count:
            return "Python"
        else:
            return "Mixed/Unknown"
    
    @staticmethod
    def get_language_specific_features(code_content, language):
        """Extract language-specific features"""
        features = {}
        
        if language == "R":
            features.update(LanguageDetector._get_r_features(code_content))
        elif language == "SQL":
            features.update(LanguageDetector._get_sql_features(code_content))
        elif language == "Python":
            features.update(LanguageDetector._get_python_features(code_content))
        
        return features
    
    @staticmethod
    def _get_r_features(code_content):
        """Extract R-specific features"""
        code_lower = code_content.lower()
        
        return {
            'uses_tidyverse': any(pkg in code_lower for pkg in ['dplyr', 'ggplot2', 'tidyr', '%>%']),
            'uses_base_r': any(func in code_lower for func in ['apply(', 'lapply(', 'sapply(']),
            'data_manipulation': any(func in code_lower for func in ['mutate(', 'filter(', 'select(']),
            'visualization': 'ggplot(' in code_lower or 'plot(' in code_lower,
            'statistical_functions': any(func in code_lower for func in ['lm(', 'glm(', 't.test(', 'cor(']),
            'data_import': any(func in code_lower for func in ['read.csv(', 'read.table(', 'read_csv(']),
            'assignment_operator_count': code_content.count('<-'),
            'pipe_operator_count': code_content.count('%>%')
        }
    
    @staticmethod
    def _get_sql_features(code_content):
        """Extract SQL-specific features"""
        code_lower = code_content.lower()
        
        return {
            'uses_joins': any(join in code_lower for join in ['join', 'inner join', 'left join', 'right join']),
            'uses_aggregation': any(func in code_lower for func in ['count(', 'sum(', 'avg(', 'max(', 'min(']),
            'uses_grouping': 'group by' in code_lower,
            'uses_ordering': 'order by' in code_lower,
            'uses_filtering': 'where' in code_lower,
            'uses_subqueries': code_lower.count('(select') > 0,
            'uses_unions': 'union' in code_lower,
            'ddl_operations': any(op in code_lower for op in ['create', 'alter', 'drop']),
            'dml_operations': any(op in code_lower for op in ['insert', 'update', 'delete']),
            'select_count': code_lower.count('select ')
        }
    
    @staticmethod
    def _get_python_features(code_content):
        """Extract Python-specific features"""
        code_lower = code_content.lower()
        
        return {
            'uses_pandas': 'pandas' in code_lower or '.iloc' in code_lower or '.loc' in code_lower,
            'uses_numpy': 'numpy' in code_lower or 'np.' in code_lower,
            'uses_matplotlib': 'matplotlib' in code_lower or 'plt.' in code_lower,
            'uses_sklearn': 'sklearn' in code_lower,
            'function_definitions': code_content.count('def '),
            'class_definitions': code_content.count('class '),
            'list_comprehensions': '[' in code_content and 'for' in code_content and 'in' in code_content,
            'exception_handling': 'try:' in code_lower or 'except' in code_lower
        }