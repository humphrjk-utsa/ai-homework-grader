#!/usr/bin/env python3
"""
Standalone Test App for AI Homework Grader Inference
Allows external users to test both Mac-only and Disaggregated inference
"""
import streamlit as st
import requests
import time
import json
import csv
import io
from datetime import datetime
from typing import Dict, Tuple
import sys
sys.path.insert(0, '.')

from disaggregated_client import DisaggregatedClient

# Page config
st.set_page_config(
    page_title="Inference Performance Tester",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Homework Grader - Inference Performance Tester")
st.markdown("Compare **Mac-only** inference vs **Disaggregated** inference (DGX + Mac)")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Mode selection
    mode = st.radio(
        "Inference Mode",
        ["Mac-only (Standalone)", "Disaggregated (DGX + Mac)"],
        help="Choose between running everything on Mac or using DGX for prefill"
    )

    # Model selection
    model_choice = st.selectbox(
        "Model",
        ["Qwen3-Coder-30B (Code Analysis)", "GPT-OSS-120B (Feedback)"],
        help="Choose the model for generation"
    )

    # Max tokens
    max_tokens = st.slider(
        "Max Output Tokens",
        min_value=100,
        max_value=2000,
        value=500,
        step=100,
        help="Maximum number of tokens to generate"
    )

    st.markdown("---")
    st.markdown("### 📊 Server Status")

    # Health checks
    if st.button("Check Server Health"):
        with st.spinner("Checking servers..."):
            health_status = {}

            # Check DGX servers
            for host, name in [("169.254.150.105", "DGX Spark 3"), ("169.254.150.106", "DGX Spark 4")]:
                try:
                    resp = requests.get(f"http://{host}:8080/health", timeout=2)
                    health_status[name] = "✅ Online" if resp.status_code == 200 else "❌ Error"
                except:
                    health_status[name] = "❌ Offline"

            # Check Mac servers
            for host, name in [("169.254.150.101", "Mac Studio 1"), ("169.254.150.102", "Mac Studio 2")]:
                try:
                    resp = requests.get(f"http://{host}:8081/health", timeout=2)
                    health_status[name] = "✅ Online" if resp.status_code == 200 else "❌ Error"
                except:
                    health_status[name] = "❌ Offline"

            for server, status in health_status.items():
                st.write(f"{server}: {status}")

# Main content area
st.markdown("---")

# Sample prompts
st.subheader("📝 Test Prompts")
prompt_template = st.selectbox(
    "Choose a sample prompt or enter your own",
    [
        "Custom (enter below)",
        "Code Analysis: R tidyverse",
        "Code Analysis: Python pandas",
        "Feedback: Student submission",
        "Quick Test: Small prompt"
    ]
)

# Preset prompts - Realistic grading scenarios with 500-2500+ tokens
prompts = {
    "Code Analysis: R tidyverse": """You are grading a data analysis assignment for a graduate-level Statistics course. Evaluate the following R code submission according to the rubric below.

ASSIGNMENT: Analyze retail sales data and create a summary report showing revenue trends by region and product category. Students should use tidyverse functions and follow best practices.

STUDENT SUBMISSION:
```r
library(tidyverse)
library(lubridate)

# Load and clean sales data
sales_data <- read_csv("retail_sales_2023.csv") %>%
  mutate(
    transaction_date = mdy(transaction_date),
    quarter = quarter(transaction_date),
    revenue = quantity * unit_price,
    profit_margin = (revenue - cost) / revenue
  ) %>%
  filter(!is.na(region), revenue > 0)

# Calculate regional summaries
regional_summary <- sales_data %>%
  group_by(region, product_category, quarter) %>%
  summarize(
    total_revenue = sum(revenue, na.rm = TRUE),
    avg_transaction_value = mean(revenue, na.rm = TRUE),
    total_transactions = n(),
    avg_profit_margin = mean(profit_margin, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(region, desc(total_revenue))

# Create comparison metrics
regional_performance <- regional_summary %>%
  group_by(region) %>%
  summarize(
    annual_revenue = sum(total_revenue),
    best_category = product_category[which.max(total_revenue)],
    total_customers = sum(total_transactions)
  )

# Export results
write_csv(regional_summary, "regional_summary_analysis.csv")
write_csv(regional_performance, "regional_performance_metrics.csv")
```

GRADING RUBRIC (100 points total):
1. Data Loading & Cleaning (20 points)
   - Proper library imports
   - Correct data import with read_csv
   - Appropriate data cleaning and filtering
   - Date handling and type conversions

2. Data Transformation (25 points)
   - Correct use of mutate for calculations
   - Proper grouping with group_by
   - Accurate summary statistics
   - Handling of missing values

3. Code Quality (25 points)
   - Clear variable naming
   - Efficient pipe operations
   - Proper use of tidyverse functions
   - Code organization and readability

4. Analysis Depth (20 points)
   - Multiple levels of aggregation
   - Meaningful metrics calculated
   - Comparison across groups
   - Business insights possible from results

5. Output & Documentation (10 points)
   - Appropriate file exports
   - Results saved correctly
   - Code comments where needed

Provide a detailed grade breakdown with specific feedback for each rubric category. Identify strengths and areas for improvement.""",

    "Code Analysis: Python pandas": """Grade this Python data analysis assignment for an Advanced Data Science course.

ASSIGNMENT DESCRIPTION:
Students must analyze customer transaction data using pandas to identify purchasing patterns. The analysis should include data cleaning, aggregation, time-series analysis, and cohort analysis. Final output should be production-ready with proper error handling.

STUDENT CODE SUBMISSION:
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load transaction data
transactions = pd.read_csv('customer_transactions.csv', parse_dates=['transaction_date'])
customers = pd.read_csv('customer_info.csv')

# Data cleaning and preparation
transactions_clean = transactions.copy()
transactions_clean['transaction_date'] = pd.to_datetime(transactions_clean['transaction_date'])
transactions_clean = transactions_clean[transactions_clean['amount'] > 0]
transactions_clean = transactions_clean.dropna(subset=['customer_id', 'amount'])

# Merge customer demographic data
df = transactions_clean.merge(customers, on='customer_id', how='left')

# Calculate customer lifetime value metrics
customer_metrics = df.groupby('customer_id').agg({
    'amount': ['sum', 'mean', 'count'],
    'transaction_date': ['min', 'max'],
    'age_group': 'first',
    'region': 'first'
}).reset_index()

customer_metrics.columns = ['customer_id', 'total_spend', 'avg_transaction',
                            'num_transactions', 'first_purchase', 'last_purchase',
                            'age_group', 'region']

customer_metrics['customer_lifetime_days'] = (
    customer_metrics['last_purchase'] - customer_metrics['first_purchase']
).dt.days

customer_metrics['purchase_frequency'] = (
    customer_metrics['num_transactions'] /
    (customer_metrics['customer_lifetime_days'] + 1)
)

# Cohort analysis
df['cohort_month'] = df.groupby('customer_id')['transaction_date'].transform('min').dt.to_period('M')
df['transaction_month'] = df['transaction_date'].dt.to_period('M')
df['cohort_age'] = (df['transaction_month'] - df['cohort_month']).apply(lambda x: x.n)

cohort_data = df.groupby(['cohort_month', 'cohort_age']).agg({
    'customer_id': 'nunique',
    'amount': 'sum'
}).reset_index()

cohort_data.columns = ['cohort_month', 'months_since_first', 'active_customers', 'revenue']

# Regional performance analysis
regional_analysis = df.groupby(['region', 'age_group']).agg({
    'amount': ['sum', 'mean'],
    'customer_id': 'nunique'
}).reset_index()

regional_analysis.columns = ['region', 'age_group', 'total_revenue',
                             'avg_transaction', 'unique_customers']

regional_analysis['revenue_per_customer'] = (
    regional_analysis['total_revenue'] / regional_analysis['unique_customers']
)

# Export results
customer_metrics.to_csv('customer_lifetime_value.csv', index=False)
cohort_data.to_csv('cohort_retention_analysis.csv', index=False)
regional_analysis.to_csv('regional_demographic_performance.csv', index=False)

print(f"Analysis complete. Processed {len(transactions_clean)} transactions")
print(f"Analyzed {customer_metrics['customer_id'].nunique()} unique customers")
```

GRADING RUBRIC (100 points):
1. Data Import & Cleaning (20 pts)
   - Proper file loading
   - Date parsing
   - Missing value handling
   - Data validation

2. Data Transformation (25 pts)
   - Correct merging/joins
   - Aggregation accuracy
   - Feature engineering
   - Column naming conventions

3. Analysis Complexity (25 pts)
   - Cohort analysis implementation
   - Time-series handling
   - Multiple aggregation levels
   - Metric calculations

4. Code Quality (20 pts)
   - Pandas best practices
   - Efficiency (avoiding loops)
   - Variable naming
   - Code structure

5. Output & Validation (10 pts)
   - Proper exports
   - Error handling
   - Result validation
   - Summary statistics

Grade this submission with detailed feedback on each rubric category.""",

    "Feedback: Student submission": """You are providing feedback on a midterm data analysis project. The student submitted both R code and a written analysis report.

ASSIGNMENT REQUIREMENTS:
Analyze the provided healthcare dataset to identify factors associated with patient readmission rates. Students must:
1. Clean and prepare the data
2. Perform exploratory data analysis
3. Build at least two predictive models
4. Compare model performance
5. Provide actionable recommendations

STUDENT R CODE:
```r
library(tidyverse)
library(caret)
library(randomForest)

# Load data
readmissions <- read_csv("hospital_readmissions.csv")

# Data cleaning
clean_data <- readmissions %>%
  filter(age >= 18, !is.na(diagnosis_code)) %>%
  mutate(
    readmitted_30day = ifelse(readmission_days <= 30, "Yes", "No"),
    length_of_stay_category = case_when(
      length_of_stay < 3 ~ "Short",
      length_of_stay < 7 ~ "Medium",
      TRUE ~ "Long"
    ),
    num_medications_group = cut(num_medications, breaks = c(0, 5, 10, 20, Inf),
                                 labels = c("Low", "Medium", "High", "Very High"))
  )

# Exploratory analysis
readmission_by_age <- clean_data %>%
  group_by(age_group, readmitted_30day) %>%
  summarize(count = n(), .groups = "drop") %>%
  mutate(proportion = count / sum(count))

# Split data
set.seed(42)
train_idx <- createDataPartition(clean_data$readmitted_30day, p = 0.7, list = FALSE)
train_data <- clean_data[train_idx, ]
test_data <- clean_data[-train_idx, ]

# Model 1: Logistic Regression
logit_model <- glm(readmitted_30day ~ age + length_of_stay + num_medications +
                   prior_admissions + diagnosis_category,
                   data = train_data, family = binomial)

# Model 2: Random Forest
rf_model <- randomForest(as.factor(readmitted_30day) ~ age + length_of_stay +
                         num_medications + prior_admissions + diagnosis_category,
                         data = train_data, ntree = 500)

# Predictions
logit_pred <- predict(logit_model, test_data, type = "response")
logit_pred_class <- ifelse(logit_pred > 0.5, "Yes", "No")

rf_pred <- predict(rf_model, test_data)

# Model evaluation
logit_cm <- confusionMatrix(as.factor(logit_pred_class), as.factor(test_data$readmitted_30day))
rf_cm <- confusionMatrix(rf_pred, as.factor(test_data$readmitted_30day))

print("Logistic Regression Accuracy:")
print(logit_cm$overall['Accuracy'])

print("Random Forest Accuracy:")
print(rf_cm$overall['Accuracy'])
```

STUDENT WRITTEN ANALYSIS EXCERPT:
"The analysis reveals that patients with longer hospital stays and higher medication counts are more likely to be readmitted within 30 days. The random forest model achieved 76% accuracy compared to 71% for logistic regression. Key predictive factors include: prior admission history (most important), length of stay, and number of prescribed medications. Recommendations: Implement enhanced discharge planning for high-risk patients identified by the model, particularly those with 3+ prior admissions."

EVALUATION CRITERIA:
- Technical correctness of R code
- Appropriate statistical methods
- Model selection and comparison
- Quality of data visualization (if any)
- Clarity of written analysis
- Actionable insights and recommendations
- Statistical rigor and validity of conclusions

Provide comprehensive feedback addressing: What the student did well, areas needing improvement, technical corrections needed, and suggestions for strengthening the analysis. Be specific and constructive.""",

    "Quick Test: Small prompt": "Analyze this simple R code and suggest one improvement:\n\n```r\nlibrary(dplyr)\ndata %>% filter(value > 10) %>% select(id, value)\n```"
}

if prompt_template == "Custom (enter below)":
    user_prompt = st.text_area(
        "Enter your prompt",
        height=200,
        placeholder="Enter your test prompt here..."
    )
else:
    user_prompt = st.text_area(
        "Prompt (you can edit this)",
        value=prompts.get(prompt_template, ""),
        height=200
    )

# Generate button
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    generate_btn = st.button("🚀 Generate", type="primary", use_container_width=True)

with col2:
    if st.button("🗑️ Clear Results", use_container_width=True):
        if 'results' in st.session_state:
            del st.session_state['results']
        st.rerun()

# Generate response
if generate_btn and user_prompt:

    # Determine model
    if "Qwen" in model_choice:
        model_name = "qwen3-coder:30b"
        model_type = "qwen"
    else:
        model_name = "gpt-oss:120b"
        model_type = "gpt-oss"

    with st.spinner(f"Generating using {mode}..."):
        try:
            start_time = time.time()

            if mode == "Disaggregated (DGX + Mac)":
                # Use disaggregated client
                client = DisaggregatedClient()
                response_text, metrics = client.generate(
                    model=model_name,
                    prompt=user_prompt,
                    max_tokens=max_tokens
                )

                # Store results
                st.session_state['results'] = {
                    'mode': 'Disaggregated',
                    'response': response_text,
                    'metrics': metrics
                }

            else:
                # Use Mac-only (local Ollama)
                # Determine which Mac to use based on model
                if model_type == "qwen":
                    mac_host = "169.254.150.102"  # Mac Studio 2
                    mac_name = "Mac Studio 2"
                else:
                    mac_host = "169.254.150.101"  # Mac Studio 1
                    mac_name = "Mac Studio 1"

                # Call local generation (bypass disaggregated)
                response = requests.post(
                    f"http://{mac_host}:8081/generate",
                    json={
                        'prompt': user_prompt,
                        'max_new_tokens': max_tokens,
                        'temperature': 0.2
                    },
                    timeout=300
                )

                if response.status_code == 200:
                    result = response.json()
                    total_time = result.get('decode_time', time.time() - start_time)

                    # Extract just the generated portion (response includes prompt)
                    full_text = result.get('generated_text', '')
                    generated_only = full_text[len(user_prompt):] if full_text.startswith(user_prompt) else full_text

                    st.session_state['results'] = {
                        'mode': f'Mac-only ({mac_name})',
                        'response': generated_only.strip(),
                        'metrics': {
                            'total_time': total_time,
                            'tokens_generated': result.get('tokens_generated', 0),
                            'speed': result.get('tokens_per_sec', 0),
                            'method': result.get('method', 'mac_local'),
                            'server': mac_name,
                            'prompt_tokens': result.get('metrics', {}).get('prompt_tokens', 0)
                        }
                    }
                else:
                    st.error(f"Mac generation failed: {response.status_code}")
                    st.code(response.text)

        except Exception as e:
            st.error(f"Generation failed: {e}")
            import traceback
            st.code(traceback.format_exc())

# Display results
if 'results' in st.session_state:
    st.markdown("---")
    st.subheader("📊 Comprehensive Performance Report")

    results = st.session_state['results']
    metrics = results['metrics']

    # Header with mode
    st.markdown(f"### {results['mode']}")

    # === SECTION 1: KEY METRICS ===
    st.markdown("#### ⚡ Key Performance Indicators")

    if results['mode'] == 'Disaggregated':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⏱️ Total Time", f"{metrics['total_time']:.2f}s")
        with col2:
            st.metric("🚀 Prefill Speed", f"{metrics['prefill_speed']:.1f} tok/s")
        with col3:
            st.metric("🎯 Decode Speed", f"{metrics.get('decode_speed', 0):.1f} tok/s")
        with col4:
            overall_speed = metrics['total_tokens'] / metrics['total_time'] if metrics['total_time'] > 0 else 0
            st.metric("📊 Overall", f"{overall_speed:.1f} tok/s")

    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⏱️ Total Time", f"{metrics['total_time']:.2f}s")
        with col2:
            st.metric("🚀 Generation Speed", f"{metrics['speed']:.1f} tok/s")
        with col3:
            st.metric("📝 Tokens Generated", metrics['tokens_generated'])
        with col4:
            prompt_tokens = metrics.get('prompt_tokens', 0)
            if prompt_tokens > 0:
                total_tokens = prompt_tokens + metrics['tokens_generated']
                st.metric("📊 Total Tokens", total_tokens)
            else:
                st.metric("📊 Total Tokens", "N/A")

    # === SECTION 2: PERFORMANCE BREAKDOWN ===
    st.markdown("---")
    st.markdown("#### 🔍 Performance Breakdown")

    if results['mode'] == 'Disaggregated':
        # Create two columns for side-by-side comparison
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🔧 Prefill Phase (DGX)**")
            st.write(f"- Server: {metrics['prefill_server']}")
            st.write(f"- Time: {metrics['prefill_time']:.3f}s")
            st.write(f"- Speed: {metrics['prefill_speed']:.1f} tok/s")
            st.write(f"- Tokens processed: {metrics['prompt_tokens']}")
            prefill_pct = (metrics['prefill_time'] / metrics['total_time'] * 100) if metrics['total_time'] > 0 else 0
            st.write(f"- % of total time: {prefill_pct:.1f}%")

        with col2:
            st.markdown("**🎨 Decode Phase (Mac)**")
            st.write(f"- Server: {metrics['decode_server']}")
            st.write(f"- Time: {metrics['decode_time']:.3f}s")
            st.write(f"- Speed: {metrics.get('decode_speed', 0):.1f} tok/s")
            st.write(f"- Tokens generated: {metrics['completion_tokens']}")
            decode_pct = (metrics['decode_time'] / metrics['total_time'] * 100) if metrics['total_time'] > 0 else 0
            st.write(f"- % of total time: {decode_pct:.1f}%")

        # Network transfer metrics
        st.markdown("**🌐 Network Transfer**")
        transfer_cols = st.columns(3)
        with transfer_cols[0]:
            st.metric("State Size", f"{metrics['state_size_mb']:.1f} MB")
        with transfer_cols[1]:
            # Estimate transfer time (10 Gb/s = 1250 MB/s)
            estimated_transfer_time = metrics['state_size_mb'] / 1250
            st.metric("Est. Transfer Time", f"{estimated_transfer_time:.3f}s")
        with transfer_cols[2]:
            bandwidth_used = metrics['state_size_mb'] * 8  # MB to Mb
            st.metric("Bandwidth Used", f"{bandwidth_used:.0f} Mb")

    else:
        st.markdown("**⚙️ Single-Phase Generation (Mac)**")
        st.write(f"- Server: {metrics['server']}")
        st.write(f"- Total time: {metrics['total_time']:.3f}s")
        st.write(f"- Speed: {metrics['speed']:.1f} tok/s")
        st.write(f"- Method: {metrics.get('method', 'unknown')}")

    # === SECTION 3: TOKEN ANALYSIS ===
    st.markdown("---")
    st.markdown("#### 📝 Token Analysis")

    if results['mode'] == 'Disaggregated':
        token_cols = st.columns(4)
        with token_cols[0]:
            st.metric("Input Tokens", metrics['prompt_tokens'])
        with token_cols[1]:
            st.metric("Output Tokens", metrics['completion_tokens'])
        with token_cols[2]:
            st.metric("Total Tokens", metrics['total_tokens'])
        with token_cols[3]:
            ratio = metrics['completion_tokens'] / metrics['prompt_tokens'] if metrics['prompt_tokens'] > 0 else 0
            st.metric("Output/Input Ratio", f"{ratio:.2f}x")
    else:
        token_cols = st.columns(3)
        with token_cols[0]:
            prompt_tokens = metrics.get('prompt_tokens', 0)
            st.metric("Input Tokens", prompt_tokens if prompt_tokens > 0 else "N/A")
        with token_cols[1]:
            st.metric("Output Tokens", metrics['tokens_generated'])
        with token_cols[2]:
            if prompt_tokens > 0:
                total = prompt_tokens + metrics['tokens_generated']
                st.metric("Total Tokens", total)
            else:
                st.metric("Total Tokens", f"~{metrics['tokens_generated']}")

    # === SECTION 4: EFFICIENCY METRICS ===
    st.markdown("---")
    st.markdown("#### 📈 Efficiency Metrics")

    eff_cols = st.columns(3)

    with eff_cols[0]:
        st.markdown("**⚡ Throughput**")
        if results['mode'] == 'Disaggregated':
            total_throughput = metrics['total_tokens'] / metrics['total_time']
            st.write(f"Overall: {total_throughput:.1f} tok/s")
            st.write(f"Prefill: {metrics['prefill_speed']:.1f} tok/s")
            st.write(f"Decode: {metrics.get('decode_speed', 0):.1f} tok/s")
        else:
            st.write(f"Overall: {metrics['speed']:.1f} tok/s")

    with eff_cols[1]:
        st.markdown("**💨 Speed Metrics**")
        if results['mode'] == 'Disaggregated':
            ms_per_token = (metrics['decode_time'] * 1000) / metrics['completion_tokens'] if metrics['completion_tokens'] > 0 else 0
            st.write(f"Latency: {ms_per_token:.1f} ms/token")
            tokens_per_minute = metrics.get('decode_speed', 0) * 60
            st.write(f"Decode rate: {tokens_per_minute:.0f} tok/min")
        else:
            ms_per_token = (metrics['total_time'] * 1000) / metrics['tokens_generated'] if metrics['tokens_generated'] > 0 else 0
            st.write(f"Latency: {ms_per_token:.1f} ms/token")
            tokens_per_minute = metrics['speed'] * 60
            st.write(f"Rate: {tokens_per_minute:.0f} tok/min")

    with eff_cols[2]:
        st.markdown("**🎯 Utilization**")
        if results['mode'] == 'Disaggregated':
            # Calculate efficiency scores
            prefill_efficiency = metrics['prefill_speed'] / 300 * 100  # Assuming 300 tok/s is max
            decode_efficiency = metrics.get('decode_speed', 0) / 50 * 100  # Assuming 50 tok/s is max
            st.write(f"Prefill: {min(prefill_efficiency, 100):.0f}%")
            st.write(f"Decode: {min(decode_efficiency, 100):.0f}%")
        else:
            mac_efficiency = metrics['speed'] / 50 * 100  # Assuming 50 tok/s is max for Mac standalone
            st.write(f"Mac: {min(mac_efficiency, 100):.0f}%")

    # === SECTION 5: COMPARISON (if both modes tested) ===
    if 'comparison' in st.session_state:
        st.markdown("---")
        st.markdown("#### ⚖️ Mode Comparison")

        comp = st.session_state['comparison']
        comp_cols = st.columns(4)

        with comp_cols[0]:
            speedup = comp['mac_time'] / comp['disagg_time'] if comp['disagg_time'] > 0 else 1
            st.metric("Speedup", f"{speedup:.2f}x", delta=f"{(speedup-1)*100:.0f}% faster" if speedup > 1 else "slower")

        with comp_cols[1]:
            time_saved = comp['mac_time'] - comp['disagg_time']
            st.metric("Time Saved", f"{time_saved:.2f}s", delta="disaggregated" if time_saved > 0 else "mac")

        with comp_cols[2]:
            throughput_diff = ((comp['disagg_speed'] / comp['mac_speed']) - 1) * 100
            st.metric("Throughput Gain", f"{throughput_diff:+.0f}%")

        with comp_cols[3]:
            # Cost per 1000 tokens (assuming time = cost proxy)
            disagg_cost = (comp['disagg_time'] / comp.get('disagg_tokens', 1)) * 1000
            mac_cost = (comp['mac_time'] / comp.get('mac_tokens', 1)) * 1000
            cost_diff = ((mac_cost / disagg_cost) - 1) * 100 if disagg_cost > 0 else 0
            st.metric("Cost Efficiency", f"{cost_diff:+.0f}%", delta="disaggregated better" if cost_diff > 0 else "mac better")

    # === SECTION 6: RESPONSE ===
    st.markdown("---")
    st.subheader("💬 Generated Response")
    with st.expander("📄 View Full Response", expanded=True):
        st.markdown(results['response'])

    # === SECTION 7: RAW DATA ===
    st.markdown("---")
    with st.expander("🔧 Technical Details & Raw Metrics"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**System Info:**")
            st.write(f"- Mode: {results['mode']}")
            st.write(f"- Method: {metrics.get('method', 'N/A')}")
            if results['mode'] == 'Disaggregated':
                st.write(f"- Prefill: {metrics['prefill_server']}")
                st.write(f"- Decode: {metrics['decode_server']}")
            else:
                st.write(f"- Server: {metrics['server']}")

        with col2:
            st.markdown("**Raw Metrics:**")
            st.json(metrics)

    # Store for comparison
    if 'mac_time' not in st.session_state:
        st.session_state['mac_time'] = None
    if 'disagg_time' not in st.session_state:
        st.session_state['disagg_time'] = None

    # Update comparison data
    if results['mode'] == 'Disaggregated':
        st.session_state['disagg_time'] = metrics['total_time']
        st.session_state['disagg_speed'] = metrics['total_tokens'] / metrics['total_time']
        st.session_state['disagg_tokens'] = metrics['total_tokens']
    else:
        st.session_state['mac_time'] = metrics['total_time']
        st.session_state['mac_speed'] = metrics['speed']
        st.session_state['mac_tokens'] = metrics.get('prompt_tokens', 0) + metrics['tokens_generated']

    # Enable comparison if both have been tested
    if st.session_state.get('mac_time') and st.session_state.get('disagg_time'):
        if 'comparison' not in st.session_state:
            st.session_state['comparison'] = {}
        st.session_state['comparison'].update({
            'mac_time': st.session_state['mac_time'],
            'disagg_time': st.session_state['disagg_time'],
            'mac_speed': st.session_state['mac_speed'],
            'disagg_speed': st.session_state['disagg_speed'],
            'mac_tokens': st.session_state.get('mac_tokens', 0),
            'disagg_tokens': st.session_state.get('disagg_tokens', 0)
        })

    # === SECTION 8: EXPORT & HISTORY ===
    st.markdown("---")
    st.markdown("#### 📥 Export Performance Data")

    export_cols = st.columns(3)

    with export_cols[0]:
        # Export current metrics as JSON
        metrics_json = json.dumps(metrics, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=metrics_json,
            file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

    with export_cols[1]:
        # Export as CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        # Header
        writer.writerow(['Metric', 'Value'])

        # Flatten metrics for CSV
        for key, value in metrics.items():
            if isinstance(value, (int, float, str)):
                writer.writerow([key, value])

        csv_data = csv_buffer.getvalue()
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with export_cols[2]:
        # Performance summary report
        report = f"""# Performance Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Mode
{results['mode']}

## Key Metrics
- Total Time: {metrics['total_time']:.2f}s
"""
        if results['mode'] == 'Disaggregated':
            report += f"""- Prefill Speed: {metrics['prefill_speed']:.1f} tok/s
- Decode Speed: {metrics.get('decode_speed', 0):.1f} tok/s
- State Size: {metrics['state_size_mb']:.1f} MB
- Total Tokens: {metrics['total_tokens']}
"""
        else:
            report += f"""- Generation Speed: {metrics['speed']:.1f} tok/s
- Tokens Generated: {metrics['tokens_generated']}
"""

        st.download_button(
            label="📝 Download Report",
            data=report,
            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    # Performance history tracking
    if 'performance_history' not in st.session_state:
        st.session_state['performance_history'] = []

    # Add current result to history
    history_entry = {
        'timestamp': datetime.now().isoformat(),
        'mode': results['mode'],
        'total_time': metrics['total_time'],
        'prompt_length': len(user_prompt) if 'user_prompt' in dir() else 0,
    }

    if results['mode'] == 'Disaggregated':
        history_entry.update({
            'prefill_speed': metrics['prefill_speed'],
            'decode_speed': metrics.get('decode_speed', 0),
            'total_tokens': metrics['total_tokens']
        })
    else:
        history_entry.update({
            'speed': metrics['speed'],
            'tokens': metrics['tokens_generated']
        })

    # Check if this is a new entry (not a page refresh)
    if not st.session_state['performance_history'] or \
       st.session_state['performance_history'][-1]['timestamp'] != history_entry['timestamp']:
        st.session_state['performance_history'].append(history_entry)

    # Show performance history if available
    if len(st.session_state['performance_history']) > 1:
        st.markdown("---")
        st.markdown("#### 📊 Performance History")

        st.write(f"**Tests run this session:** {len(st.session_state['performance_history'])}")

        # Summary stats
        disagg_tests = [h for h in st.session_state['performance_history'] if 'Disaggregated' in h['mode']]
        mac_tests = [h for h in st.session_state['performance_history'] if 'Mac-only' in h['mode']]

        stats_cols = st.columns(2)

        if disagg_tests:
            with stats_cols[0]:
                st.markdown("**Disaggregated Stats:**")
                avg_time = sum(h['total_time'] for h in disagg_tests) / len(disagg_tests)
                avg_prefill = sum(h['prefill_speed'] for h in disagg_tests) / len(disagg_tests)
                st.write(f"- Tests: {len(disagg_tests)}")
                st.write(f"- Avg time: {avg_time:.2f}s")
                st.write(f"- Avg prefill: {avg_prefill:.1f} tok/s")

        if mac_tests:
            with stats_cols[1]:
                st.markdown("**Mac-only Stats:**")
                avg_time = sum(h['total_time'] for h in mac_tests) / len(mac_tests)
                avg_speed = sum(h['speed'] for h in mac_tests) / len(mac_tests)
                st.write(f"- Tests: {len(mac_tests)}")
                st.write(f"- Avg time: {avg_time:.2f}s")
                st.write(f"- Avg speed: {avg_speed:.1f} tok/s")

        # Option to clear history
        if st.button("🗑️ Clear Performance History"):
            st.session_state['performance_history'] = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
### About This Test App

This application allows you to compare two inference modes:

1. **Mac-only (Standalone)**: All processing happens locally on a Mac Studio
   - Simpler architecture
   - Good for small prompts
   - Single machine processes everything

2. **Disaggregated (DGX + Mac)**: Splits prefill and decode phases
   - Prefill: DGX Spark (CUDA acceleration, 200+ tok/s)
   - Decode: Mac Studio (Metal acceleration, 10-31 tok/s)
   - 2x speedup for large prompts (2000+ tokens)
   - Better resource utilization

**When to use disaggregated:**
- Large prompts (grading assignments with lots of code)
- Batch processing multiple students
- When you need maximum performance

**When to use Mac-only:**
- Small prompts (<100 tokens)
- Simple queries
- Single-shot testing
""")
