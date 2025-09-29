#!/usr/bin/env python3
"""
Test script for two-model grading system timing
Tests the bf16 Gemma model performance
"""

import time
import os
import sys
import json
import nbformat
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from two_model_grader import TwoModelGrader

def test_two_model_timing():
    """Test the two-model system timing with bf16 Gemma"""
    
    print("🎯 Two-Model System Timing Test")
    print("=" * 50)
    
    # Find a test submission
    submissions_dir = Path("submissions")
    test_notebooks = []
    
    if submissions_dir.exists():
        for assignment_dir in submissions_dir.iterdir():
            if assignment_dir.is_dir():
                for notebook in assignment_dir.glob("*.ipynb"):
                    test_notebooks.append(notebook)
                    break  # Just get one per assignment
    
    if not test_notebooks:
        print("❌ No test notebooks found in submissions directory")
        print("💡 Looking for any .ipynb files...")
        
        # Look for any notebook files
        for notebook in Path(".").rglob("*.ipynb"):
            if "homework" in str(notebook).lower() or "assignment" in str(notebook).lower():
                test_notebooks.append(notebook)
                break
    
    if not test_notebooks:
        print("❌ No suitable test notebooks found")
        return
    
    test_notebook = test_notebooks[0]
    print(f"📝 Test notebook: {test_notebook}")
    
    # Initialize two-model grader
    print("\n🚀 Initializing Two-Model System...")
    start_init = time.time()
    
    try:
        grader = TwoModelGrader()
        init_time = time.time() - start_init
        print(f"✅ Initialization complete: {init_time:.2f}s")
        
        # Show model configuration
        print(f"🔧 Code Analyzer: Qwen 3.0 Coder")
        print(f"📝 Feedback Generator: {grader.feedback_generator.feedback_model.model_name}")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Extract code and markdown from notebook
    print(f"\n📖 Extracting notebook content...")
    try:
        with open(test_notebook, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Extract code and markdown
        student_code = ""
        student_markdown = ""
        
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                student_code += cell.source + "\n\n"
            elif cell.cell_type == 'markdown':
                student_markdown += cell.source + "\n\n"
        
        print(f"📊 Extracted {len(student_code)} chars of code, {len(student_markdown)} chars of markdown")
        
    except Exception as e:
        print(f"❌ Failed to extract notebook content: {e}")
        return
    
    # Create minimal test data
    assignment_info = {
        "name": "Test Assignment",
        "description": "R programming assignment test",
        "total_points": 100
    }
    
    rubric_elements = {
        "code_quality": {"points": 40, "description": "Code functionality and correctness"},
        "analysis": {"points": 30, "description": "Data analysis and interpretation"},
        "presentation": {"points": 30, "description": "Clear explanations and formatting"}
    }
    
    solution_code = "# Reference solution\nlibrary(tidyverse)\ndata <- read.csv('data.csv')\nsummary(data)"
    
    # Run grading test
    print(f"\n⏱️  Starting grading test...")
    start_grading = time.time()
    
    try:
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        total_time = time.time() - start_grading
        
        print(f"\n✅ Grading Complete!")
        print("=" * 50)
        print(f"⏱️  Total Time: {total_time:.1f} seconds")
        print(f"📊 Final Score: {result.get('final_score', 'N/A'):.1f}%")
        
        # Performance analysis
        if total_time < 120:
            print("🚀 EXCELLENT: Under 2 minutes!")
        elif total_time < 180:
            print("✅ GOOD: Under 3 minutes")
        elif total_time < 240:
            print("⚠️  ACCEPTABLE: Under 4 minutes")
        else:
            print("🐌 SLOW: Over 4 minutes")
        
        # Show timing breakdown if available
        if hasattr(grader, 'last_timing'):
            timing = grader.last_timing
            print(f"\n📈 Timing Breakdown:")
            print(f"  Code Analysis: {timing.get('code_analysis_time', 'N/A'):.1f}s")
            print(f"  Feedback Generation: {timing.get('feedback_time', 'N/A'):.1f}s")
        
        # Show brief feedback sample
        feedback = result.get('detailed_feedback', '')
        if feedback:
            print(f"\n📝 Feedback Sample (first 200 chars):")
            print(f"   {feedback[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_two_model_timing()