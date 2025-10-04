#!/usr/bin/env python3
"""
Integrated Dual Panel System
Complete implementation of the dual-panel layout with all components
"""

import streamlit as st
import os
import logging
from typing import Dict, List, Any, Optional
from dual_panel_layout import DualPanelLayout, apply_filters
from submission_list_panel import SubmissionListPanel, sort_submissions, filter_submissions_by_search
from tabbed_review_panel import TabbedReviewPanel
from enhanced_training_interface import EnhancedTrainingInterface

# Set up logging
logger = logging.getLogger(__name__)

class IntegratedDualPanelSystem:
    """Complete dual-panel system integrating all components"""
    
    def __init__(self, training_interface: EnhancedTrainingInterface):
        self.training_interface = training_interface
        self.layout = DualPanelLayout()
        self.left_panel = SubmissionListPanel(self.layout)
        self.right_panel = TabbedReviewPanel(self.layout)
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'selected_submission_id' not in st.session_state:
            st.session_state.selected_submission_id = None
        
        if 'current_assignment_id' not in st.session_state:
            st.session_state.current_assignment_id = None
        
        if 'filters' not in st.session_state:
            st.session_state.filters = {
                'score_range': (0.0, 37.5),
                'review_status': 'All',
                'student_search': '',
                'sort_by': 'Student Name (A-Z)'
            }
    
    def render_complete_interface(self, assignment_id: int) -> Dict[str, Any]:
        """
        Render the complete dual-panel interface
        
        Args:
            assignment_id: ID of the assignment to display
            
        Returns:
            Dict with any actions that occurred
        """
        
        actions = {}
        
        # Update current assignment if changed
        if st.session_state.current_assignment_id != assignment_id:
            st.session_state.current_assignment_id = assignment_id
            st.session_state.selected_submission_id = None
        
        # Get assignment statistics
        stats = self.training_interface.get_training_stats(assignment_id)
        
        # Render metrics header
        self.layout.render_metrics_header(stats)
        
        # Get and filter submissions
        all_submissions = self.training_interface.get_submissions(assignment_id)
        
        if not all_submissions:
            st.warning("No submissions found for this assignment.")
            return actions
        
        # Apply filters and sorting
        filtered_submissions = self._apply_all_filters(all_submissions)
        
        # Ensure we have a selected submission
        if not st.session_state.selected_submission_id or not any(
            s['id'] == st.session_state.selected_submission_id for s in filtered_submissions
        ):
            if filtered_submissions:
                st.session_state.selected_submission_id = filtered_submissions[0]['id']
        
        # Create the dual-panel layout with separate headers and content
        self.layout.create_layout(
            lambda: self._render_left_panel_header(filtered_submissions, len(all_submissions)),
            lambda: self._render_left_panel(filtered_submissions, len(all_submissions)),
            lambda: self._render_right_panel_header(filtered_submissions),
            lambda: self._render_right_panel(filtered_submissions)
        )
        
        return actions
    
    def _render_left_panel(self, submissions: List[Dict[str, Any]], total_count: int):
        """Render the left panel content with header and scrollable area"""
        
        # This function is called within the left-panel-content div
        # The header is rendered separately
        
        # Filters and search (in scrollable area)
        filters = self.layout.render_filter_section()
        
        # Update session state filters
        if filters != st.session_state.filters:
            st.session_state.filters = filters
            st.rerun()
        
        # Bulk operations (in scrollable area)
        bulk_actions = self.layout.render_bulk_operations()
        if bulk_actions:
            self._handle_bulk_actions(bulk_actions, submissions)
        
        # Submission list (scrollable)
        list_actions = self.left_panel.render_submission_list(
            submissions,
            selected_id=st.session_state.selected_submission_id,
            on_select=self._handle_submission_select,
            on_score_save=self._handle_quick_score_save
        )
        
        if list_actions:
            self._handle_list_actions(list_actions)
    
    def _render_left_panel_header(self, submissions: List[Dict[str, Any]], total_count: int):
        """Render the left panel header"""
        self.left_panel.render_list_header(total_count, len(submissions))
    
    def _render_right_panel(self, submissions: List[Dict[str, Any]]):
        """Render the right panel content with header and scrollable area"""
        
        # Get selected submission
        selected_submission = None
        if st.session_state.selected_submission_id:
            selected_submission = next(
                (s for s in submissions if s['id'] == st.session_state.selected_submission_id),
                None
            )
        
        if not selected_submission:
            if submissions:
                selected_submission = submissions[0]
                st.session_state.selected_submission_id = selected_submission['id']
            else:
                st.info("No submission selected or available.")
                return
        
        # Render tabbed interface (content area)
        tab_actions = self.right_panel.render_tabbed_interface(
            selected_submission,
            self.training_interface
        )
        
        if tab_actions:
            self._handle_tab_actions(tab_actions, submissions)
    
    def _render_right_panel_header(self, submissions: List[Dict[str, Any]]):
        """Render the right panel header"""
        # Get selected submission for header
        selected_submission = None
        if st.session_state.selected_submission_id:
            selected_submission = next(
                (s for s in submissions if s['id'] == st.session_state.selected_submission_id),
                None
            )
        
        if selected_submission:
            self.right_panel.render_submission_header(selected_submission)
        else:
            st.markdown("### Select a submission to review")
    
    def _apply_all_filters(self, submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all filters and sorting to submissions"""
        
        filters = st.session_state.filters
        
        # Apply basic filters
        filtered = apply_filters(submissions, filters)
        
        # Apply search filter
        filtered = filter_submissions_by_search(filtered, filters.get('student_search', ''))
        
        # Apply sorting
        filtered = sort_submissions(filtered, filters.get('sort_by', 'Student Name (A-Z)'))
        
        return filtered
    
    def _handle_submission_select(self, submission_id: int):
        """Handle submission selection"""
        st.session_state.selected_submission_id = submission_id
        st.rerun()
    
    def _handle_quick_score_save(self, submission_id: int, score: float, feedback: str = "Quick save") -> bool:
        """Handle quick score save from left panel"""
        success = self.training_interface.save_human_feedback(submission_id, score, feedback)
        if success:
            st.success("Score saved!")
            st.rerun()
        else:
            st.error("Failed to save score")
        return success
    
    def _handle_bulk_actions(self, actions: Dict[str, Any], submissions: List[Dict[str, Any]]):
        """Handle bulk operations"""
        
        if 'boost' in actions:
            # Apply boost to AI-only submissions
            ai_only_ids = [s['id'] for s in submissions if s['human_score'] is None]
            if ai_only_ids:
                success, message = self.training_interface.apply_bulk_operation(
                    ai_only_ids, "boost_percentage", boost_percent=actions['boost']['percent']
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        elif 'curve' in actions:
            # Apply curve to all submissions
            all_ids = [s['id'] for s in submissions]
            success, message = self.training_interface.apply_bulk_operation(
                all_ids, "apply_curve", curve_points=actions['curve']['points']
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        
        elif 'reset' in actions:
            # Reset to AI scores
            human_reviewed_ids = [s['id'] for s in submissions if s['human_score'] is not None]
            if human_reviewed_ids:
                success, message = self.training_interface.apply_bulk_operation(
                    human_reviewed_ids, "reset_to_ai"
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    def _handle_list_actions(self, actions: Dict[str, Any]):
        """Handle actions from the submission list"""
        
        if actions.get('action') == 'select':
            st.session_state.selected_submission_id = actions['submission_id']
            st.rerun()
        
        elif actions.get('action') == 'save':
            # Score was already saved in the callback
            st.rerun()
        
        elif actions.get('action') == 'review':
            # Switch to human review tab (would need tab state management)
            st.session_state.selected_submission_id = actions['submission_id']
            st.rerun()
    
    def _handle_tab_actions(self, actions: Dict[str, Any], submissions: List[Dict[str, Any]]):
        """Handle actions from the tabbed interface"""
        
        if actions.get('action') == 'save_review':
            st.success("Review saved successfully!")
            st.rerun()
        
        elif actions.get('action') == 'generate_clean_pdf':
            self._generate_clean_individual_pdf(
                actions['submission_id'], 
                actions['student_name']
            )
        
        elif actions.get('action') == 'approve_ai':
            st.success("AI grade approved!")
            st.rerun()
        
        elif actions.get('action') == 'next_student':
            self._navigate_to_next_student(submissions)
    
    def _generate_clean_individual_pdf(self, submission_id: int, student_name: str):
        """Generate clean PDF for individual submission - instructor content only"""
        try:
            # Get assignment name
            assignments = self.training_interface.get_assignments()
            assignment_name = "Assignment"
            if assignments:
                current_assignment_id = st.session_state.get('current_assignment_id')
                assignment = next((a for a in assignments if a['id'] == current_assignment_id), None)
                if assignment:
                    assignment_name = assignment['title']
            
            # Generate clean PDF report
            pdf_path = self.training_interface.generate_clean_pdf_report(
                submission_id, student_name, assignment_name
            )
            
            if pdf_path and os.path.exists(pdf_path):
                st.success(f"✅ Clean PDF report generated for {student_name}")
                
                # Provide download
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        "📥 Download Clean PDF Report",
                        f.read(),
                        file_name=f"{student_name}_clean_report.pdf",
                        mime="application/pdf",
                        key=f"clean_pdf_{submission_id}"
                    )
            else:
                st.error("Failed to generate PDF report")
                
        except Exception as e:
            st.error(f"PDF generation failed: {e}")
            logger.error(f"Error generating clean PDF for submission {submission_id}: {e}")
    
    def _navigate_to_next_student(self, submissions: List[Dict[str, Any]]):
        """Navigate to the next student in the list"""
        
        current_id = st.session_state.selected_submission_id
        current_idx = next(
            (i for i, s in enumerate(submissions) if s['id'] == current_id),
            -1
        )
        
        if current_idx >= 0:
            next_idx = (current_idx + 1) % len(submissions)
            st.session_state.selected_submission_id = submissions[next_idx]['id']
            st.rerun()
    
    def render_bulk_export_section(self, assignment_id: int, submissions: List[Dict[str, Any]]):
        """Render bulk export and operations section"""
        
        st.markdown("---")
        st.subheader("📊 Bulk Operations & Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📁 Generate All PDFs", type="secondary", use_container_width=True):
                self._generate_bulk_pdfs(submissions)
        
        with col2:
            if st.button("📊 Export CSV", type="secondary", use_container_width=True):
                self._export_csv(assignment_id, submissions)
        
        with col3:
            if st.button("📈 Training Report", type="secondary", use_container_width=True):
                self._show_training_report(assignment_id)
    
    def _generate_bulk_pdfs(self, submissions: List[Dict[str, Any]]):
        """Generate PDFs for all submissions"""
        try:
            st.info("Bulk PDF generation would be implemented here")
            # This would integrate with existing bulk PDF generation
        except Exception as e:
            st.error(f"Bulk PDF generation failed: {e}")
    
    def _export_csv(self, assignment_id: int, submissions: List[Dict[str, Any]]):
        """Export submissions to CSV"""
        try:
            csv_path = self.training_interface.export_to_csv(assignment_id, submissions)
            if csv_path:
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        "📥 Download CSV",
                        f.read(),
                        file_name=f"assignment_{assignment_id}_grades.csv",
                        mime="text/csv"
                    )
                # Clean up temp file
                import os
                os.unlink(csv_path)
        except Exception as e:
            st.error(f"CSV export failed: {e}")
    
    def _show_training_report(self, assignment_id: int):
        """Show training summary report"""
        
        stats = self.training_interface.get_training_stats(assignment_id)
        
        st.subheader("📈 Training Summary Report")
        
        # Basic statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Overview**")
            st.write(f"• Total Submissions: {stats['total_submissions']}")
            st.write(f"• Human Reviewed: {stats['human_reviewed']} ({stats['review_percentage']}%)")
            st.write(f"• AI Accuracy: {stats['ai_accuracy_percentage']}%")
        
        with col2:
            st.write("**🎯 Scores**")
            st.write(f"• Average AI Score: {stats['avg_ai_score']:.1f}/37.5")
            st.write(f"• Average Human Score: {stats['avg_human_score']:.1f}/37.5")
            st.write(f"• Average Difference: {stats['avg_score_difference']:.1f}")
        
        # Score distribution
        if stats['score_distribution']:
            st.write("**📈 Score Distribution**")
            for category, count in stats['score_distribution'].items():
                st.write(f"• {category}: {count} students")

def create_enhanced_training_page_with_dual_panels():
    """Create the enhanced training page using the integrated dual-panel system"""
    
    st.title("🎓 Enhanced AI Training Review Interface")
    st.markdown("Comprehensive system for reviewing and correcting AI-generated scores")
    
    try:
        # Initialize training interface
        training_interface = EnhancedTrainingInterface()
        
        # Get assignments
        assignments = training_interface.get_assignments()
        if not assignments:
            st.warning("No assignments found in the database.")
            return
        
        # Assignment selection
        assignment_options = {
            f"{a['title']} ({a['submission_count']} submissions, {a['human_reviewed_count']} reviewed)": a['id'] 
            for a in assignments
        }
        
        selected_assignment_key = st.selectbox("Select Assignment", list(assignment_options.keys()))
        selected_assignment_id = assignment_options[selected_assignment_key]
        
        # Create and render dual-panel system with independent scrollable areas
        dual_panel_system = IntegratedDualPanelSystem(training_interface)
        actions = dual_panel_system.render_complete_interface(selected_assignment_id)
        
        # Get current submissions for bulk operations
        submissions = training_interface.get_submissions(selected_assignment_id)
        filtered_submissions = dual_panel_system._apply_all_filters(submissions)
        
        # Render bulk export section below the panels
        dual_panel_system.render_bulk_export_section(selected_assignment_id, filtered_submissions)
        
        # Add usage instructions
        with st.expander("ℹ️ Interface Guide"):
            st.markdown("""
            **Left Panel (1/3 width):**
            - Browse and search through all submissions
            - Each submission shows student name, score, and status
            - Click any submission to view details in the right panel
            - Use filters to narrow down the list
            - Quick edit scores directly in the list
            - Independent scrolling for large lists
            
            **Right Panel (2/3 width):**
            - Detailed view of the selected submission
            - Three tabs: AI Feedback, Notebook, Human Review
            - Independent scrolling for long content
            - Full notebook viewer with multiple display modes
            - Complete human review and scoring interface
            """)
        
    except Exception as e:
        st.error(f"Error loading enhanced training interface: {e}")
        st.info("Please ensure all dependencies are installed and the database is properly configured.")

if __name__ == "__main__":
    create_enhanced_training_page_with_dual_panels()