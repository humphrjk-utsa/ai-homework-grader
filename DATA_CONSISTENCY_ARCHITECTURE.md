# Data Consistency Architecture - Single Source of Truth

## Overview

The Enhanced AI Training Review Interface implements a robust **Single Source of Truth** architecture to ensure data consistency across all database operations. This document outlines the data flow, authoritative sources, and consistency mechanisms.

## 🏗️ Database Architecture

### Primary Tables (Authoritative Sources)

1. **`human_feedback` table** - **AUTHORITATIVE** for human reviews
   ```sql
   CREATE TABLE human_feedback (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       submission_id INTEGER UNIQUE NOT NULL,
       human_score REAL NOT NULL CHECK (human_score >= 0 AND human_score <= 37.5),
       human_feedback TEXT,
       instructor_id TEXT DEFAULT 'instructor',
       created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE
   );
   ```

2. **`grading_results` table** - **AUTHORITATIVE** for AI scores
   ```sql
   CREATE TABLE grading_results (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       submission_id INTEGER,
       final_score REAL,
       final_score_percentage REAL,
       grading_method TEXT,
       comprehensive_feedback TEXT,
       FOREIGN KEY (submission_id) REFERENCES submissions (id)
   );
   ```

### Derived Tables (Computed Fields)

3. **`submissions` table** - Contains **DERIVED** fields for quick access
   ```sql
   -- These fields are derived from authoritative sources:
   final_score REAL,      -- Computed from human_feedback OR grading_results
   human_score REAL,      -- Copy of human_feedback.human_score (for compatibility)
   human_feedback TEXT    -- Copy of human_feedback.human_feedback (for compatibility)
   ```

## 📊 Data Flow Architecture

### Single Source of Truth Rules

1. **Human Scores**: `human_feedback` table is the **ONLY** authoritative source
2. **AI Scores**: `grading_results` table is the **ONLY** authoritative source  
3. **Final Scores**: Computed as `COALESCE(human_score, ai_score)` from authoritative sources
4. **Backward Compatibility**: `submissions` table fields are **derived copies** only

### Data Write Operations

#### 1. Save Human Feedback
```python
def save_human_feedback(submission_id, score, feedback):
    # TRANSACTION ensures atomicity
    BEGIN TRANSACTION
    
    # 1. PRIMARY: Write to authoritative source
    INSERT OR REPLACE INTO human_feedback (submission_id, human_score, human_feedback)
    VALUES (submission_id, score, feedback)
    
    # 2. DERIVED: Update computed field for quick access
    UPDATE submissions SET final_score = score WHERE id = submission_id
    
    # 3. COMPATIBILITY: Update legacy fields
    UPDATE submissions SET human_score = score, human_feedback = feedback WHERE id = submission_id
    
    COMMIT
```

#### 2. Reset to AI Score
```python
def reset_to_ai_score(submission_id):
    BEGIN TRANSACTION
    
    # 1. Remove from authoritative human source
    DELETE FROM human_feedback WHERE submission_id = submission_id
    
    # 2. Reset derived field to AI score
    UPDATE submissions SET final_score = (
        SELECT COALESCE(gr.final_score, submissions.ai_score, 0)
        FROM grading_results gr WHERE gr.submission_id = submissions.id
    ) WHERE id = submission_id
    
    # 3. Clear compatibility fields
    UPDATE submissions SET human_score = NULL, human_feedback = NULL WHERE id = submission_id
    
    COMMIT
```

## 🔍 Data Consistency View

### Training Report View (Single Source of Truth)
```sql
CREATE VIEW training_report_view AS
SELECT 
    s.id as submission_id,
    -- AI Score: Always from grading_results (authoritative)
    COALESCE(gr.final_score, s.ai_score, 0) as ai_score,
    -- Human Score: Always from human_feedback (authoritative)  
    hf.human_score,
    -- Final Score: Human if exists, otherwise AI (computed from authoritative sources)
    COALESCE(hf.human_score, gr.final_score, s.ai_score, 0) as final_score,
    -- Review Status: Based on authoritative sources
    CASE 
        WHEN hf.human_score IS NULL THEN 'AI Only'
        WHEN hf.human_score > COALESCE(gr.final_score, s.ai_score, 0) THEN 'Boosted'
        WHEN hf.human_score < COALESCE(gr.final_score, s.ai_score, 0) THEN 'Reduced'
        ELSE 'Confirmed'
    END as review_status
FROM submissions s
LEFT JOIN grading_results gr ON s.id = gr.submission_id  -- Authoritative AI scores
LEFT JOIN human_feedback hf ON s.id = hf.submission_id   -- Authoritative human scores
```

## ✅ Data Validation & Consistency

### Automatic Validation
The system includes automatic data consistency validation:

```python
def validate_data_consistency():
    """Validates and fixes any data inconsistencies"""
    
    # Check that derived fields match authoritative sources
    for submission in all_submissions:
        expected_final_score = human_score if human_score else ai_score
        
        if submission.final_score != expected_final_score:
            # FIX: Update derived field to match authoritative source
            UPDATE submissions SET final_score = expected_final_score
            
        if submission.human_score != authoritative_human_score:
            # FIX: Update compatibility field to match authoritative source
            UPDATE submissions SET human_score = authoritative_human_score
```

### Consistency Guarantees

1. **Transactional Integrity**: All multi-table operations use database transactions
2. **Referential Integrity**: Foreign key constraints ensure data relationships
3. **Automatic Validation**: Built-in validation detects and fixes inconsistencies
4. **Unique Constraints**: Prevent duplicate human feedback entries
5. **Check Constraints**: Enforce score ranges (0-37.5)

## 🚀 Benefits of This Architecture

### 1. **Data Integrity**
- Single authoritative source for each data type
- Automatic consistency validation and repair
- Transactional operations prevent partial updates

### 2. **Performance**
- Derived fields in `submissions` table for quick access
- View provides computed fields without complex joins in application code
- Indexes on authoritative tables for fast lookups

### 3. **Backward Compatibility**
- Legacy code can still access `submissions.human_score`
- Gradual migration path from old to new architecture
- No breaking changes to existing interfaces

### 4. **Auditability**
- Clear data lineage from authoritative sources
- Timestamps track when human reviews were made
- Instructor ID tracks who made changes

### 5. **Reliability**
- Automatic detection and repair of inconsistencies
- Comprehensive test coverage validates all operations
- Error handling with rollback on failures

## 🧪 Testing & Validation

The system includes comprehensive tests that verify:

1. **Data Consistency Validation**: Detects and fixes inconsistencies
2. **Single Source of Truth**: Ensures authoritative sources are respected
3. **View Consistency**: Validates computed fields match expectations
4. **Transaction Integrity**: Verifies atomic operations
5. **Error Recovery**: Tests rollback on failures

### Running Tests
```bash
python test_data_consistency.py
```

## 📋 Best Practices

### For Developers
1. **Always use the training interface methods** - Don't write directly to database
2. **Use transactions** for multi-table operations
3. **Validate data** after bulk operations
4. **Test consistency** after making schema changes

### For Database Operations
1. **Read from authoritative sources** when accuracy is critical
2. **Use the view** for reporting and display purposes
3. **Run validation** periodically to catch any drift
4. **Monitor logs** for consistency warnings

## 🔧 Maintenance

### Regular Maintenance Tasks
1. **Data Validation**: Run `validate_data_consistency()` weekly
2. **Cleanup**: Remove old training statistics (configurable retention)
3. **Monitoring**: Check logs for consistency warnings
4. **Backup**: Regular backups of authoritative tables

### Schema Evolution
When adding new fields:
1. Add to authoritative table first
2. Update view definition
3. Add derived fields if needed for performance
4. Update validation logic
5. Run consistency tests

This architecture ensures that the Enhanced AI Training Review Interface maintains perfect data consistency while providing excellent performance and backward compatibility.