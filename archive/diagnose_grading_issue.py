#!/usr/bin/env python3
"""
Diagnose why the web interface is using fallback grading instead of Business Analytics Grader
"""

import requests
import os
import sqlite3
import pandas as pd
import nbformat
from business_analytics_grader import BusinessAnalyticsGrader

def check_ollama_status():
    """Check if Ollama is running and models are available"""
    
    print("🔍 Checking Ollama Status...")
    
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama is running")
            
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            
            print(f"📚 Available models: {len(available_models)}")
            
            # Check our specific models
            code_model = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest"
            feedback_model = "gemma3:27b-it-q8_0"
            
            if code_model in available_models:
                print(f"✅ Code Analyzer: {code_model}")
            else:
                print(f"❌ Code Analyzer: {code_model} - NOT FOUND")
                print("   Available coding models:")
                for model in available_models:
                    if any(keyword in model.lower() for keyword in ['coder', 'code', 'qwen']):
                        print(f"     • {model}")
            
            if feedback_model in available_models:
                print(f"✅ Feedback Generator: {feedback_model}")
            else:
                print(f"❌ Feedback Generator: {feedback_model} - NOT FOUND")
                print("   Available feedback models:")
                for model in available_models:
                    if any(keyword in model.lower() for keyword in ['gemma', 'llama', 'mistral']):
                        print(f"     • {model}")
            
            return code_model in available_models and feedback_model in available_models
            
        else:
            print(f"❌ Ollama returned error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running or not accessible")
        print("💡 Start Ollama with: ollama serve")
        return False
    
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def test_business_grader():
    """Test if BusinessAnalyticsGrader can be initialized"""
    
    print("\n🤖 Testing Business Analytics Grader...")
    
    try:
        grader = BusinessAnalyticsGrader()
        print("✅ BusinessAnalyticsGrader initialized successfully")
        
        # Test connection check
        if grader.check_ollama_connection():
            print("✅ Ollama connection verified")
        else:
            print("❌ Ollama connection failed")
            return False
        
        # Test model availability check
        if grader.check_models_available():
            print("✅ Required models available")
            return True
        else:
            print("❌ Required models not available")
            return False
            
    except Exception as e:
        print(f"❌ BusinessAnalyticsGrader initialization failed: {e}")
        import traceback
        print(f"Details: {traceback.format_exc()}")
        return False

def test_sample_grading():
    """Test grading with a sample submission"""
    
    print("\n📝 Testing Sample Grading...")
    
    # Check if Logan's notebook exists
    notebook_path = "Balfour_Logan_homework_lesson_1.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"❌ Test notebook not found: {notebook_path}")
        return False
    
    print(f"✅ Test notebook found: {notebook_path}")
    
    try:
        # Initialize grader
        grader = BusinessAnalyticsGrader()
        
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Extract content
        student_code = ""
        student_markdown = ""
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                student_code += cell.source + "\n\n"
            elif cell.cell_type == 'markdown':
                student_markdown += cell.source + "\n\n"
        
        print(f"✅ Extracted {len(student_code)} chars of code")
        print(f"✅ Extracted {len(student_markdown)} chars of markdown")
        
        # Test grading
        assignment_info = {
            "title": "Test Assignment",
            "student_name": "Logan Balfour"
        }
        
        rubric_elements = {
            "technical_execution": {"weight": 0.25, "max_score": 37.5},
            "business_thinking": {"weight": 0.30, "max_score": 37.5},
            "data_analysis": {"weight": 0.25, "max_score": 37.5},
            "communication": {"weight": 0.20, "max_score": 37.5}
        }
        
        solution_code = '''
        library(tidyverse)
        library(readxl)
        sales_df <- read_csv("data/sales_data.csv")
        '''
        
        print("🚀 Starting test grading...")
        
        result = grader.grade_submission(
            student_code=student_code,
            student_markdown=student_markdown,
            solution_code=solution_code,
            assignment_info=assignment_info,
            rubric_elements=rubric_elements
        )
        
        if result:
            print("✅ Grading successful!")
            print(f"   Score: {result['final_score']}/37.5 ({result['final_score_percentage']:.1f}%)")
            print(f"   Method: {result.get('grading_method', 'Unknown')}")
            
            # Check if it used two models
            if 'grading_stats' in result:
                stats = result['grading_stats']
                print(f"   Code Analysis Time: {stats.get('code_analysis_time', 0):.1f}s")
                print(f"   Feedback Generation Time: {stats.get('feedback_generation_time', 0):.1f}s")
                print(f"   Parallel Efficiency: {stats.get('parallel_efficiency', 0):.1f}x")
            
            return True
        else:
            print("❌ Grading returned no result")
            return False
            
    except Exception as e:
        print(f"❌ Test grading failed: {e}")
        import traceback
        print(f"Details: {traceback.format_exc()}")
        return False

def check_database_setup():
    """Check if database is properly set up"""
    
    print("\n🗄️ Checking Database Setup...")
    
    db_path = "grading_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Check assignments
        assignments = pd.read_sql_query("SELECT * FROM assignments", conn)
        print(f"✅ Assignments: {len(assignments)} records")
        
        # Check students
        students = pd.read_sql_query("SELECT * FROM students", conn)
        print(f"✅ Students: {len(students)} records")
        
        # Check submissions
        submissions = pd.read_sql_query("SELECT * FROM submissions", conn)
        print(f"✅ Submissions: {len(submissions)} records")
        
        # Check for ungraded submissions
        ungraded = submissions[submissions['ai_score'].isna()]
        print(f"📝 Ungraded submissions: {len(ungraded)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    
    print("🔍 GRADING SYSTEM DIAGNOSTIC")
    print("=" * 50)
    
    # Check Ollama
    ollama_ok = check_ollama_status()
    
    # Check Business Grader
    grader_ok = test_business_grader()
    
    # Check Database
    db_ok = check_database_setup()
    
    # Test Sample Grading
    if ollama_ok and grader_ok:
        grading_ok = test_sample_grading()
    else:
        grading_ok = False
        print("\n❌ Skipping grading test due to previous failures")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    print(f"Ollama Status: {'✅ OK' if ollama_ok else '❌ FAILED'}")
    print(f"Business Grader: {'✅ OK' if grader_ok else '❌ FAILED'}")
    print(f"Database Setup: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"Sample Grading: {'✅ OK' if grading_ok else '❌ FAILED'}")
    
    if all([ollama_ok, grader_ok, db_ok, grading_ok]):
        print("\n🎉 ALL SYSTEMS WORKING!")
        print("   The web interface should use BusinessAnalyticsGrader")
        print("   If it's still using fallback, check for errors in the web interface logs")
    else:
        print("\n❌ ISSUES FOUND!")
        print("   Fix the failed components before using the web interface")
        
        if not ollama_ok:
            print("\n🔧 To fix Ollama:")
            print("   1. Start Ollama: ollama serve")
            print("   2. Download models: ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest")
            print("   3. Download models: ollama pull gemma3:27b-it-q8_0")

if __name__ == "__main__":
    main()