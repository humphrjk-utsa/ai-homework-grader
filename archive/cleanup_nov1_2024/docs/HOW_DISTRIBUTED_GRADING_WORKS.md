# How Distributed Grading Works

## 🤔 Your Question: Do the models talk to each other?

**Answer: No!** They work in **parallel** but **independently**.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit App (Orchestrator)           │
│                                                          │
│  1. Receives student submission                         │
│  2. Prepares TWO different prompts                      │
│  3. Sends them to BOTH servers at the SAME TIME        │
│  4. Waits for BOTH responses                            │
│  5. Combines the results                                │
└─────────────────────────────────────────────────────────┘
                    ↓                    ↓
        ┌───────────────────┐  ┌───────────────────┐
        │   Mac Studio 2    │  │   Mac Studio 1    │
        │   (Qwen Model)    │  │  (GPT-OSS Model)  │
        │                   │  │                   │
        │ 🔧 Code Analysis  │  │ 📝 Feedback Gen   │
        │                   │  │                   │
        │ Gets: Student     │  │ Gets: Student     │
        │       code +      │  │       code +      │
        │       rubric      │  │       Qwen's      │
        │                   │  │       analysis    │
        │ Returns:          │  │                   │
        │ - Technical score │  │ Returns:          │
        │ - Code issues     │  │ - Written feedback│
        │ - Suggestions     │  │ - Encouragement   │
        └───────────────────┘  └───────────────────┘
                    ↓                    ↓
        ┌─────────────────────────────────────────┐
        │     Results Combined in Streamlit       │
        │                                          │
        │  Final Grade = Technical + Reflection   │
        │  Report = Code Analysis + Feedback      │
        └─────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Process

### **Step 1: Student Submits Homework**
```
Student uploads: homework_assignment_4.ipynb
```

### **Step 2: Streamlit Prepares TWO Prompts**

**Prompt A (for Qwen - Code Analysis):**
```
Analyze this R code for Assignment 4:
[student's code here]

Rubric:
- Data transformation: 15 points
- Mutate operations: 10 points
...

Provide technical analysis and score.
```

**Prompt B (for GPT-OSS - Feedback):**
```
Based on this code analysis:
[Qwen's analysis will go here]

And this student code:
[student's code here]

Write encouraging feedback for the student.
```

### **Step 3: Parallel Execution**

```python
# Both requests sent AT THE SAME TIME
with ThreadPoolExecutor(max_workers=2) as executor:
    qwen_future = executor.submit(ask_qwen, prompt_A)
    gpt_future = executor.submit(ask_gpt, prompt_B)
    
    # Wait for BOTH to finish
    qwen_result = qwen_future.result()
    gpt_result = gpt_future.result()
```

**Timeline:**
```
Time 0s:  Both requests sent simultaneously
Time 30s: Qwen finishes (code analysis)
Time 45s: GPT-OSS finishes (feedback)
Total:    45s (not 75s!)
```

### **Step 4: Combine Results**

```python
final_grade = {
    'technical_score': qwen_result['score'],      # From Qwen
    'code_analysis': qwen_result['analysis'],     # From Qwen
    'feedback': gpt_result['feedback'],           # From GPT-OSS
    'total_score': calculate_total(qwen, gpt)
}
```

---

## 🔄 Do They Communicate?

### **No Direct Communication:**
```
❌ Qwen does NOT ask GPT-OSS questions
❌ GPT-OSS does NOT ask Qwen questions
❌ They do NOT share information during processing
```

### **Sequential Information Flow:**
```
✅ Streamlit asks Qwen first
✅ Streamlit gets Qwen's answer
✅ Streamlit includes Qwen's answer in GPT-OSS prompt
✅ GPT-OSS uses that info to write better feedback
```

---

## 💡 Why This Design?

### **Division of Labor:**

**Qwen (Code Expert):**
- Specialized in code analysis
- Faster at technical evaluation
- Identifies syntax errors, logic issues
- Assigns technical scores

**GPT-OSS (Communication Expert):**
- Better at natural language
- Writes encouraging feedback
- Explains concepts clearly
- Provides learning guidance

### **Parallel Processing Benefits:**

**Without Parallel (Sequential):**
```
Qwen:     30 seconds
GPT-OSS:  45 seconds
Total:    75 seconds ⏰
```

**With Parallel:**
```
Qwen:     30 seconds  ┐
GPT-OSS:  45 seconds  ├─ Running simultaneously
Total:    45 seconds ⚡ (40% faster!)
```

---

## 🎯 Real Example

### **Student Submission:**
```r
# Student's code
sales_data %>%
  mutate(profit = revenue - cost) %>%
  group_by(region) %>%
  summarize(total_profit = sum(profit))
```

### **What Happens:**

**1. Qwen Analyzes (Mac Studio 2):**
```
Technical Analysis:
✅ Correct use of mutate()
✅ Proper pipe syntax
✅ Good variable naming
⚠️  Missing na.rm=TRUE in sum()

Score: 28/30 points
```

**2. GPT-OSS Writes Feedback (Mac Studio 1):**
```
Great work on your data transformation! Your use of 
mutate() and group_by() shows solid understanding.

One suggestion: Add na.rm=TRUE to your sum() function
to handle missing values gracefully.

Overall: Excellent submission! Score: 28/30
```

**3. Combined Result:**
```
Technical Score: 28/30 (from Qwen)
Feedback: [GPT-OSS's encouraging message]
Total Time: 45 seconds (parallel processing)
```

---

## 🔧 Technical Details

### **How Prompts Are Structured:**

**Qwen's Prompt (Technical):**
```python
prompt = f"""
You are a technical code reviewer.
Analyze this code against the rubric:

CODE:
{student_code}

RUBRIC:
{rubric_criteria}

Provide:
1. Technical score
2. Code issues
3. Suggestions
"""
```

**GPT-OSS's Prompt (Feedback):**
```python
prompt = f"""
You are an encouraging instructor.

TECHNICAL ANALYSIS:
{qwen_analysis}

STUDENT CODE:
{student_code}

Write supportive feedback that:
1. Acknowledges strengths
2. Explains issues clearly
3. Encourages improvement
"""
```

### **Why GPT-OSS Gets Qwen's Analysis:**

This is **one-way information flow**, not a conversation:

```
Qwen → Analysis → Streamlit → Includes in GPT prompt → GPT-OSS
```

**Benefits:**
- GPT-OSS knows what technical issues were found
- Can explain them in student-friendly language
- Avoids contradicting the technical analysis
- Provides consistent feedback

---

## 📊 Performance Metrics

### **Current Setup:**
- **Qwen:** ~30-40 seconds (code analysis)
- **GPT-OSS:** ~40-50 seconds (feedback)
- **Parallel Time:** ~45-50 seconds (max of the two)
- **Efficiency:** 1.4-1.6x speedup

### **If Sequential:**
- **Total:** ~75-90 seconds
- **Efficiency:** 1.0x (baseline)

### **Speedup Calculation:**
```
Sequential time: 75s
Parallel time:   45s
Speedup:        75/45 = 1.67x faster
```

---

## 🎓 Summary

### **Key Points:**

1. **No Inter-Model Communication**
   - Models don't talk to each other
   - They work independently

2. **Orchestrated by Streamlit**
   - Streamlit sends prompts to both
   - Waits for both responses
   - Combines results

3. **Sequential Information Flow**
   - Qwen analyzes first
   - Result included in GPT-OSS prompt
   - One-way information transfer

4. **Parallel Execution**
   - Both run at the same time
   - 40-60% faster than sequential
   - Better resource utilization

5. **Specialized Roles**
   - Qwen: Technical analysis
   - GPT-OSS: Student feedback
   - Each does what it's best at

---

## 🔮 Could They Talk to Each Other?

**Technically possible but not beneficial:**

```python
# Hypothetical (not implemented)
qwen_analysis = ask_qwen(code)
gpt_question = ask_gpt("What should I ask Qwen?")
qwen_answer = ask_qwen(gpt_question)
gpt_feedback = ask_gpt(qwen_answer)
```

**Why we don't do this:**
- ❌ Much slower (sequential)
- ❌ More complex
- ❌ Higher chance of errors
- ❌ No real benefit

**Current approach is better:**
- ✅ Faster (parallel)
- ✅ Simpler
- ✅ More reliable
- ✅ Clear separation of concerns

---

## 💡 Think of It Like...

**Restaurant Kitchen:**
```
Chef 1 (Qwen):     Cooks the main dish
Chef 2 (GPT-OSS):  Prepares the presentation

They work at the same time, but:
- Don't talk during cooking
- Each has their specialty
- Head chef (Streamlit) coordinates
- Final plate combines both efforts
```

**Not like a conversation:**
```
❌ Person A asks Person B a question
❌ Person B responds
❌ Person A asks follow-up
❌ Back and forth dialogue
```

**More like parallel workers:**
```
✅ Boss assigns two tasks
✅ Worker 1 does task A
✅ Worker 2 does task B
✅ Both work simultaneously
✅ Boss combines results
```

---

That's how distributed grading works! Two specialized models working in parallel, coordinated by Streamlit, but not talking to each other. 🚀
