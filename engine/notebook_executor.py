#!/usr/bin/env python3
"""
Notebook Executor
Automatically executes student notebooks that haven't been run
Handles path injection and data folder setup
"""

import nbformat
from nbformat.v4 import new_code_cell, new_output
import os
import tempfile
import shutil
import re
import subprocess
import json
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotebookExecutor:
    """Execute student notebooks with path injection and timeout"""
    
    def __init__(self, data_folder: str = "data", timeout: int = 30):
        """
        Initialize notebook executor
        
        Args:
            data_folder: Path to folder containing assignment data files
            timeout: Maximum execution time in seconds (default 30)
        """
        self.data_folder = data_folder
        self.timeout = timeout
        
    def needs_execution(self, notebook_path: str) -> Tuple[bool, int, int]:
        """
        Check if notebook needs to be executed
        
        Returns:
            (needs_execution, total_cells, executed_cells)
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
            total_cells = len(code_cells)
            
            # Count cells that have been executed (have outputs or execution_count)
            executed_cells = 0
            for cell in code_cells:
                if cell.get('execution_count') is not None or cell.get('outputs'):
                    executed_cells += 1
            
            # Need execution if less than 50% of cells have been run
            needs_exec = executed_cells < (total_cells * 0.5)
            
            logger.info(f"Notebook analysis: {executed_cells}/{total_cells} cells executed")
            return needs_exec, total_cells, executed_cells
            
        except Exception as e:
            logger.error(f"Error analyzing notebook: {e}")
            return False, 0, 0
    
    def inject_paths(self, notebook_path: str, temp_dir: str) -> str:
        """
        Create a modified notebook with injected paths
        
        Args:
            notebook_path: Original notebook path
            temp_dir: Temporary directory for execution
            
        Returns:
            Path to modified notebook
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Inject setup cell at the beginning
            setup_code = f"""
# AUTO-INJECTED: Set working directory for grading
import os
os.chdir(r'{temp_dir}')
print(f"Working directory set to: {{os.getcwd()}}")
"""
            setup_cell = new_code_cell(source=setup_code)
            nb.cells.insert(0, setup_cell)
            
            # Modify cells with path issues
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    source = cell.source
                    
                    # Comment out setwd() calls
                    source = re.sub(
                        r'setwd\s*\([^)]+\)',
                        '# setwd() commented out for grading',
                        source,
                        flags=re.IGNORECASE
                    )
                    
                    # Replace file paths - extract just the filename
                    # This handles patterns like:
                    # "C:/Users/Name/Documents/data/file.csv" -> "file.csv"
                    # "/Users/Name/Documents/data/file.csv" -> "file.csv"
                    # "~/Documents/MSBA/data/file.csv" -> "file.csv"
                    
                    # Pattern 1: Windows absolute paths (C:/... or C:\...)
                    source = re.sub(
                        r'["\']([A-Za-z]:[/\\][^"\']*[/\\])([^/\\"\'\s]+\.(csv|xlsx|xls|txt|json|rds|rda|RData))["\']',
                        r'"\2"',
                        source,
                        flags=re.IGNORECASE
                    )
                    
                    # Pattern 2: Unix absolute paths (/Users/... or /home/...)
                    source = re.sub(
                        r'["\']([/\\](?:Users|home)[/\\][^"\']*[/\\])([^/\\"\'\s]+\.(csv|xlsx|xls|txt|json|rds|rda|RData))["\']',
                        r'"\2"',
                        source,
                        flags=re.IGNORECASE
                    )
                    
                    # Pattern 3: Home directory paths (~/...)
                    source = re.sub(
                        r'["\']~[/\\][^"\']*[/\\]([^/\\"\'\s]+\.(csv|xlsx|xls|txt|json|rds|rda|RData))["\']',
                        r'"\1"',
                        source,
                        flags=re.IGNORECASE
                    )
                    
                    # Pattern 4: Relative paths with multiple directories (../../data/file.csv -> file.csv)
                    source = re.sub(
                        r'["\'](?:\.\./)+[^"\']*[/\\]([^/\\"\'\s]+\.(csv|xlsx|xls|txt|json|rds|rda|RData))["\']',
                        r'"\1"',
                        source,
                        flags=re.IGNORECASE
                    )
                    
                    # Pattern 5: data/ or ./data/ prefixes (data/file.csv -> file.csv)
                    source = re.sub(
                        r'["\'](?:\./)?data[/\\]([^/\\"\'\s]+\.(csv|xlsx|xls|txt|json|rds|rda|RData))["\']',
                        r'"\1"',
                        source,
                        flags=re.IGNORECASE
                    )
                    
                    cell.source = source
            
            # Save modified notebook
            modified_path = os.path.join(temp_dir, 'modified_notebook.ipynb')
            with open(modified_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            
            logger.info(f"Created modified notebook with injected paths")
            return modified_path
            
        except Exception as e:
            logger.error(f"Error injecting paths: {e}")
            return notebook_path
    
    def setup_data_folder(self, temp_dir: str) -> bool:
        """
        Copy data files to temporary directory
        
        Args:
            temp_dir: Temporary directory for execution
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(self.data_folder):
                logger.warning(f"Data folder not found: {self.data_folder}")
                return False
            
            # Copy all data files to temp directory
            for item in os.listdir(self.data_folder):
                src = os.path.join(self.data_folder, item)
                dst = os.path.join(temp_dir, item)
                
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    logger.info(f"Copied data file: {item}")
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
                    logger.info(f"Copied data folder: {item}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up data folder: {e}")
            return False
    
    def execute_notebook(self, notebook_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Execute notebook with timeout and error handling
        
        Args:
            notebook_path: Path to notebook to execute
            
        Returns:
            (success, executed_notebook_path, error_message)
        """
        temp_dir = None
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='notebook_exec_')
            logger.info(f"Created temp directory: {temp_dir}")
            
            # Setup data folder
            self.setup_data_folder(temp_dir)
            
            # Inject paths
            modified_notebook = self.inject_paths(notebook_path, temp_dir)
            
            # Execute using nbconvert
            output_notebook = os.path.join(temp_dir, 'executed_notebook.ipynb')
            
            cmd = [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                '--ExecutePreprocessor.timeout=' + str(self.timeout),
                '--ExecutePreprocessor.kernel_name=ir',  # R kernel
                '--output', output_notebook,
                modified_notebook
            ]
            
            logger.info(f"Executing notebook with {self.timeout}s timeout...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 10  # Extra buffer for subprocess
            )
            
            if result.returncode == 0:
                logger.info("✅ Notebook executed successfully")
                
                # Copy executed notebook to original location
                executed_path = notebook_path.replace('.ipynb', '_executed.ipynb')
                shutil.copy2(output_notebook, executed_path)
                
                return True, executed_path, None
            else:
                error_msg = result.stderr or "Unknown execution error"
                logger.error(f"❌ Execution failed: {error_msg}")
                return False, None, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"Execution timeout ({self.timeout}s exceeded)"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Execution error: {error_msg}")
            return False, None, error_msg
            
        finally:
            # Cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temp directory")
                except:
                    pass
    
    def execute_if_needed(self, notebook_path: str) -> Tuple[str, Dict]:
        """
        Check if notebook needs execution and execute if necessary
        
        Args:
            notebook_path: Path to student notebook
            
        Returns:
            (notebook_to_use, execution_info)
        """
        needs_exec, total_cells, executed_cells = self.needs_execution(notebook_path)
        
        execution_info = {
            'needed_execution': needs_exec,
            'total_cells': total_cells,
            'executed_cells': executed_cells,
            'execution_attempted': False,
            'execution_success': False,
            'executed_notebook_path': None,
            'error_message': None
        }
        
        if not needs_exec:
            logger.info("Notebook already executed, using original")
            return notebook_path, execution_info
        
        logger.info(f"Notebook needs execution ({executed_cells}/{total_cells} cells run)")
        execution_info['execution_attempted'] = True
        
        success, executed_path, error_msg = self.execute_notebook(notebook_path)
        
        execution_info['execution_success'] = success
        execution_info['executed_notebook_path'] = executed_path
        execution_info['error_message'] = error_msg
        
        if success:
            logger.info(f"Using executed notebook: {executed_path}")
            return executed_path, execution_info
        else:
            logger.warning(f"Execution failed, using original notebook")
            return notebook_path, execution_info


def test_executor():
    """Test the notebook executor"""
    executor = NotebookExecutor(data_folder='data', timeout=30)
    
    # Test with a sample notebook
    test_notebook = 'submissions/2/Francisco_Guadarrama_178108.ipynb'
    
    if os.path.exists(test_notebook):
        print(f"Testing with: {test_notebook}")
        notebook_to_use, info = executor.execute_if_needed(test_notebook)
        
        print("\nExecution Info:")
        print(json.dumps(info, indent=2))
        print(f"\nNotebook to use for grading: {notebook_to_use}")
    else:
        print(f"Test notebook not found: {test_notebook}")


if __name__ == '__main__':
    test_executor()
