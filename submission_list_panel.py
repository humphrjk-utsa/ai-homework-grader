#!/usr/bin/env python3
"""
Submission List Panel
Left panel interface for managing submissions with inline editing
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Callable
from dual_panel_layout import DualPanelLayout

class SubmissionListPanel:
    """Manages the left panel submission list with inline editing capabilities"""
    
    def __init__(self, layout: DualPanelLayout):
        self.layout = layout
        self.setup_panel_css()
    
    def setup_panel_css(self):
        """Set up CSS specific to the submission list panel"""
        
        st.markdown("""
        <style>
        /* Submission list container - fits within left panel scroll area */
        .submission-list-container {
            height: 100%;
            overflow: visible; /* Let parent handle scrolling */
            padding-right: 0.5rem;
        }
        
        /* Individual submission card */
        .submission-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }
        
        .submission-card:hover {
            border-color: #007bff;
            box-shadow: 0 4px 12px rgba(0,123,255,0.15);
            transform: translateY(-2px);
        }
        
        .submission-card.selected {
            border-color: #007bff;
            background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%);
            box-shadow: 0 6px 20px rgba(0,123,255,0.2);
        }
        
        .submission-card.needs-attention {
            border-left: 4px solid #dc3545;
        }
        
        .submission-card.excellent {
            border-left: 4px solid #28a745;
        }
        
        .submission-card.good {
            border-left: 4px solid #17a2b8;
        }
        
        .submission-card.fair {
            border-left: 4px solid #ffc107;
        }
        
        /* Student info section */
        .student-info {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.75rem;
        }
        
        .student-name {
            font-weight: 600;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 0.25rem;
        }
        
        .student-id {
            font-size: 0.85em;
            color: #6c757d;
        }
        
        /* Score display */
        .score-display {
            text-align: right;
        }
        
        .score-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .score-percentage {
            font-size: 0.9em;
            color: #6c757d;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .status-ai-only {
            background-color: #e3f2fd;
            color: #1565c0;
            border: 1px solid #bbdefb;
        }
        
        .status-boosted {
            background-color: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
        }
        
        .status-reduced {
            background-color: #fff3e0;
            color: #f57c00;
            border: 1px solid #ffcc02;
        }
        
        .status-confirmed {
            background-color: #f3e5f5;
            color: #7b1fa2;
            border: 1px solid #e1bee7;
        }
        
        /* Inline editing section */
        .inline-edit-section {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem;
            background-color: #f8f9fa;
            border-radius: 6px;
            margin-top: 0.5rem;
        }
        
        .score-input {
            width: 80px !important;
            font-size: 0.9em !important;
        }
        
        .save-button {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 0.25rem 0.5rem !important;
            font-size: 0.8em !important;
            cursor: pointer !important;
        }
        
        .save-button:hover {
            background-color: #218838 !important;
        }
        
        /* Quick actions */
        .quick-actions {
            display: flex;
            gap: 0.25rem;
            margin-top: 0.5rem;
        }
        
        .quick-action-btn {
            padding: 0.25rem 0.5rem;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background: white;
            font-size: 0.75em;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .quick-action-btn:hover {
            background-color: #f8f9fa;
            border-color: #007bff;
        }
        
        /* Submission metadata */
        .submission-meta {
            font-size: 0.75em;
            color: #6c757d;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid #e9ecef;
        }
        
        /* Loading state */
        .submission-loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
            color: #6c757d;
        }
        
        /* Empty state */
        .submission-empty {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
        }
        
        /* Pagination */
        .pagination-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            margin-top: 1rem;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 6px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_submission_list(self, submissions: List[Dict[str, Any]], 
                             selected_id: Optional[int] = None,
                             on_select: Optional[Callable] = None,
                             on_score_save: Optional[Callable] = None,
                             items_per_page: int = 10) -> Dict[str, Any]:
        """
        Render the complete submission list with pagination and inline editing
        
        Args:
            submissions: List of submission dictionaries
            selected_id: Currently selected submission ID
            on_select: Callback when submission is selected
            on_score_save: Callback when score is saved
            items_per_page: Number of items per page
            
        Returns:
            Dict with any actions that occurred
        """
        
        actions = {}
        
        if not submissions:
            self._render_empty_state()
            return actions
        
        # Pagination setup
        total_pages = (len(submissions) - 1) // items_per_page + 1
        
        if total_pages > 1:
            page = st.selectbox(
                "Page", 
                range(1, total_pages + 1), 
                key="submission_page",
                help=f"Showing {len(submissions)} submissions across {total_pages} pages"
            ) - 1
        else:
            page = 0
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(submissions))
        page_submissions = submissions[start_idx:end_idx]
        
        # Render submissions container
        st.markdown('<div class="submission-list-container">', unsafe_allow_html=True)
        
        for submission in page_submissions:
            action = self._render_submission_card(
                submission, 
                selected_id == submission['id'],
                on_select,
                on_score_save
            )
            
            if action:
                actions.update(action)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Render pagination info
        if total_pages > 1:
            self._render_pagination_info(start_idx + 1, end_idx, len(submissions))
        
        return actions
    
    def _render_submission_card(self, submission: Dict[str, Any], is_selected: bool,
                              on_select: Optional[Callable] = None,
                              on_score_save: Optional[Callable] = None) -> Optional[Dict]:
        """Render individual submission card"""
        
        # Determine card styling
        card_classes = ["submission-card"]
        if is_selected:
            card_classes.append("selected")
        
        # Add grade-based styling
        final_score = submission['final_score']
        if final_score >= 35:
            card_classes.append("excellent")
        elif final_score >= 30:
            card_classes.append("good")
        elif final_score >= 25:
            card_classes.append("fair")
        else:
            card_classes.append("needs-attention")
        
        # Create unique key for this submission
        card_key = f"card_{submission['id']}"
        
        # Render card HTML
        st.markdown(f"""
        <div class="{' '.join(card_classes)}" id="{card_key}">
            <div class="student-info">
                <div>
                    <div class="student-name">{submission['student_name']}</div>
                    <div class="student-id">ID: {submission.get('student_id', 'N/A')}</div>
                </div>
                <div class="score-display">
                    <div class="score-value">{final_score:.1f}/37.5</div>
                    <div class="score-percentage">{(final_score/37.5*100):.1f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Selection button (invisible overlay)
        if st.button(
            f"Select {submission['student_name']}", 
            key=f"select_{submission['id']}",
            label_visibility="collapsed",
            use_container_width=True
        ):
            if on_select:
                on_select(submission['id'])
                return {'action': 'select', 'submission_id': submission['id']}
        
        # Status indicator
        status_class = self._get_status_class(submission['score_status'])
        st.markdown(f"""
        <div class="status-indicator {status_class}">
            {submission['score_status']}
        </div>
        """, unsafe_allow_html=True)
        
        # Inline editing section
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.caption("Quick Edit:")
            
            with col2:
                current_score = submission['human_score'] or submission['ai_score']
                new_score = st.number_input(
                    "Score",
                    min_value=0.0,
                    max_value=37.5,
                    value=float(current_score),
                    step=0.5,
                    key=f"score_input_{submission['id']}",
                    label_visibility="collapsed"
                )
            
            with col3:
                if st.button("💾", key=f"save_{submission['id']}", help="Save score"):
                    if on_score_save:
                        result = on_score_save(submission['id'], new_score)
                        if result:
                            return {'action': 'save', 'submission_id': submission['id'], 'score': new_score}
        
        # Quick actions
        with st.expander("⚡ Quick Actions", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("👍 Approve AI", key=f"approve_{submission['id']}", use_container_width=True):
                    if on_score_save:
                        ai_score = submission['ai_score']
                        result = on_score_save(submission['id'], ai_score, "AI grade approved")
                        if result:
                            return {'action': 'approve', 'submission_id': submission['id']}
            
            with col2:
                if st.button("📝 Review", key=f"review_{submission['id']}", use_container_width=True):
                    return {'action': 'review', 'submission_id': submission['id']}
        
        # Submission metadata
        st.markdown(f"""
        <div class="submission-meta">
            📅 Submitted: {submission.get('submission_date', 'Unknown')}<br>
            🤖 AI Method: {submission.get('grading_method', 'Unknown')}<br>
            📊 Grade: {submission['grade_indicator']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        return None
    
    def _get_status_class(self, status: str) -> str:
        """Get CSS class for status indicator"""
        status_map = {
            "🤖 AI Only": "status-ai-only",
            "📈 Boosted": "status-boosted", 
            "📉 Reduced": "status-reduced",
            "✅ Confirmed": "status-confirmed"
        }
        return status_map.get(status, "status-ai-only")
    
    def _render_empty_state(self):
        """Render empty state when no submissions"""
        st.markdown("""
        <div class="submission-empty">
            <h3>📭 No Submissions Found</h3>
            <p>No submissions match your current filters.</p>
            <p>Try adjusting your search criteria or filters.</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_pagination_info(self, start: int, end: int, total: int):
        """Render pagination information"""
        st.markdown(f"""
        <div class="pagination-controls">
            <small>Showing {start}-{end} of {total} submissions</small>
        </div>
        """, unsafe_allow_html=True)
    
    def render_list_header(self, total_count: int, filtered_count: int):
        """Render header for the submission list - this goes in the left panel header"""
        
        # This will be rendered in the left-panel-header div
        st.markdown("### 📋 Submissions")
        
        if filtered_count != total_count:
            st.caption(f"Showing {filtered_count} of {total_count} submissions")
        else:
            st.caption(f"{total_count} submissions")
        
        # Quick stats in compact format
        if total_count > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", total_count, label_visibility="collapsed")
            with col2:
                st.metric("Showing", filtered_count, label_visibility="collapsed")
    
    def render_bulk_selection(self, submissions: List[Dict[str, Any]]) -> List[int]:
        """Render bulk selection interface"""
        
        st.markdown("**Bulk Selection**")
        
        col1, col2, col3 = st.columns(3)
        
        selected_ids = []
        
        with col1:
            if st.button("Select All", use_container_width=True):
                selected_ids = [s['id'] for s in submissions]
        
        with col2:
            if st.button("Select AI Only", use_container_width=True):
                selected_ids = [s['id'] for s in submissions if s['human_score'] is None]
        
        with col3:
            if st.button("Select Needs Review", use_container_width=True):
                selected_ids = [s['id'] for s in submissions 
                              if s['human_score'] is None and s['final_score'] < 30]
        
        if selected_ids:
            st.success(f"Selected {len(selected_ids)} submissions")
        
        return selected_ids
    
    def render_search_and_sort(self) -> Dict[str, Any]:
        """Render search and sort controls"""
        
        st.markdown("**🔍 Search & Sort**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input(
                "Search students",
                placeholder="Enter student name...",
                key="student_search_input"
            )
        
        with col2:
            sort_option = st.selectbox(
                "Sort by",
                [
                    "Student Name (A-Z)",
                    "Student Name (Z-A)", 
                    "Score (High to Low)",
                    "Score (Low to High)",
                    "Review Status",
                    "Submission Date"
                ],
                key="sort_option"
            )
        
        return {
            'search_term': search_term,
            'sort_option': sort_option
        }

def sort_submissions(submissions: List[Dict[str, Any]], sort_option: str) -> List[Dict[str, Any]]:
    """Sort submissions based on the selected option"""
    
    if sort_option == "Student Name (A-Z)":
        return sorted(submissions, key=lambda x: x['student_name'])
    elif sort_option == "Student Name (Z-A)":
        return sorted(submissions, key=lambda x: x['student_name'], reverse=True)
    elif sort_option == "Score (High to Low)":
        return sorted(submissions, key=lambda x: x['final_score'], reverse=True)
    elif sort_option == "Score (Low to High)":
        return sorted(submissions, key=lambda x: x['final_score'])
    elif sort_option == "Review Status":
        return sorted(submissions, key=lambda x: (x['human_score'] is not None, x['student_name']))
    elif sort_option == "Submission Date":
        return sorted(submissions, key=lambda x: x.get('submission_date', ''), reverse=True)
    else:
        return submissions

def filter_submissions_by_search(submissions: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """Filter submissions by search term"""
    
    if not search_term:
        return submissions
    
    search_lower = search_term.lower()
    return [
        s for s in submissions 
        if search_lower in s['student_name'].lower() or 
           search_lower in s.get('student_id', '').lower()
    ]