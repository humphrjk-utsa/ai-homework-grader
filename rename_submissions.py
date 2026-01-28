#!/usr/bin/env python3
"""
Rename student submission files to Student_1, Student_2, etc.
"""
import os
import sys
import shutil

def rename_submissions(source_dir, output_dir=None):
    """
    Rename all .ipynb files in source_dir to Student_1, Student_2, etc.
    
    Args:
        source_dir: Directory containing student submissions
        output_dir: Optional output directory (if None, renames in place)
    """
    
    # Get all .ipynb files
    files = [f for f in os.listdir(source_dir) if f.endswith('.ipynb')]
    files.sort()  # Sort for consistent ordering
    
    print(f"📁 Found {len(files)} notebook files in: {source_dir}")
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📂 Copying to: {output_dir}")
    
    # Rename each file
    for i, filename in enumerate(files, start=1):
        old_path = os.path.join(source_dir, filename)
        new_filename = f"Student_{i}.ipynb"
        
        if output_dir:
            new_path = os.path.join(output_dir, new_filename)
            shutil.copy2(old_path, new_path)
            print(f"✅ Copied: {filename} → {new_filename}")
        else:
            new_path = os.path.join(source_dir, new_filename)
            os.rename(old_path, new_path)
            print(f"✅ Renamed: {filename} → {new_filename}")
    
    print(f"\n✅ Done! Processed {len(files)} files")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rename_submissions.py <source_dir> [output_dir]")
        print("\nExample:")
        print("  python3 rename_submissions.py submissions/1")
        print("  python3 rename_submissions.py submissions/1 submissions/test_batch")
        sys.exit(1)
    
    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(source):
        print(f"❌ Error: Directory not found: {source}")
        sys.exit(1)
    
    rename_submissions(source, output)
