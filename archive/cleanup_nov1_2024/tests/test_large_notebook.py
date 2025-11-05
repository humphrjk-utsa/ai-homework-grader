#!/usr/bin/env python3
"""
Test that large notebooks are handled properly
"""
import os

# Check the problematic notebook
problem_notebook = "desantiagopalomaressalinasalejandro_21935_11607677_Submit 3 - Homework 3 - Alejandro De Santiago Palomares Salinas.ipynb"
success_notebook = "schoemandeon_LATE_170956_11694321_Schoeman_Deon_homework_lesson_3_data_transformation-1.ipynb"

if os.path.exists(problem_notebook):
    size_kb = os.path.getsize(problem_notebook) / 1024
    size_mb = os.path.getsize(problem_notebook) / (1024 * 1024)
    print(f"Problem notebook: {size_kb:.1f} KB ({size_mb:.2f} MB)")
    
    if size_kb > 200:
        print(f"✅ This notebook WILL skip output comparison (> 200KB threshold)")
    else:
        print(f"❌ This notebook will attempt output comparison")

if os.path.exists(success_notebook):
    size_kb = os.path.getsize(success_notebook) / 1024
    size_mb = os.path.getsize(success_notebook) / (1024 * 1024)
    print(f"\nSuccess notebook: {size_kb:.1f} KB ({size_mb:.2f} MB)")
    
    if size_kb > 200:
        print(f"⚠️ This notebook will skip output comparison (> 200KB threshold)")
    else:
        print(f"✅ This notebook will run output comparison normally")
