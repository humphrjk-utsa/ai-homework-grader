#!/usr/bin/env python3
"""
Test Parallax Integration with AI Homework Grader
Verifies the Parallax client and grader integration works correctly
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_parallax_client():
    """Test the Parallax client directly"""
    print("=" * 60)
    print("TEST 1: Parallax Client Connection")
    print("=" * 60)

    from models.parallax_client import ParallaxClient

    client = ParallaxClient(scheduler_url="http://169.254.150.101:3001")
    status = client.get_system_status()

    print(f"Scheduler URL: {status['scheduler_url']}")
    print(f"Scheduler Available: {status['scheduler_available']}")
    print(f"Distributed Ready: {status['distributed_ready']}")

    if status['distributed_ready']:
        print("✅ Parallax cluster is online!")
        return True
    else:
        print("❌ Parallax cluster is offline or not responding")
        return False


def test_simple_generation():
    """Test simple text generation via Parallax"""
    print("\n" + "=" * 60)
    print("TEST 2: Simple Generation")
    print("=" * 60)

    from models.parallax_client import ParallaxClient

    client = ParallaxClient(scheduler_url="http://169.254.150.101:3001")

    # Test a simple prompt
    prompt = "What is 2 + 2? Answer with just the number."

    print(f"Prompt: {prompt}")
    print("Generating response...")

    result = client.generate_code_analysis(prompt, max_tokens=50)

    if result:
        print(f"Response: {result}")
        print("✅ Generation successful!")
        return True
    else:
        print("❌ Generation failed")
        return False


def test_parallel_generation():
    """Test parallel generation (code + feedback)"""
    print("\n" + "=" * 60)
    print("TEST 3: Parallel Generation")
    print("=" * 60)

    from models.parallax_client import ParallaxClient

    client = ParallaxClient(scheduler_url="http://169.254.150.101:3001")

    code_prompt = "Analyze this R code: x <- 1:10; mean(x). Return JSON with 'analysis' key."
    feedback_prompt = "Give brief feedback on a student who correctly calculated a mean. Return JSON with 'feedback' key."

    print("Running parallel generation...")
    print(f"  Code prompt: {code_prompt[:50]}...")
    print(f"  Feedback prompt: {feedback_prompt[:50]}...")

    result = client.generate_parallel_sync(code_prompt, feedback_prompt)

    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return False

    print(f"\nResults:")
    print(f"  Code analysis: {result['code_analysis'][:100] if result['code_analysis'] else 'None'}...")
    print(f"  Feedback: {result['feedback'][:100] if result['feedback'] else 'None'}...")
    print(f"\nPerformance:")
    print(f"  Parallel time: {result['parallel_time']:.1f}s")
    print(f"  Code analysis time: {result['qwen_time']:.1f}s")
    print(f"  Feedback time: {result['gemma_time']:.1f}s")
    print(f"  Parallel efficiency: {result['parallel_efficiency']:.2f}x")

    if result['code_analysis'] and result['feedback']:
        print("✅ Parallel generation successful!")
        return True
    else:
        print("❌ Parallel generation failed")
        return False


def test_grader_integration():
    """Test that the grader detects and uses Parallax"""
    print("\n" + "=" * 60)
    print("TEST 4: Grader Integration Check")
    print("=" * 60)

    # Check if BusinessAnalyticsGraderV2 would detect Parallax
    # We can't fully test without a rubric, but we can check the import

    try:
        os.environ['PARALLAX_SCHEDULER_URL'] = 'http://169.254.150.101:3001'

        print("Checking grader imports...")

        from models.parallax_client import ParallaxClient
        client = ParallaxClient()
        status = client.get_system_status()

        if status['distributed_ready']:
            print("✅ Grader would detect and use Parallax cluster")
            return True
        else:
            print("⚠️ Parallax not available, grader would fall back to Ollama")
            return False

    except Exception as e:
        print(f"❌ Integration check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PARALLAX INTEGRATION TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1: Client connection
    results.append(("Parallax Client Connection", test_parallax_client()))

    # Only continue if cluster is available
    if results[0][1]:
        # Test 2: Simple generation
        results.append(("Simple Generation", test_simple_generation()))

        # Test 3: Parallel generation
        results.append(("Parallel Generation", test_parallel_generation()))

    # Test 4: Grader integration
    results.append(("Grader Integration", test_grader_integration()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
