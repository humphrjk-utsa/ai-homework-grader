#!/usr/bin/env python3
"""
Test script for hybrid grading pipeline
Tests each component separately and together
"""

import sys
from pathlib import Path
from validators.hybrid_grading_pipeline import HybridGradingPipeline


def test_systematic_validator():
    """Test Step 1: Systematic Validator"""
    print("\n" + "="*80)
    print("TEST 1: SYSTEMATIC VALIDATOR (Deterministic)")
    print("="*80)
    
    from validators.assignment_6_systematic_validator import Assignment6SystematicValidator
    
    validator = Assignment6SystematicValidator()
    result = validator.validate_notebook("submissions/12/Emerickkathrynj_emerickkathrynj.ipynb")
    
    print(f"✅ Score: {result['final_score']:.1f}/100")
    print(f"✅ Grade: {result['grade']}")
    print(f"✅ Variables: {result['variable_check']['found']}/25")
    print(f"✅ Sections: {sum(1 for s in result['section_breakdown'].values() if s['status'] == 'complete')}/21")
    
    return result


def test_qwen_connection():
    """Test Step 2: Qwen Coder Connection"""
    print("\n" + "="*80)
    print("TEST 2: QWEN CODER CONNECTION")
    print("="*80)
    
    import requests
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:latest",
                "prompt": "Write a simple R function to add two numbers",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Qwen Coder is responding")
            print(f"✅ Response preview: {result.get('response', '')[:200]}...")
            return True
        else:
            print(f"❌ Qwen returned status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at http://localhost:11434")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_gpt_connection():
    """Test Step 3: GPT-OSS Connection"""
    print("\n" + "="*80)
    print("TEST 3: GPT-OSS-120B CONNECTION")
    print("="*80)
    
    import requests
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gpt-oss-120b:latest",
                "prompt": "Write encouraging feedback for a student who scored 91%",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ GPT-OSS-120B is responding")
            print(f"✅ Response preview: {result.get('response', '')[:200]}...")
            return True
        else:
            print(f"❌ GPT-OSS returned status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at http://localhost:11434")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_full_pipeline():
    """Test Full Pipeline"""
    print("\n" + "="*80)
    print("TEST 4: FULL HYBRID PIPELINE")
    print("="*80)
    
    pipeline = HybridGradingPipeline()
    
    try:
        result = pipeline.grade_submission("submissions/12/Emerickkathrynj_emerickkathrynj.ipynb")
        
        print("\n✅ PIPELINE COMPLETE!")
        print(f"   Objective Score: {result['objective_score']:.1f}/100")
        print(f"   Grade: {result['grade']}")
        print(f"   Code Evaluation: {len(result['code_evaluation']['raw_response'])} chars")
        print(f"   Narrative Feedback: {len(result['narrative_feedback']['raw_response'])} chars")
        
        return result
    
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("HYBRID GRADING PIPELINE - TEST SUITE")
    print("="*80)
    
    # Test 1: Systematic Validator (always works, no dependencies)
    try:
        validation_result = test_systematic_validator()
        test1_pass = True
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        test1_pass = False
    
    # Test 2: Qwen Connection
    test2_pass = test_qwen_connection()
    
    # Test 3: GPT-OSS Connection
    test3_pass = test_gpt_connection()
    
    # Test 4: Full Pipeline (only if all connections work)
    if test2_pass and test3_pass:
        test4_pass = test_full_pipeline() is not None
    else:
        print("\n" + "="*80)
        print("TEST 4: FULL HYBRID PIPELINE")
        print("="*80)
        print("⏭️  Skipping (LLM connections not available)")
        test4_pass = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Test 1 (Systematic Validator): {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"Test 2 (Qwen Connection):      {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print(f"Test 3 (GPT-OSS Connection):   {'✅ PASS' if test3_pass else '❌ FAIL'}")
    print(f"Test 4 (Full Pipeline):        {'✅ PASS' if test4_pass else '❌ FAIL' if not (test2_pass and test3_pass) else '⏭️  SKIP'}")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if test1_pass and not test2_pass and not test3_pass:
        print("✅ Systematic validator works (deterministic grading)")
        print("⚠️  LLM connections not available")
        print("\nTo enable full pipeline:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull models:")
        print("   ollama pull qwen2.5-coder:latest")
        print("   ollama pull gpt-oss-120b:latest")
        print("3. Run this test again")
        print("\nYou can still use systematic validator alone:")
        print("   python3 grade_with_systematic_validator.py --dir submissions/12")
    
    elif test1_pass and test2_pass and test3_pass:
        print("✅ ALL SYSTEMS OPERATIONAL!")
        print("\nYou can now use the full hybrid pipeline:")
        print("   python3 validators/hybrid_grading_pipeline.py \\")
        print("     --file submissions/12/student.ipynb")
        print("\nOr grade all submissions:")
        print("   python3 batch_grade_hybrid.py")
    
    else:
        print("⚠️  Some tests failed. Check errors above.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
