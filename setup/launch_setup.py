#!/usr/bin/env python3
"""
Launch setup from the correct directory
"""

import os
import sys

# Change to homework_grader directory
os.chdir('homework_grader')

# Import and run setup
from setup_assignment_1 import main
main()