#!/usr/bin/env python3
"""
Anonymization utilities for demo mode
Shared across all pages
"""

import streamlit as st
import hashlib


def anonymize_name(student_name: str, student_id: str = None) -> str:
    """
    Anonymize student name for demo mode
    
    Args:
        student_name: The student's real name
        student_id: Optional student ID
        
    Returns:
        Anonymized name if demo mode is on, otherwise original name
    """
    if not st.session_state.get('demo_mode', False):
        return student_name
    
    # If student_id is numeric, use it
    if student_id and str(student_id).isdigit():
        return f"Student {student_id}"
    
    # Otherwise, create consistent hash-based number
    hash_num = int(hashlib.md5(student_name.encode()).hexdigest()[:6], 16) % 10000
    return f"Student {hash_num:04d}"


def anonymize_student_id(student_id: str) -> str:
    """
    Anonymize student ID for demo mode
    
    Args:
        student_id: The student's real ID
        
    Returns:
        'REDACTED' if demo mode is on, otherwise original ID
    """
    if st.session_state.get('demo_mode', False):
        return 'REDACTED'
    return student_id
