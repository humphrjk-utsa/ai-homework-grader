#!/usr/bin/env python3
"""
Grade assignments using the systematic validator
This replaces the old validator with evidence-based grading
"""

import sys
import json
from pathlib import Path
from validators.assignment_6_systematic_validator import Assignment6SystematicValidator


def grade_submission(notebook_path: str, output_path: str = None):
    """Grade a single submission"""
    print(f"\n{'='*80}")
    print(f"GRADING: {notebook_path}")
    print(f"{'='*80}")
    
    # Validate
    validator = Assignment6SystematicValidator()
    result = validator.validate_notebook(notebook_path)
    
    # Generate report
    report = validator.generate_detailed_report(result)
    print(report)
    
    # Save result if output path provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n✅ Results saved to: {output_path}")
    
    return result


def grade_all_submissions(submissions_dir: str = "submissions/12", output_dir: str = "grading_results"):
    """Grade all submissions in a directory"""
    submissions_path = Path(submissions_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Find all notebooks
    notebooks = list(submissions_path.glob("*.ipynb"))
    print(f"\n🔍 Found {len(notebooks)} submissions in {submissions_dir}")
    
    results = []
    
    for notebook in sorted(notebooks):
        student_name = notebook.stem
        output_file = output_path / f"{student_name}_result.json"
        
        try:
            result = grade_submission(str(notebook), str(output_file))
            results.append({
                "student": student_name,
                "score": result['final_score'],
                "grade": result['grade'],
                "file": str(notebook)
            })
        except Exception as e:
            print(f"\n❌ ERROR grading {student_name}: {e}")
            results.append({
                "student": student_name,
                "score": 0,
                "grade": "ERROR",
                "error": str(e),
                "file": str(notebook)
            })
    
    # Generate summary
    print(f"\n{'='*80}")
    print("GRADING SUMMARY")
    print(f"{'='*80}")
    print(f"\n{'Student':<40} {'Score':>10} {'Grade':>8}")
    print("-" * 80)
    
    for r in sorted(results, key=lambda x: x['score'], reverse=True):
        print(f"{r['student']:<40} {r['score']:>10.1f} {r['grade']:>8}")
    
    # Statistics
    scores = [r['score'] for r in results if r['score'] > 0]
    if scores:
        print(f"\n{'='*80}")
        print("STATISTICS")
        print(f"{'='*80}")
        print(f"Total submissions: {len(results)}")
        print(f"Average score: {sum(scores)/len(scores):.1f}")
        print(f"Highest score: {max(scores):.1f}")
        print(f"Lowest score: {min(scores):.1f}")
        
        # Grade distribution
        grade_counts = {}
        for r in results:
            grade = r['grade']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        print(f"\nGrade Distribution:")
        for grade in ['A', 'B', 'C', 'D', 'F', 'ERROR']:
            count = grade_counts.get(grade, 0)
            if count > 0:
                print(f"  {grade}: {count} ({100*count/len(results):.1f}%)")
    
    # Save summary
    summary_file = output_path / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "results": results,
            "statistics": {
                "total": len(results),
                "average": sum(scores)/len(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "min": min(scores) if scores else 0,
                "grade_distribution": grade_counts
            }
        }, f, indent=2)
    
    print(f"\n✅ Summary saved to: {summary_file}")
    
    return results


def compare_with_old_scores(new_results_dir: str = "grading_results", old_scores_file: str = None):
    """Compare new systematic scores with old scores"""
    if not old_scores_file:
        print("No old scores file provided for comparison")
        return
    
    # Load old scores
    with open(old_scores_file, 'r') as f:
        old_data = json.load(f)
    
    # Load new results
    new_results = {}
    results_path = Path(new_results_dir)
    for result_file in results_path.glob("*_result.json"):
        with open(result_file, 'r') as f:
            data = json.load(f)
            student_name = result_file.stem.replace('_result', '')
            new_results[student_name] = data['final_score']
    
    # Compare
    print(f"\n{'='*80}")
    print("COMPARISON: OLD vs NEW SCORES")
    print(f"{'='*80}")
    print(f"\n{'Student':<40} {'Old':>10} {'New':>10} {'Diff':>10}")
    print("-" * 80)
    
    differences = []
    for student, new_score in sorted(new_results.items()):
        # Try to find old score
        old_score = None
        for old_entry in old_data.get('results', []):
            if student.lower() in old_entry.get('student', '').lower():
                old_score = old_entry.get('score', 0)
                break
        
        if old_score is not None:
            diff = new_score - old_score
            differences.append(diff)
            diff_str = f"{diff:+.1f}"
            print(f"{student:<40} {old_score:>10.1f} {new_score:>10.1f} {diff_str:>10}")
    
    if differences:
        print(f"\n{'='*80}")
        print("DIFFERENCE STATISTICS")
        print(f"{'='*80}")
        print(f"Average difference: {sum(differences)/len(differences):+.1f} points")
        print(f"Students scored higher: {sum(1 for d in differences if d > 0)}")
        print(f"Students scored lower: {sum(1 for d in differences if d < 0)}")
        print(f"Students scored same: {sum(1 for d in differences if d == 0)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Grade assignments with systematic validator")
    parser.add_argument("--file", help="Grade a single file")
    parser.add_argument("--dir", default="submissions/12", help="Grade all files in directory")
    parser.add_argument("--output", default="grading_results", help="Output directory")
    parser.add_argument("--compare", help="Compare with old scores file")
    
    args = parser.parse_args()
    
    if args.file:
        # Grade single file
        grade_submission(args.file)
    else:
        # Grade all submissions
        results = grade_all_submissions(args.dir, args.output)
        
        # Compare if requested
        if args.compare:
            compare_with_old_scores(args.output, args.compare)
