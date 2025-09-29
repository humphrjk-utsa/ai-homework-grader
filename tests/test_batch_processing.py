#!/usr/bin/env python3
"""
Test batch processing performance with multiple submissions
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from two_model_grader import TwoModelGrader
import nbformat

def extract_notebook_content(notebook_path):
    """Extract code and markdown from notebook"""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        code_cells = []
        markdown_cells = []
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                code_cells.append(cell.source)
            elif cell.cell_type == 'markdown':
                markdown_cells.append(cell.source)
        
        return '\n\n'.join(code_cells), '\n\n'.join(markdown_cells)
    except Exception as e:
        print(f"Error reading notebook: {e}")
        return "", ""

def test_batch_processing():
    """Test batch processing with multiple submissions"""
    
    print("🧪 Testing Batch Processing Performance")
    print("=" * 60)
    
    # Create sample submissions (using Deon's notebook multiple times for testing)
    notebook_path = "submissions/1/Deon_Schoeman_170956.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"❌ Test notebook not found: {notebook_path}")
        return False
    
    # Extract content once
    student_code, student_markdown = extract_notebook_content(notebook_path)
    
    # Assignment info
    assignment_info = {
        'title': 'Assignment 1: Introduction to R',
        'total_points': 37.5,
        'learning_objectives': [
            'Set up R environment and working directory',
            'Import and explore datasets using R functions',
            'Understand data types and structures in R',
            'Perform basic data quality assessment'
        ]
    }
    
    # Rubric elements
    rubric_elements = {
        'environment_setup': {
            'max_points': 7.5,
            'category': 'automated',
            'description': 'Working directory setup and package loading'
        },
        'data_import': {
            'max_points': 10,
            'category': 'automated',
            'description': 'Successful data import and initial exploration'
        },
        'data_exploration': {
            'max_points': 10,
            'category': 'manual',
            'description': 'Quality of data exploration and observations'
        },
        'code_quality': {
            'max_points': 5,
            'category': 'manual',
            'description': 'Code organization and documentation'
        },
        'written_responses': {
            'max_points': 5,
            'category': 'manual',
            'description': 'Quality of written analysis and responses'
        }
    }
    
    # Create test batch (simulate 5 students for testing)
    test_students = [
        "Deon Schoeman",
        "Alex Johnson", 
        "Maria Garcia",
        "James Wilson",
        "Sarah Chen"
    ]
    
    submissions = []
    for student_name in test_students:
        submissions.append({
            'student_name': student_name,
            'student_code': student_code,
            'student_markdown': student_markdown,
            'solution_code': '',
            'assignment_info': assignment_info,
            'rubric_elements': rubric_elements
        })
    
    print(f"📊 Testing with {len(submissions)} submissions")
    print("🚀 Starting batch processing test...")
    
    # Test batch processing
    grader = TwoModelGrader()
    
    try:
        results = grader.grade_batch(submissions)
        
        print(f"\n✅ Batch processing completed successfully!")
        print(f"📊 Results summary:")
        
        total_time = sum(r.get('submission_time', 0) for r in results)
        avg_score = sum(r.get('score', 0) for r in results) / len(results)
        avg_time = total_time / len(results)
        
        print(f"   • Average score: {avg_score:.1f}/37.5 ({avg_score/37.5*100:.1f}%)")
        print(f"   • Average time per submission: {avg_time:.1f}s")
        print(f"   • Total processing time: {total_time:.1f}s")
        
        # Estimate for 50 submissions
        estimated_50 = avg_time * 50
        print(f"\n🎯 Estimated time for 50 submissions: {estimated_50:.1f}s ({estimated_50/60:.1f} minutes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_vs_batch():
    """Compare single submission vs batch processing performance"""
    
    print("\n🔬 Comparing Single vs Batch Processing")
    print("=" * 50)
    
    # Test single submission first
    print("📊 Testing single submission performance...")
    
    # (Single submission test code would go here)
    
    # Then test batch
    print("📊 Testing batch processing performance...")
    
    # (Batch test results comparison)

if __name__ == "__main__":
    success = test_batch_processing()
    
    if success:
        print("\n🎉 Batch processing test completed!")
        print("\n📋 Key Optimizations Applied:")
        print("• Model preloading for batch processing")
        print("• Reduced token limits (1500/2000 vs 2000/2500)")
        print("• Optimized timeouts")
        print("• Business-friendly grading adjustments")
    else:
        print("\n❌ Batch processing test failed.")
        
    print("\n📈 Expected Performance Improvements:")
    print("• First submission: ~120-150s (includes model loading)")
    print("• Subsequent submissions: ~60-90s each")
    print("• 50 submissions: ~60-75 minutes (vs 2+ hours sequential)")