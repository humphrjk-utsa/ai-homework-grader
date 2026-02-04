# Homework 7: String Manipulation and Date/Time Data

## Overview

This homework assignment is based on Lesson 7 and focuses on string manipulation with `stringr` and date/time operations with `lubridate`. It follows the style of existing homework assignments with more TODO sections and less given code, making students think more while remaining structured for AI grading.

## File Information

**Filename:** `homework_lesson_7_string_datetime.ipynb`  
**Location:** `data/raw/homework_lesson_7_string_datetime.ipynb`  
**Format:** Jupyter Notebook (R kernel)  
**Total Cells:** 35 (16 markdown, 19 code)

## Key Features

### Student-Friendly Design
- ✅ **Student name/ID/date fields** at the top of the notebook
- ✅ **More TODO sections, less given code** - students must think and implement
- ✅ **Clear business context** for every task
- ✅ **Step-by-step guidance** with hints
- ✅ **Follows existing homework style** (matches Homework 3 and 4 format)

### AI Grading Optimization
- ✅ **Consistent variable names** across all tasks
- ✅ **Predictable output structure** for automated checking
- ✅ **Clear task numbering** (Task 1.1, 1.2, 2.1, etc.)
- ✅ **Standardized column names** for created variables
- ✅ **Structured reflection questions** with clear prompts

### Educational Value
- ✅ **Real-world business scenarios** for each task
- ✅ **Progressive difficulty** from basic to advanced
- ✅ **Combines multiple skills** in later sections
- ✅ **Comprehensive reflection questions** (6 questions)
- ✅ **Professional submission checklist**

## Assignment Structure

### Part 1: Data Import and Initial Exploration
- Load packages (tidyverse, lubridate)
- Import three CSV files
- Examine data structure
- Identify quality issues

### Part 2: String Cleaning and Standardization
- Clean product names (trim, title case)
- Standardize categories
- Clean feedback text
- Remove extra whitespace

### Part 3: Pattern Detection and Extraction
- Detect product features (wireless, premium, gaming)
- Extract specifications (numbers from text)
- Perform sentiment analysis
- Count positive/negative words

### Part 4: Date Parsing and Component Extraction
- Parse transaction dates
- Extract year, month, day, weekday
- Identify weekend transactions
- Extract quarters and month names

### Part 5: Date Calculations and Recency Analysis
- Calculate days since transaction
- Categorize by recency (Recent, Moderate, At Risk)
- Identify at-risk customers
- Analyze customer engagement

### Part 6: Combined String and Date Operations
- Extract first names from customer names
- Create personalized messages based on recency
- Analyze transaction patterns by weekday
- Perform monthly transaction analysis

### Part 7: Business Intelligence Summary
- Create executive dashboard
- Calculate key metrics
- Identify top products and categories
- Provide data-driven recommendations

### Part 8: Reflection Questions
Six comprehensive questions covering:
1. Data quality impact
2. Pattern detection value
3. Date analysis importance
4. Customer recency strategy
5. Sentiment analysis application
6. Real-world application scenarios

## Required Datasets

The homework uses three CSV files that should be in the `data/` directory:

1. **customer_feedback.csv**
   - Customer reviews with messy text
   - Contains: customer names, feedback text, ratings
   - Issues: Extra spaces, inconsistent case, embedded information

2. **transaction_log.csv**
   - Transaction records with dates
   - Contains: customer names, transaction dates, amounts
   - Issues: Various date formats, need temporal analysis

3. **product_catalog.csv**
   - Product descriptions needing standardization
   - Contains: product names, categories, descriptions
   - Issues: Inconsistent formatting, embedded specifications

## Skills Assessed

### String Manipulation (stringr)
- `str_trim()` - Remove leading/trailing whitespace
- `str_squish()` - Remove extra whitespace
- `str_to_lower()`, `str_to_upper()`, `str_to_title()` - Case conversion
- `str_detect()` - Pattern detection
- `str_extract()` - Information extraction
- `str_count()` - Pattern counting
- Regular expressions for complex patterns

### Date/Time Operations (lubridate)
- `ymd()`, `mdy()`, `dmy()` - Date parsing
- `year()`, `month()`, `day()` - Component extraction
- `wday()` - Weekday extraction
- `quarter()` - Quarter extraction
- `today()` - Current date
- Date arithmetic - Calculating differences
- `case_when()` - Conditional categorization

### Business Applications
- Data cleaning and standardization
- Customer segmentation by recency
- Sentiment analysis
- Pattern identification
- Temporal trend analysis
- Personalized communication
- Executive reporting

## Grading Criteria

The homework is designed to be graded on:

- **Code Correctness (40%)**: All tasks completed correctly
  - Proper use of stringr functions
  - Correct date parsing and calculations
  - Accurate pattern detection and extraction
  - Valid business logic implementation

- **Code Quality (20%)**: Clean, well-commented, efficient code
  - Proper use of pipe operator
  - Clear variable names
  - Helpful comments
  - Efficient approach

- **Business Understanding (20%)**: Demonstrates understanding of business applications
  - Appropriate categorization logic
  - Meaningful insights
  - Practical recommendations
  - Context awareness

- **Reflection Questions (15%)**: Thoughtful, complete answers
  - Demonstrates understanding
  - Provides specific examples
  - Shows critical thinking
  - Connects to real-world scenarios

- **Presentation (5%)**: Professional formatting and organization
  - Complete student information
  - Clean output
  - Organized structure
  - No remaining TODOs

## Expected Student Outputs

### Variables Students Will Create

**Products Dataset:**
- `product_name_clean` - Cleaned product names
- `category_clean` - Standardized categories
- `is_wireless` - Boolean flag
- `is_premium` - Boolean flag
- `is_gaming` - Boolean flag
- `size_number` - Extracted specifications

**Feedback Dataset:**
- `feedback_clean` - Cleaned feedback text
- `positive_words` - Count of positive words
- `negative_words` - Count of negative words
- `sentiment_score` - Overall sentiment

**Transactions Dataset:**
- `date_parsed` - Parsed date objects
- `trans_year`, `trans_month`, `trans_day` - Date components
- `trans_month_name` - Month name
- `trans_weekday` - Weekday name
- `trans_quarter` - Quarter number
- `is_weekend` - Boolean flag
- `days_since` - Days since transaction
- `recency_category` - Categorization
- `first_name` - Extracted first name
- `personalized_message` - Custom message

### Analysis Outputs

- Weekday transaction patterns
- Monthly transaction patterns
- Product category distribution
- Sentiment analysis summary
- Customer recency distribution
- Business intelligence dashboard

## Usage Instructions

### For Instructors

1. **Distribute the notebook** to students
2. **Ensure data files are available** in the `data/` directory
3. **Set due date** in the header cell
4. **Review grading criteria** with students
5. **Use consistent variable names** for automated grading

### For Students

1. **Fill in header information** (name, ID, date)
2. **Work through each part sequentially**
3. **Complete all TODO sections**
4. **Run cells to verify code works**
5. **Answer all reflection questions**
6. **Check submission checklist before submitting**

### For AI Grading

The homework is structured for AI grading with:
- Consistent variable naming conventions
- Predictable output structures
- Clear task delineation
- Standardized column names
- Verifiable calculations

## Comparison to Existing Homework

### Similar to Homework 3 & 4:
- Student name/ID/date at top
- Clear part structure
- TODO-based approach
- Business context for each task
- Reflection questions
- Submission checklist

### Enhancements:
- More comprehensive business scenarios
- Stronger connection to real-world applications
- Better structured for AI grading
- More progressive difficulty
- Combines multiple skills in later sections

## Next Steps

After completing this homework, students will be ready for:
- **Lesson 8**: Advanced data wrangling techniques
- **Complex pipelines**: Chaining multiple operations
- **Data validation**: Quality checks and business rules
- **Reproducible workflows**: Professional analysis practices

## Notes for AI Grading

### Key Variables to Check:
- All `*_clean` variables should exist
- Boolean flags should be TRUE/FALSE
- Date components should be numeric or factor
- Sentiment scores should be numeric
- Recency categories should match criteria

### Common Student Errors to Watch For:
- Forgetting to use `str_to_lower()` for case-insensitive matching
- Incorrect regex patterns (missing double backslashes)
- Wrong date parsing function (ymd vs mdy vs dmy)
- Incorrect recency category logic
- Missing pipe operators

### Validation Checks:
- All required columns created
- No NA values in key calculations
- Logical consistency (e.g., is_weekend matches wday)
- Proper data types
- Reasonable value ranges

---

**Created:** 2025-01-05  
**Based on:** Lesson 7 - String Manipulation and Date/Time Data  
**Style:** Matches existing homework assignments (3 & 4)  
**Optimized for:** Student learning and AI grading
