#!/usr/bin/env python3
"""
Create Assignment 7 Solution Notebook for Version 2 (Processed Data)
Uses only methods taught in Lesson 7
"""

import json

# Read the template to match structure
with open('data/raw/homework_lesson_7_string_datetime (1).ipynb', 'r') as f:
    template = json.load(f)

# Create solution notebook based on template
solution = {
    "cells": [],
    "metadata": template.get("metadata", {}),
    "nbformat": template.get("nbformat", 4),
    "nbformat_minor": template.get("nbformat_minor", 5)
}

# Helper function to create code cells
def code_cell(source, execution_count=None):
    return {
        "cell_type": "code",
        "execution_count": execution_count,
        "id": f"cell_{len(solution['cells'])}",
        "metadata": {"vscode": {"languageId": "r"}},
        "outputs": [],
        "source": source if isinstance(source, list) else [source]
    }

# Helper function to create markdown cells
def markdown_cell(source):
    return {
        "cell_type": "markdown",
        "id": f"cell_{len(solution['cells'])}",
        "metadata": {},
        "source": source if isinstance(source, list) else [source]
    }

# Add cells from template but with solution code
for cell in template['cells']:
    if cell['cell_type'] == 'markdown':
        # Keep all markdown cells as-is
        solution['cells'].append(cell)
    elif cell['cell_type'] == 'code':
        # Check cell ID to add appropriate solution
        cell_id = cell.get('id', '')
        
        if cell_id == 'setup' or 'Task 1.1' in ''.join(cell.get('source', [])):
            # Task 1.1: Load packages
            solution['cells'].append(code_cell([
                "# Task 1.1: Load Required Packages\n",
                "library(tidyverse)  # includes stringr\n",
                "\n",
                "library(lubridate)\n",
                "\n",
                "cat(\"✅ Packages loaded successfully!\\n\")"
            ], 1))
            
        elif cell_id == 'import_data' or 'Task 1.2' in ''.join(cell.get('source', [])):
            # Task 1.2: Import data
            solution['cells'].append(code_cell([
                "# Task 1.2: Import Datasets\n",
                "# NOTE: Using processed data with PascalCase columns\n",
                "feedback <- read_csv(\"data/processed/customer_feedback (1).csv\")\n",
                "\n",
                "transactions <- read_csv(\"data/processed/transaction_log.csv\")\n",
                "\n",
                "products <- read_csv(\"data/processed/product_catalog.csv\")\n",
                "\n",
                "cat(\"✅ Data imported successfully!\\n\")\n",
                "cat(\"Feedback rows:\", nrow(feedback), \"\\n\")\n",
                "cat(\"Transaction rows:\", nrow(transactions), \"\\n\")\n",
                "cat(\"Product rows:\", nrow(products), \"\\n\")"
            ], 2))
            
        elif cell_id == 'explore_data' or 'Task 1.3' in ''.join(cell.get('source', [])):
            # Task 1.3: Explore data
            solution['cells'].append(code_cell([
                "# Task 1.3: Initial Data Exploration\n",
                "\n",
                "cat(\"=== CUSTOMER FEEDBACK DATA ===\\n\")\n",
                "str(feedback)\n",
                "\n",
                "head(feedback, 5)\n",
                "\n",
                "cat(\"\\n=== TRANSACTION DATA ===\\n\")\n",
                "str(transactions)\n",
                "\n",
                "head(transactions, 5)\n",
                "\n",
                "cat(\"\\n=== PRODUCT CATALOG DATA ===\\n\")\n",
                "str(products)\n",
                "\n",
                "head(products, 5)"
            ], 3))
            
        elif cell_id == 'clean_products' or 'Task 2.1' in ''.join(cell.get('source', [])):
            # Task 2.1: Clean product names
            solution['cells'].append(code_cell([
                "# Task 2.1: Clean Product Names\n",
                "# NOTE: Column is Product_Description not product_name\n",
                "products_clean <- products %>%\n",
                "  mutate(\n",
                "    product_name_clean = str_to_title(str_trim(Product_Description))\n",
                "  )\n",
                "\n",
                "# Display before and after\n",
                "cat(\"Product Name Cleaning Results:\\n\")\n",
                "products_clean %>%\n",
                "  select(Product_Description, product_name_clean) %>%\n",
                "  head(10) %>%\n",
                "  print()"
            ], 4))
            
        elif cell_id == 'clean_categories' or 'Task 2.2' in ''.join(cell.get('source', [])):
            # Task 2.2: Clean categories
            solution['cells'].append(code_cell([
                "# Task 2.2: Standardize Product Categories\n",
                "products_clean <- products_clean %>%\n",
                "  mutate(\n",
                "    category_clean = str_to_title(str_trim(Category))\n",
                "  )\n",
                "\n",
                "# Show unique categories before and after\n",
                "cat(\"Original categories:\\n\")\n",
                "print(unique(products$Category))\n",
                "\n",
                "cat(\"\\nCleaned categories:\\n\")\n",
                "print(unique(products_clean$category_clean))"
            ], 5))
            
        elif cell_id == 'clean_feedback' or 'Task 2.3' in ''.join(cell.get('source', [])):
            # Task 2.3: Clean feedback
            solution['cells'].append(code_cell([
                "# Task 2.3: Clean Customer Feedback Text\n",
                "# NOTE: Column is Feedback_Text not feedback_text\n",
                "feedback_clean <- feedback %>%\n",
                "  mutate(\n",
                "    feedback_clean = str_squish(str_to_lower(Feedback_Text))\n",
                "  )\n",
                "\n",
                "# Display sample\n",
                "cat(\"Feedback Cleaning Sample:\\n\")\n",
                "feedback_clean %>%\n",
                "  select(Feedback_Text, feedback_clean) %>%\n",
                "  head(5) %>%\n",
                "  print()"
            ], 6))
            
        else:
            # Keep template cell for now
            solution['cells'].append(cell)

# Write solution notebook
with open('data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb', 'w') as f:
    json.dump(solution, f, indent=1)

print("✅ Solution notebook created!")
print("Location: data/raw/homework_lesson_7_string_datetime_SOLUTION_v2.ipynb")
