#!/usr/bin/env python3
"""
Simple test to show output validation working
"""

import json
import re

def extract_outputs_with_context(notebook_path):
    """Extract outputs with their code context"""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    results = {}
    
    for idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            outputs = []
            
            for output in cell.get('outputs', []):
                if 'text' in output:
                    outputs.append(''.join(output['text']))
            
            if outputs:
                results[idx] = {
                    'source': source,
                    'outputs': outputs
                }
    
    return results

def find_value_in_outputs(outputs_dict, patterns):
    """Find a value using multiple patterns"""
    for cell_data in outputs_dict.values():
        for output in cell_data['outputs']:
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    return int(match.group(1))
    return None

# Test
print("="*80)
print("SIMPLE OUTPUT VALIDATION TEST")
print("="*80)

student_outputs = extract_outputs_with_context('submissions/12/Emerickkathrynj_emerickkathrynj.ipynb')

# Test 1: Find customer_orders row count
patterns = [
    r'Inner Join Result:\s*(\d+)',
    r'customer_orders.*?(\d+)\s*rows',
]
value = find_value_in_outputs(student_outputs, patterns)
print(f"\ncustomer_orders row count: {value} (expected 200)")
print(f"✅ PASS" if value == 200 else f"❌ FAIL")

# Test 2: Find customers without orders
patterns = [
    r'Customers without orders:\s*(\d+)',
    r'Customers with No Orders:\s*(\d+)',
]
value = find_value_in_outputs(student_outputs, patterns)
print(f"\nCustomers without orders: {value} (expected 0)")
print(f"✅ PASS" if value == 0 else f"❌ FAIL")

# Test 3: Find orphaned orders
patterns = [
    r'Orders with invalid customer IDs:\s*(\d+)',
    r'Orders without valid customers:\s*(\d+)',
]
value = find_value_in_outputs(student_outputs, patterns)
print(f"\nOrphaned orders: {value} (expected 50)")
print(f"✅ PASS" if value == 50 else f"❌ FAIL")

# Test 4: Find top customer spent
patterns = [
    r'Top customer total spent:\s*\$?\s*([\d,]+\.?\d*)',
    r'top customer.*?\$?\s*([\d,]+\.?\d*)',
]
for cell_data in student_outputs.values():
    for output in cell_data['outputs']:
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                value = float(value_str)
                print(f"\nTop customer spent: ${value:.2f} (expected $8471.51)")
                diff = abs(value - 8471.51)
                print(f"✅ PASS (within 5%)" if diff / 8471.51 < 0.05 else f"❌ FAIL")
                break

print("\n" + "="*80)
