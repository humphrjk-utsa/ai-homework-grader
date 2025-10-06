# Homework 8: Advanced Data Wrangling - Capstone Project

## Overview

This is the **final capstone assignment** that integrates all R data wrangling skills covered throughout the course. Students perform a comprehensive business analysis that demonstrates mastery of data transformation, string manipulation, date/time operations, and business intelligence reporting.

## File Information

**Filename:** `homework_lesson_8_capstone.ipynb`  
**Location:** `data/raw/homework_lesson_8_capstone.ipynb`  
**Format:** Jupyter Notebook (R kernel)  
**Total Cells:** 36 (15 markdown, 21 code)  
**Estimated Time:** 3-4 hours

## Key Features

### Capstone Design
- ✅ **Comprehensive integration** of all course skills
- ✅ **Real-world business scenario** (e-commerce company analysis)
- ✅ **Student name/ID/date fields** at the top
- ✅ **More TODO sections, less given code** - students must apply knowledge
- ✅ **Structured for AI grading** with consistent variable names
- ✅ **Professional deliverables** (executive dashboard, strategic recommendations)

### Skills Integration
- ✅ **All dplyr functions**: select, filter, arrange, mutate, summarize, group_by
- ✅ **String manipulation**: stringr functions for cleaning and standardization
- ✅ **Date/time operations**: lubridate for parsing and temporal analysis
- ✅ **Complex logic**: case_when() for sophisticated categorization
- ✅ **Data validation**: Quality checks and business rule validation
- ✅ **Multi-dimensional analysis**: Grouped operations across multiple dimensions

## Assignment Structure

### Part 1: Data Import and Initial Validation (4 tasks)
- Load packages (tidyverse, lubridate)
- Import company sales data
- Perform initial exploration
- Validate data quality
- Document issues

**Key Variables Created:**
- `sales_data` - Raw imported data
- `data_quality_summary` - Quality metrics

### Part 2: Data Transformation and Feature Engineering (5 tasks)
- Calculate financial metrics (profit, profit_margin, ROI)
- Create performance categories
- Clean and standardize text fields
- Parse dates and extract components
- Create customer value scores

**Key Variables Created:**
- `sales_enhanced` - Main enhanced dataset with all calculated fields
- Calculated columns: `profit`, `profit_margin`, `roi`, `revenue_per_unit`, `cost_per_unit`
- Categories: `performance_tier`, `revenue_size`, `deal_type`, `high_value_flag`
- Cleaned text: `product_category_clean`, `region_clean`, `sales_rep_clean`
- Date components: `date_parsed`, `sale_year`, `sale_month`, `sale_month_name`, `sale_quarter`, `sale_weekday`, `is_weekend`
- Value score: `customer_value_score`

### Part 3: Comprehensive Business Analysis (6 tasks)
- Regional performance analysis
- Product category evaluation
- Sales representative performance
- Monthly trend analysis
- Weekday pattern analysis
- Multi-dimensional analysis (region × category)

**Key Variables Created:**
- `regional_performance` - Performance by region
- `category_performance` - Performance by product category
- `sales_rep_performance` - Performance by sales rep
- `monthly_trends` - Trends over time
- `weekday_patterns` - Patterns by day of week
- `region_category_performance` - Cross-dimensional analysis

### Part 4: Executive Dashboard and KPIs (3 tasks)
- Calculate overall business KPIs
- Identify top performers
- Analyze performance distribution

**Key Variables Created:**
- `business_kpis` - Overall business metrics
- `performance_dist` - Distribution of performance tiers
- `value_dist` - Distribution of customer value scores

### Part 5: Strategic Insights and Recommendations (2 tasks)
- Identify growth opportunities
- Highlight areas of concern
- Provide data-driven recommendations

**Key Variables Created:**
- `underperforming_regions` - Regions with potential
- Various analytical summaries

### Part 6: Capstone Reflection Questions (8 questions)
Comprehensive questions covering:
1. Data wrangling workflow
2. Integration of skills
3. Business impact and recommendations
4. Data quality importance
5. Grouped analysis value
6. Conditional logic application
7. Temporal analysis insights
8. Professional development reflection

## Required Dataset

**File:** `company_sales_data.csv` (located in `data/` directory)

**Contains:**
- Sales transactions with revenue, cost, units sold
- Customer information
- Product details and categories
- Regional information
- Sales representative data
- Transaction dates
- Various business metrics

**Expected Columns:**
- Revenue, Cost, Units_Sold
- Product_Category
- Region
- Sales_Rep
- Date
- (Other columns as available in the dataset)

## Skills Assessed

### Data Transformation (dplyr)
- `select()` - Column selection
- `filter()` - Row filtering
- `arrange()` - Sorting
- `mutate()` - Creating calculated fields
- `summarize()` - Aggregation
- `group_by()` - Grouped operations
- Pipe operator (`%>%`) - Chaining operations

### String Manipulation (stringr)
- `str_trim()` - Remove whitespace
- `str_to_title()` - Case conversion
- `str_to_lower()` - Lowercase conversion
- Text cleaning and standardization

### Date/Time Operations (lubridate)
- `ymd()`, `mdy()`, `dmy()` - Date parsing
- `year()`, `month()`, `day()` - Component extraction
- `wday()` - Weekday extraction
- `quarter()` - Quarter extraction
- Date calculations and comparisons

### Advanced Techniques
- `case_when()` - Complex conditional logic
- Multi-dimensional grouping
- Data quality validation
- Business rule implementation
- KPI calculation

### Business Applications
- Customer segmentation
- Performance categorization
- Temporal trend analysis
- Regional comparison
- Product portfolio analysis
- Executive reporting
- Strategic recommendation development

## Expected Student Outputs

### Main Enhanced Dataset
`sales_enhanced` with 20+ calculated columns including:
- Financial metrics (profit, margins, ROI)
- Performance categories (tiers, sizes, types)
- Cleaned text fields
- Date components
- Customer value scores

### Analysis Datasets
- `regional_performance` - 4-6 regions with metrics
- `category_performance` - 5-8 categories with metrics
- `sales_rep_performance` - Top 10+ sales reps
- `monthly_trends` - 3-12 months of data
- `weekday_patterns` - 7 days with patterns
- `region_category_performance` - 15+ combinations

### Business Intelligence
- `business_kpis` - 8+ key metrics
- Performance distributions
- Top performer identification
- Opportunity analysis
- Concern identification

## Grading Criteria

### Code Correctness (35%)
- All tasks completed correctly
- Proper function usage
- Accurate calculations
- Correct business logic
- All required variables created

### Code Quality (20%)
- Clean, organized code
- Meaningful variable names
- Helpful comments
- Efficient pipe usage
- Professional structure

### Business Analysis (25%)
- Understanding of business context
- Meaningful insights identified
- Appropriate categorization
- Data-driven recommendations
- Strategic thinking demonstrated

### Reflection Questions (15%)
- Thoughtful, complete answers
- Deep understanding shown
- Specific examples provided
- Critical thinking evident
- Real-world connections made

### Presentation (5%)
- Professional formatting
- Clear, organized output
- Complete information
- No errors/warnings
- Executive-ready quality

## AI Grading Optimization

### Consistent Variable Names
All key variables have standardized names:
- `sales_enhanced` - Main dataset
- `*_performance` - Performance analyses
- `*_trends` - Temporal analyses
- `*_patterns` - Pattern analyses
- `business_kpis` - KPI summary

### Predictable Structure
- Clear task numbering (Task 1.1, 1.2, etc.)
- Consistent column naming conventions
- Standardized output formats
- Verifiable calculations

### Validation Points
- Data quality metrics
- Category distributions
- Performance rankings
- KPI calculations
- Trend identifications

## Common Student Challenges

### Technical Challenges
- Parsing dates in correct format
- Creating complex case_when() logic
- Multi-dimensional grouping
- Calculating percentages correctly
- Handling NA values

### Business Challenges
- Understanding business context
- Creating meaningful categories
- Identifying actionable insights
- Prioritizing recommendations
- Communicating to executives

### Solutions Provided
- Clear business context for each task
- Hints for complex operations
- Examples of expected outputs
- Guidance on categorization logic
- Templates for recommendations

## Comparison to Other Homework

### Builds on Previous Assignments
- **Homework 3**: Basic dplyr operations
- **Homework 4**: Mutate, summarize, group_by
- **Homework 7**: String and date manipulation

### Capstone Enhancements
- Integrates all previous skills
- More complex business scenario
- Multi-dimensional analysis
- Executive-level deliverables
- Strategic recommendations required
- Comprehensive reflection

## Usage Instructions

### For Instructors
1. Ensure `company_sales_data.csv` is available
2. Set due date in header
3. Review grading criteria with students
4. Emphasize integration of all skills
5. Highlight professional deliverable expectations

### For Students
1. Fill in header information
2. Work through parts sequentially
3. Complete all TODO sections
4. Verify calculations are reasonable
5. Answer reflection questions thoroughly
6. Check submission checklist
7. Review executive dashboard for professionalism

### For AI Grading
- Check all required variables exist
- Verify calculations are correct
- Validate category logic
- Confirm distributions are reasonable
- Review reflection question completeness

## Learning Outcomes

Upon completion, students will be able to:
- Import and validate business data
- Transform raw data into analysis-ready format
- Clean and standardize text and dates
- Create sophisticated business categories
- Perform multi-dimensional analysis
- Calculate business KPIs
- Identify strategic opportunities
- Communicate insights to executives
- Provide data-driven recommendations

## Next Steps After Capstone

Students are prepared for:
- Advanced R programming
- Data visualization with ggplot2
- Statistical analysis
- Machine Learning
- R Markdown reporting
- Shiny dashboard development
- Professional data analyst roles

## Notes

### Time Management
- Part 1: 30 minutes (setup and validation)
- Part 2: 60 minutes (transformation)
- Part 3: 60 minutes (analysis)
- Part 4: 30 minutes (dashboard)
- Part 5: 20 minutes (recommendations)
- Part 6: 40 minutes (reflection)
- **Total: 3-4 hours**

### Professional Development
This capstone simulates real-world data analyst work:
- Working with messy business data
- Creating executive deliverables
- Making strategic recommendations
- Documenting analysis workflow
- Communicating technical findings

---

**Created:** 2025-01-05  
**Course:** R Data Wrangling  
**Type:** Final Capstone Project  
**Integrates:** All course skills (Lessons 1-8)  
**Style:** Matches Homework 7 format  
**Optimized for:** Student learning and AI grading
