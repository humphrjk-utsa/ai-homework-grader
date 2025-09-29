#!/usr/bin/env python3
"""
Restore essential files that were moved to archive but are still needed
"""

import shutil
import os

def restore_essential_files():
    """Copy back essential files from archive"""
    
    print("🔧 Restoring essential files from archive...")
    
    # Essential files that need to be in root directory
    essential_files = [
        'ai_grader.py',
        'rubric_manager.py', 
        'correction_helpers.py',
        'assignment_matcher.py',
        'assignment_setup_helper.py',
        'migration_helper.py',
        'alternative_approaches.py'
    ]
    
    restored_count = 0
    
    for filename in essential_files:
        archive_path = f'archive/{filename}'
        if os.path.exists(archive_path):
            if not os.path.exists(filename):  # Only copy if not already there
                shutil.copy2(archive_path, filename)
                print(f"✅ Restored {filename}")
                restored_count += 1
            else:
                print(f"ℹ️ {filename} already exists")
        else:
            print(f"❌ {filename} not found in archive")
    
    print(f"\n✅ Restored {restored_count} essential files")
    
    # Test imports
    print("\n🧪 Testing imports...")
    try:
        import app
        print("✅ app.py imports working")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    success = restore_essential_files()
    if success:
        print("\n🎉 All essential files restored! App should work now.")
        print("Run: streamlit run app.py")
    else:
        print("\n⚠️ Some issues remain. Check the error messages above.")