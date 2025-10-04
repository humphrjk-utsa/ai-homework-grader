#!/usr/bin/env python3
"""
Dual Panel Layout System
Responsive two-column layout for the AI training interface
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable

class DualPanelLayout:
    """Manages the dual-panel layout with responsive behavior"""
    
    def __init__(self, left_ratio: float = 0.33, right_ratio: float = 0.67):
        """
        Initialize dual panel layout
        
        Args:
            left_ratio: Width ratio for left panel (default 1/3)
            right_ratio: Width ratio for right panel (default 2/3)
        """
        self.left_ratio = left_ratio
        self.right_ratio = right_ratio
        self.setup_responsive_css()
    
    def setup_responsive_css(self):
        """Set up responsive CSS for the layout"""
        
        # Custom CSS for responsive behavior and visual improvements
        st.markdown("""
        <style>
        /* Main container styling */
        .main-container {
            display: flex;
            gap: 1rem;
            height: calc(100vh - 200px);
            min-height: 600px;
        }
        
        /* Left panel styling - Independent scrollable area */
        .left-panel {
            flex: 1;
            min-width: 300px;
            max-width: 400px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 200px);
            max-height: 800px;
        }
        
        .left-panel-header {
            padding: 1rem;
            border-bottom: 1px solid #e9ecef;
            background-color: #ffffff;
            border-radius: 8px 8px 0 0;
            flex-shrink: 0;
        }
        
        .left-panel-content {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background-color: #f8f9fa;
        }
        
        /* Right panel styling - Independent scrollable area */
        .right-panel {
            flex: 2;
            min-width: 500px;
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 200px);
            max-height: 800px;
        }
        
        .right-panel-header {
            padding: 1rem;
            border-bottom: 1px solid #e9ecef;
            background-color: #f8f9fa;
            border-radius: 8px 8px 0 0;
            flex-shrink: 0;
        }
        
        .right-panel-content {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background-color: #ffffff;
        }
        
        /* Responsive behavior for smaller screens */
        @media (max-width: 1200px) {
            .main-container {
                flex-direction: column;
                height: auto;
            }
            
            .left-panel, .right-panel {
                min-width: 100%;
                max-width: 100%;
            }
            
            .left-panel {
                max-height: 400px;
            }
        }
        
        /* Submission list styling */
        .submission-item {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .submission-item:hover {
            border-color: #007bff;
            box-shadow: 0 2px 4px rgba(0,123,255,0.1);
        }
        
        .submission-item.selected {
            border-color: #007bff;
            background-color: #f8f9ff;
            box-shadow: 0 2px 8px rgba(0,123,255,0.15);
        }
        
        /* Score indicator styling */
        .score-indicator {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .score-excellent {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .score-good {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .score-fair {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        .score-needs-work {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        /* Tab styling improvements */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #f8f9fa;
            border-radius: 8px 8px 0 0;
            border: 1px solid #dee2e6;
            border-bottom: none;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white;
            border-color: #007bff;
        }
        
        /* Filter section styling */
        .filter-section {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        /* Bulk operations styling */
        .bulk-operations {
            background-color: #fff;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 0.75rem;
            margin-bottom: 1rem;
        }
        
        /* Metrics styling */
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        /* Loading spinner */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }
        
        /* Error message styling */
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Success message styling */
        .success-message {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def create_layout(self, left_header_func: Callable, left_content_func: Callable, 
                     right_header_func: Callable, right_content_func: Callable):
        """
        Create the dual-panel layout with separate header and content functions
        
        Args:
            left_header_func: Function to render left panel header
            left_content_func: Function to render left panel scrollable content
            right_header_func: Function to render right panel header
            right_content_func: Function to render right panel scrollable content
        """
        
        # Create columns with specified ratios
        left_col, right_col = st.columns([self.left_ratio, self.right_ratio])
        
        with left_col:
            # Add container class for styling with independent scroll
            st.markdown('<div class="left-panel">', unsafe_allow_html=True)
            st.markdown('<div class="left-panel-header">', unsafe_allow_html=True)
            left_header_func()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="left-panel-content">', unsafe_allow_html=True)
            left_content_func()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with right_col:
            # Add container class for styling with independent scroll
            st.markdown('<div class="right-panel">', unsafe_allow_html=True)
            st.markdown('<div class="right-panel-header">', unsafe_allow_html=True)
            right_header_func()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="right-panel-content">', unsafe_allow_html=True)
            right_content_func()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_submission_item(self, submission: Dict[str, Any], is_selected: bool = False, 
                             on_select: Optional[Callable] = None) -> bool:
        """
        Render a single submission item in the left panel
        
        Args:
            submission: Submission data dictionary
            is_selected: Whether this submission is currently selected
            on_select: Callback function when submission is selected
            
        Returns:
            bool: True if submission was clicked
        """
        
        # Determine CSS class based on selection and score
        css_class = "submission-item"
        if is_selected:
            css_class += " selected"
        
        # Create container with styling
        container = st.container()
        
        with container:
            # Main selection button
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Student name and grade indicator
                grade_class = self._get_grade_css_class(submission['final_score'])
                
                st.markdown(f"""
                <div class="{css_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{submission['student_name']}</strong>
                            <br>
                            <span class="score-indicator {grade_class}">
                                {submission['grade_indicator']}
                            </span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.1em; font-weight: bold;">
                                {submission['final_score']:.1f}/37.5
                            </div>
                            <div style="font-size: 0.8em; color: #6c757d;">
                                {submission['score_status']}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Selection button (invisible overlay)
                clicked = st.button(
                    f"Select {submission['student_name']}", 
                    key=f"select_{submission['id']}",
                    label_visibility="collapsed",
                    use_container_width=True
                )
                
                if clicked and on_select:
                    on_select(submission['id'])
                    return True
            
            with col2:
                # Quick action buttons
                st.markdown("**Quick Actions**")
                
                # Score input
                current_score = submission['human_score'] or submission['ai_score']
                new_score = st.number_input(
                    "Score",
                    min_value=0.0,
                    max_value=37.5,
                    value=float(current_score),
                    step=0.5,
                    key=f"quick_score_{submission['id']}",
                    label_visibility="collapsed"
                )
                
                # Save button
                if st.button("💾", key=f"quick_save_{submission['id']}", help="Quick save"):
                    return {'action': 'save', 'score': new_score, 'submission_id': submission['id']}
        
        return False
    
    def _get_grade_css_class(self, score: float) -> str:
        """Get CSS class for grade indicator based on score"""
        if score >= 35:
            return "score-excellent"
        elif score >= 30:
            return "score-good"
        elif score >= 25:
            return "score-fair"
        else:
            return "score-needs-work"
    
    def render_metrics_header(self, metrics: Dict[str, Any]):
        """Render metrics header with styling"""
        
        st.markdown(f"""
        <div class="metric-container">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2em; font-weight: bold;">{metrics.get('total_submissions', 0)}</div>
                    <div style="opacity: 0.9;">Total Submissions</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2em; font-weight: bold;">{metrics.get('human_reviewed', 0)}</div>
                    <div style="opacity: 0.9;">Human Reviewed ({metrics.get('review_percentage', 0)}%)</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2em; font-weight: bold;">{metrics.get('avg_ai_score', 0):.1f}</div>
                    <div style="opacity: 0.9;">Avg AI Score</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2em; font-weight: bold;">{metrics.get('ai_accuracy_percentage', 0):.1f}%</div>
                    <div style="opacity: 0.9;">AI Accuracy</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_filter_section(self) -> Dict[str, Any]:
        """Render filter section and return filter values"""
        
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown("**🔍 Filters & Search**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            score_range = st.slider(
                "Score Range", 
                0.0, 37.5, (0.0, 37.5), 
                step=0.5,
                help="Filter submissions by score range"
            )
            
            review_status = st.selectbox(
                "Review Status", 
                ["All", "AI Only", "Human Reviewed", "Needs Review"],
                help="Filter by review status"
            )
        
        with col2:
            student_search = st.text_input(
                "Search Student", 
                placeholder="Enter student name...",
                help="Search by student name"
            )
            
            sort_by = st.selectbox(
                "Sort By",
                ["Student Name", "Score (High to Low)", "Score (Low to High)", "Review Status"],
                help="Sort submissions by criteria"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return {
            'score_range': score_range,
            'review_status': review_status,
            'student_search': student_search,
            'sort_by': sort_by
        }
    
    def render_bulk_operations(self) -> Dict[str, Any]:
        """Render bulk operations section and return actions"""
        
        st.markdown('<div class="bulk-operations">', unsafe_allow_html=True)
        st.markdown("**⚡ Bulk Operations**")
        
        col1, col2, col3 = st.columns(3)
        
        actions = {}
        
        with col1:
            st.markdown("**Score Adjustments**")
            boost_percent = st.number_input(
                "Boost %", 
                min_value=1, max_value=20, value=5,
                help="Percentage to boost AI-only scores"
            )
            
            if st.button("📈 Boost All AI Scores", use_container_width=True):
                actions['boost'] = {'percent': boost_percent}
        
        with col2:
            st.markdown("**Curve Application**")
            curve_points = st.number_input(
                "Curve Points", 
                min_value=0.5, max_value=5.0, value=2.0, step=0.5,
                help="Points to add to all scores"
            )
            
            if st.button("📊 Apply Curve", use_container_width=True):
                actions['curve'] = {'points': curve_points}
        
        with col3:
            st.markdown("**Reset Options**")
            st.markdown("⚠️ *Use with caution*")
            
            if st.button("🔄 Reset to AI Scores", use_container_width=True):
                # Add confirmation
                if st.session_state.get('confirm_reset'):
                    actions['reset'] = True
                    st.session_state.confirm_reset = False
                else:
                    st.session_state.confirm_reset = True
                    st.warning("Click again to confirm reset")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return actions
    
    def render_loading_state(self, message: str = "Loading..."):
        """Render loading state"""
        st.markdown(f"""
        <div class="loading-spinner">
            <div style="text-align: center;">
                <div style="font-size: 1.2em; margin-bottom: 1rem;">{message}</div>
                <div>⏳</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_error_state(self, error_message: str, details: str = ""):
        """Render error state"""
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ Error:</strong> {error_message}
            {f'<br><small>{details}</small>' if details else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def render_success_state(self, success_message: str):
        """Render success state"""
        st.markdown(f"""
        <div class="success-message">
            <strong>✅ Success:</strong> {success_message}
        </div>
        """, unsafe_allow_html=True)

# Utility functions for layout management
def apply_filters(submissions: list, filters: Dict[str, Any]) -> list:
    """Apply filters to submissions list"""
    
    filtered = submissions.copy()
    
    # Score range filter
    if filters.get('score_range'):
        min_score, max_score = filters['score_range']
        filtered = [s for s in filtered if min_score <= s['final_score'] <= max_score]
    
    # Review status filter
    if filters.get('review_status') and filters['review_status'] != 'All':
        if filters['review_status'] == 'AI Only':
            filtered = [s for s in filtered if s['human_score'] is None]
        elif filters['review_status'] == 'Human Reviewed':
            filtered = [s for s in filtered if s['human_score'] is not None]
        elif filters['review_status'] == 'Needs Review':
            filtered = [s for s in filtered if s['human_score'] is None and s['final_score'] < 30]
    
    # Student search filter
    if filters.get('student_search'):
        search_term = filters['student_search'].lower()
        filtered = [s for s in filtered if search_term in s['student_name'].lower()]
    
    # Sorting
    if filters.get('sort_by'):
        if filters['sort_by'] == 'Student Name':
            filtered.sort(key=lambda x: x['student_name'])
        elif filters['sort_by'] == 'Score (High to Low)':
            filtered.sort(key=lambda x: x['final_score'], reverse=True)
        elif filters['sort_by'] == 'Score (Low to High)':
            filtered.sort(key=lambda x: x['final_score'])
        elif filters['sort_by'] == 'Review Status':
            filtered.sort(key=lambda x: (x['human_score'] is not None, x['student_name']))
    
    return filtered

def get_responsive_columns(screen_size: str = "desktop") -> tuple:
    """Get column ratios based on screen size"""
    
    if screen_size == "mobile":
        return (1.0,)  # Single column on mobile
    elif screen_size == "tablet":
        return (0.4, 0.6)  # Adjusted ratios for tablet
    else:  # desktop
        return (0.33, 0.67)  # Standard desktop ratios