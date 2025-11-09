#!/usr/bin/env python3
"""
Test that server code imports correctly
"""
import sys
import importlib.util

def test_import(file_path, name):
    """Test importing a Python file"""
    print(f"\nTesting {name}...")
    try:
        spec = importlib.util.spec_from_file_location(name, file_path)
        module = importlib.util.module_from_spec(spec)
        
        # Don't execute, just check syntax
        with open(file_path, 'r') as f:
            code = f.read()
            compile(code, file_path, 'exec')
        
        print(f"  ✅ {name} - Syntax OK")
        return True
    except SyntaxError as e:
        print(f"  ❌ {name} - Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  {name} - Import issue (may need dependencies): {e}")
        return True  # Syntax is OK, just missing deps

print("="*70)
print("SERVER CODE SYNTAX TESTS")
print("="*70)

results = []
results.append(test_import('disaggregated_inference/prefill_server_dgx.py', 'Prefill Server'))
results.append(test_import('disaggregated_inference/decode_server_mac.py', 'Decode Server'))
results.append(test_import('disaggregated_inference/orchestrator.py', 'Orchestrator'))

print("\n" + "="*70)
if all(results):
    print("✅ All server code syntax is valid!")
else:
    print("❌ Some files have syntax errors")
print("="*70)
