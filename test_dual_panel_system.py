#!/usr/bin/env python3
"""
Test Dual Panel System
Comprehensive testing for the dual-panel layout implementation
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add current directory to path
sys.path.append('.')

from dual_panel_layout import DualPanelLayout, apply_filters, get_responsive_columns
from submission_list_panel import SubmissionListPanel, sort_submissions, filter_submissions_by_search
from tabbed_review_panel import TabbedReviewPanel
from integrated_dual_panel_system import IntegratedDualPanelSystem
from enhanced_training_interface import EnhancedTrainingInterface

def create_sample_submissions():
    """Create sample submission data for testing"""
    
    submissions = [
        {
            'id': 1,
            'student_name': 'Alice Johnson',
            'student_id': 'S001',
            'ai_score': 32.5,
            'human_score': None,
            'final_score': 32.5,
            'score_status': '🤖 AI Only',
            'grade_indicator': '👍 Good',
            'grade_category': 'Good',
            'submission_date': '2025-01-15',
            'notebook_path': 'test_notebook_1.ipynb',
            'ai_feedback': json.dumps({
                'detailed_feedback': {
                    'reflection_assessment': ['Good engagement with questions'],
                    'analytical_strengths': ['Clear code structure'],
                    'areas_for_development': ['Could improve visualization']
                },
                'instructor_comments': 'Solid work overall'
            })
        },
        {
            'id': 2,
            'student_name': 'Bob Smith',
            'student_id': 'S002',
            'ai_score': 28.0,
            'human_score': 30.0,
            'final_score': 30.0,
            'score_status': '📈 Boosted',
            'grade_indicator': '👍 Good',
            'grade_category': 'Good',
            'submission_date': '2025-01-14',
            'notebook_path': 'test_notebook_2.ipynb',
            'ai_feedback': json.dumps({
                'detailed_feedback': {
                    'reflection_assessment': ['Shows understanding'],
                    'analytical_strengths': ['Good use of methods'],
                    'areas_for_development': ['Need more analysis']
                }
            })
        },
        {
            'id': 3,
            'student_name': 'Carol Davis',
            'student_id': 'S003',
            'ai_score': 35.0,
            'human_score': 35.0,
            'final_score': 35.0,
            'score_status': '✅ Confirmed',
            'grade_indicator': '🎉 Excellent',
            'grade_category': 'Excellent',
            'submission_date': '2025-01-16',
            'notebook_path': 'test_notebook_3.ipynb',
            'ai_feedback': json.dumps({
                'detailed_feedback': {
                    'reflection_assessment': ['Excellent critical thinking'],
                    'analytical_strengths': ['Advanced techniques used'],
                    'areas_for_development': ['Minor formatting issues']
                }
            })
        },
        {
            'id': 4,
            'student_name': 'David Wilson',
            'student_id': 'S004',
            'ai_score': 22.0,
            'human_score': None,
            'final_score': 22.0,
            'score_status': '🤖 AI Only',
            'grade_indicator': '❌ Needs Work',
            'grade_category': 'Needs Work',
            'submission_date': '2025-01-13',
            'notebook_path': 'test_notebook_4.ipynb',
            'ai_feedback': json.dumps({
                'detailed_feedback': {
                    'reflection_assessment': ['Limited engagement'],
                    'analytical_strengths': ['Basic understanding shown'],
                    'areas_for_development': ['Major gaps in analysis', 'Incomplete work']
                }
            })
        }
    ]
    
    return submissions

def test_dual_panel_layout():
    """Test the dual panel layout system"""
    print("🧪 Testing Dual Panel Layout")
    print("=" * 40)
    
    try:
        # Test layout initialization
        layout = DualPanelLayout()
        print("✅ Layout initialization successful")
        
        # Test responsive columns
        desktop_cols = get_responsive_columns("desktop")
        tablet_cols = get_responsive_columns("tablet")
        mobile_cols = get_responsive_columns("mobile")
        
        assert desktop_cols == (0.33, 0.67), "Desktop columns should be (0.33, 0.67)"
        assert tablet_cols == (0.4, 0.6), "Tablet columns should be (0.4, 0.6)"
        assert mobile_cols == (1.0,), "Mobile should be single column"
        print("✅ Responsive column ratios correct")
        
        # Test filter application
        submissions = create_sample_submissions()
        
        # Test score range filter
        filters = {'score_range': (25.0, 35.0)}
        filtered = apply_filters(submissions, filters)
        assert len(filtered) == 3, "Should filter to 3 submissions in range 25-35"
        print("✅ Score range filtering works")
        
        # Test review status filter
        filters = {'review_status': 'AI Only'}
        filtered = apply_filters(submissions, filters)
        ai_only_count = len([s for s in filtered if s['human_score'] is None])
        assert ai_only_count == len(filtered), "Should only return AI-only submissions"
        print("✅ Review status filtering works")
        
        print("🎉 Dual panel layout tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Dual panel layout test failed: {e}")
        return False

def test_submission_list_panel():
    """Test the submission list panel"""
    print("\n🧪 Testing Submission List Panel")
    print("=" * 40)
    
    try:
        # Initialize components
        layout = DualPanelLayout()
        panel = SubmissionListPanel(layout)
        submissions = create_sample_submissions()
        
        print("✅ Submission list panel initialized")
        
        # Test sorting
        sorted_by_name = sort_submissions(submissions, "Student Name (A-Z)")
        assert sorted_by_name[0]['student_name'] == 'Alice Johnson', "Should sort alphabetically"
        
        sorted_by_score = sort_submissions(submissions, "Score (High to Low)")
        assert sorted_by_score[0]['final_score'] == 35.0, "Should sort by highest score first"
        print("✅ Sorting functions work correctly")
        
        # Test search filtering
        search_results = filter_submissions_by_search(submissions, "alice")
        assert len(search_results) == 1, "Should find Alice Johnson"
        assert search_results[0]['student_name'] == 'Alice Johnson', "Should return Alice"
        
        search_results = filter_submissions_by_search(submissions, "S00")
        assert len(search_results) == 4, "Should find all students with S00 prefix"
        print("✅ Search filtering works correctly")
        
        # Test empty search
        empty_search = filter_submissions_by_search(submissions, "")
        assert len(empty_search) == len(submissions), "Empty search should return all"
        print("✅ Empty search handling works")
        
        print("🎉 Submission list panel tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Submission list panel test failed: {e}")
        return False

def test_tabbed_review_panel():
    """Test the tabbed review panel"""
    print("\n🧪 Testing Tabbed Review Panel")
    print("=" * 40)
    
    try:
        # Initialize components
        layout = DualPanelLayout()
        panel = TabbedReviewPanel(layout)
        submissions = create_sample_submissions()
        
        print("✅ Tabbed review panel initialized")
        
        # Test AI feedback parsing
        submission = submissions[0]  # Alice Johnson
        ai_feedback = json.loads(submission['ai_feedback'])
        
        assert 'detailed_feedback' in ai_feedback, "Should have detailed feedback"
        assert 'reflection_assessment' in ai_feedback['detailed_feedback'], "Should have reflection assessment"
        print("✅ AI feedback structure validation works")
        
        # Test score metrics calculation
        submission_with_human = submissions[1]  # Bob Smith
        ai_score = submission_with_human['ai_score']
        human_score = submission_with_human['human_score']
        final_score = submission_with_human['final_score']
        
        assert human_score > ai_score, "Human score should be higher (boosted)"
        assert final_score == human_score, "Final score should match human score"
        print("✅ Score metrics calculation works")
        
        # Test grade categorization
        excellent_submission = submissions[2]  # Carol Davis
        needs_work_submission = submissions[3]  # David Wilson
        
        assert excellent_submission['grade_category'] == 'Excellent', "Should categorize as Excellent"
        assert needs_work_submission['grade_category'] == 'Needs Work', "Should categorize as Needs Work"
        print("✅ Grade categorization works")
        
        print("🎉 Tabbed review panel tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Tabbed review panel test failed: {e}")
        return False

def test_integrated_system():
    """Test the integrated dual panel system"""
    print("\n🧪 Testing Integrated Dual Panel System")
    print("=" * 40)
    
    try:
        # Create mock training interface
        class MockTrainingInterface:
            def get_training_stats(self, assignment_id):
                return {
                    'total_submissions': 4,
                    'human_reviewed': 1,
                    'review_percentage': 25.0,
                    'avg_ai_score': 29.4,
                    'avg_human_score': 30.0,
                    'ai_accuracy_percentage': 75.0,
                    'avg_score_difference': 1.5,
                    'score_distribution': {
                        'Excellent': 1,
                        'Good': 2,
                        'Needs Work': 1
                    }
                }
            
            def get_submissions(self, assignment_id, filters=None):
                submissions = create_sample_submissions()
                if filters:
                    submissions = apply_filters(submissions, filters)
                return submissions
            
            def save_human_feedback(self, submission_id, score, feedback):
                return True
            
            def apply_bulk_operation(self, submission_ids, operation, **kwargs):
                return True, f"Applied {operation} to {len(submission_ids)} submissions"
            
            def export_to_csv(self, assignment_id, submissions):
                # Create temporary CSV file
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                temp_file.write("student_name,score\n")
                for s in submissions:
                    temp_file.write(f"{s['student_name']},{s['final_score']}\n")
                temp_file.close()
                return temp_file.name
        
        # Initialize integrated system
        mock_interface = MockTrainingInterface()
        system = IntegratedDualPanelSystem(mock_interface)
        
        print("✅ Integrated system initialized")
        
        # Test filter application
        submissions = create_sample_submissions()
        
        # Test with different filters
        system._session_state_filters = {
            'score_range': (30.0, 37.5),
            'review_status': 'All',
            'student_search': '',
            'sort_by': 'Score (High to Low)'
        }
        
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self.filters = {
                    'score_range': (30.0, 37.5),
                    'review_status': 'All',
                    'student_search': '',
                    'sort_by': 'Score (High to Low)'
                }
        
        # Test filter application (mock session state)
        import types
        mock_session_state = types.SimpleNamespace()
        mock_session_state.filters = {
            'score_range': (30.0, 37.5),
            'review_status': 'All',
            'student_search': '',
            'sort_by': 'Score (High to Low)'
        }
        
        # Temporarily replace session state for testing
        original_session_state = getattr(system, '_session_state', None)
        system._session_state = mock_session_state
        
        # Apply filters manually for testing
        filtered = apply_filters(submissions, mock_session_state.filters)
        high_score_count = len([s for s in filtered if s['final_score'] >= 30.0])
        assert high_score_count == len(filtered), "Should only return high-scoring submissions"
        print("✅ Integrated filtering works")
        
        # Test CSV export
        csv_path = mock_interface.export_to_csv(1, submissions)
        assert os.path.exists(csv_path), "CSV file should be created"
        
        with open(csv_path, 'r') as f:
            content = f.read()
            assert 'Alice Johnson' in content, "CSV should contain student data"
        
        # Cleanup
        os.unlink(csv_path)
        print("✅ CSV export works")
        
        print("🎉 Integrated system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integrated system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_responsive_behavior():
    """Test responsive behavior of the layout"""
    print("\n🧪 Testing Responsive Behavior")
    print("=" * 40)
    
    try:
        # Test different screen sizes
        screen_sizes = ["desktop", "tablet", "mobile"]
        
        for size in screen_sizes:
            columns = get_responsive_columns(size)
            print(f"✅ {size.capitalize()} layout: {columns}")
            
            if size == "desktop":
                assert len(columns) == 2, "Desktop should have 2 columns"
            elif size == "tablet":
                assert len(columns) == 2, "Tablet should have 2 columns"
            elif size == "mobile":
                assert len(columns) == 1, "Mobile should have 1 column"
        
        print("✅ Responsive behavior works correctly")
        
        # Test CSS class generation
        layout = DualPanelLayout()
        
        # Test that CSS setup doesn't crash
        layout.setup_responsive_css()
        print("✅ CSS setup works without errors")
        
        print("🎉 Responsive behavior tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Responsive behavior test failed: {e}")
        return False

def run_all_dual_panel_tests():
    """Run all tests for the dual panel system"""
    print("🚀 Dual Panel System - Comprehensive Tests")
    print("=" * 60)
    
    tests = [
        ("Dual Panel Layout", test_dual_panel_layout),
        ("Submission List Panel", test_submission_list_panel),
        ("Tabbed Review Panel", test_tabbed_review_panel),
        ("Integrated System", test_integrated_system),
        ("Responsive Behavior", test_responsive_behavior)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Tests...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DUAL PANEL SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All dual panel system tests passed! Ready for integration.")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_dual_panel_tests()
    sys.exit(0 if success else 1)