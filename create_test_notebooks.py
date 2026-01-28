#!/usr/bin/env python3
"""
Create anonymized test notebooks from a student submission
"""
import json
import os
import sys

def create_test_notebooks(source_file, output_dir, num_copies=5):
    """Create anonymized copies of a notebook for testing"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📖 Reading source notebook: {source_file}")
    
    # Read the source notebook
    with open(source_file, 'r') as f:
        notebook = json.load(f)
    
    # Create copies
    for i in range(1, num_copies + 1):
        # Convert notebook to string for replacement
        notebook_str = json.dumps(notebook, indent=2)
        
        # Replace any student name references
        # Add common patterns here
        replacements = {
            "Alexander Weis": f"Student {i}",
            "Alexander_Weis": f"Student_{i}",
            "weisalexanderj": f"student{i}",
            "alexandermichaelgregory": f"student{i}",
            "Michael Alexander": f"Student {i}",
            "Michael_Alexander": f"Student_{i}",
        }
        
        for old, new in replacements.items():
            notebook_str = notebook_str.replace(old, new)
        
        # Parse back to JSON
        notebook_copy = json.loads(notebook_str)
        
        # Write the new notebook
        output_file = os.path.join(output_dir, f"Student_{i}_test.ipynb")
        with open(output_file, 'w') as f:
            json.dump(notebook_copy, f, indent=2)
        
        print(f"✅ Created: {output_file}")
    
    print(f"\n📁 {num_copies} test notebooks created in: {output_dir}")

if __name__ == "__main__":
    # Default: use Alexander Weis submission from folder 1
    source = "submissions/1/Alexander_Weis_51610.ipynb"
    output = "submissions/test_batch"
    num = 5
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        source = sys.argv[1]
    if len(sys.argv) > 2:
        output = sys.argv[2]
    if len(sys.argv) > 3:
        num = int(sys.argv[3])
    
    create_test_notebooks(source, output, num)
