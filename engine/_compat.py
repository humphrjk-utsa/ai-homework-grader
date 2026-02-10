"""
Streamlit compatibility shim for the engine package.

When running under Flask (no streamlit available), provides no-op
replacements so engine code works without modification.
"""
import logging

logger = logging.getLogger('engine')

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

    class _NoOp:
        """No-op object that absorbs any attribute access or call."""
        def __getattr__(self, name):
            return self
        def __call__(self, *args, **kwargs):
            return self
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
        def __bool__(self):
            return False

    class _SessionState(dict):
        """Dict-like session state replacement."""
        def __getattr__(self, name):
            return self.get(name)

    class _MockStreamlit:
        """Mock streamlit module with no-op methods."""
        session_state = _SessionState()

        def __getattr__(self, name):
            if name == 'session_state':
                return self.__class__.session_state
            return _NoOp()

    st = _MockStreamlit()
