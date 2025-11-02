# Rubric Backup - October 31, 2024 7:14 PM

## Purpose
Backup created before implementing stricter scoring rules to address score clustering problem.

## Problem Being Fixed
- Scores clustering around 85-87%
- No differentiation between good and excellent work
- AI too lenient with incomplete work
- Grade inflation

## Files Backed Up
- assignment_1_rubric.json
- assignment_2_rubric.json
- assignment_3_rubric.json (all versions)
- assignment_4_rubric.json (both versions)
- assignment_5_rubric.json
- assignment_6_rubric.json

## Changes Being Applied
1. Stricter scoring rules (no output = 0 points)
2. Reweighted categories (technical 40%, not 25%)
3. Completion-based maximum scores
4. Explicit penalties for incomplete work
5. Force score differentiation

## To Restore
If needed, copy files from this backup folder back to rubrics/:
```bash
cp rubrics/backup_20251031_191430/*.json rubrics/
```

## Current Score Distribution (Before Changes)
```
Assignment 2:  86.4% average
Assignment 5:  74.7% average
Assignment 6:  85.5% average
Assignment 8:  86.7% average
Assignment 10: 85.1% average
Assignment 12: 85.9% average
```

## Target Distribution (After Changes)
```
90-100%: 15% (excellent)
80-89%:  30% (good)
70-79%:  35% (adequate)
60-69%:  15% (poor)
0-59%:   5%  (failing)
```
