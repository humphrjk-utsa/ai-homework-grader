#!/usr/bin/env python3
"""
Correction Pattern Analyzer
Analyzes patterns in human corrections to improve AI grading accuracy
"""

import sqlite3
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import json

class CorrectionAnalyzer:
    """Analyzes patterns in human grade corrections"""
    
    def __init__(self, db_path: str = "grading_database.db"):
        self.db_path = db_path
    
    def get_corrections(self, assignment_id: int = None) -> pd.DataFrame:
        """Get all submissions where human corrected the AI score"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                s.id,
                s.assignment_id,
                a.name as assignment_name,
                s.student_id,
                st.name as student_name,
                s.ai_score,
                s.human_score,
                s.final_score,
                s.ai_feedback,
                s.human_feedback,
                (s.human_score - s.ai_score) as score_diff,
                ((s.human_score - s.ai_score) / s.ai_score * 100) as percent_diff
            FROM submissions s
            LEFT JOIN assignments a ON s.assignment_id = a.id
            LEFT JOIN students st ON s.student_id = st.id
            WHERE s.human_score IS NOT NULL
                AND s.ai_score IS NOT NULL
                AND s.human_score != s.ai_score
        """
        
        if assignment_id:
            query += f" AND s.assignment_id = {assignment_id}"
        
        query += " ORDER BY s.graded_date DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def analyze_patterns(self, assignment_id: int = None) -> Dict:
        """Analyze correction patterns to identify systematic AI biases"""
        corrections = self.get_corrections(assignment_id)
        
        if corrections.empty:
            return {
                'total_corrections': 0,
                'message': 'No corrections found'
            }
        
        analysis = {
            'total_corrections': len(corrections),
            'avg_score_diff': corrections['score_diff'].mean(),
            'median_score_diff': corrections['score_diff'].median(),
            'avg_percent_diff': corrections['percent_diff'].mean(),
            'median_percent_diff': corrections['percent_diff'].median(),
            'over_scored_count': len(corrections[corrections['score_diff'] < 0]),
            'under_scored_count': len(corrections[corrections['score_diff'] > 0]),
            'over_score_percentage': (len(corrections[corrections['score_diff'] < 0]) / len(corrections) * 100),
            'under_score_percentage': (len(corrections[corrections['score_diff'] > 0]) / len(corrections) * 100),
        }
        
        # Identify common patterns
        analysis['patterns'] = self._identify_patterns(corrections)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _identify_patterns(self, corrections: pd.DataFrame) -> List[Dict]:
        """Identify specific patterns in corrections"""
        patterns = []
        
        # Pattern 1: Consistent over-scoring
        if corrections['score_diff'].mean() < -2:
            patterns.append({
                'type': 'over_scoring',
                'severity': 'high' if corrections['score_diff'].mean() < -5 else 'medium',
                'description': f"AI consistently over-scores by {abs(corrections['score_diff'].mean()):.1f} points on average",
                'affected_count': len(corrections[corrections['score_diff'] < -2])
            })
        
        # Pattern 2: Consistent under-scoring
        if corrections['score_diff'].mean() > 2:
            patterns.append({
                'type': 'under_scoring',
                'severity': 'high' if corrections['score_diff'].mean() > 5 else 'medium',
                'description': f"AI consistently under-scores by {corrections['score_diff'].mean():.1f} points on average",
                'affected_count': len(corrections[corrections['score_diff'] > 2])
            })
        
        # Pattern 3: Large variance (inconsistent grading)
        if corrections['score_diff'].std() > 5:
            patterns.append({
                'type': 'inconsistent',
                'severity': 'medium',
                'description': f"AI grading is inconsistent (std dev: {corrections['score_diff'].std():.1f})",
                'affected_count': len(corrections)
            })
        
        # Pattern 4: Extreme corrections (>10 points difference)
        extreme = corrections[abs(corrections['score_diff']) > 10]
        if len(extreme) > 0:
            patterns.append({
                'type': 'extreme_corrections',
                'severity': 'high',
                'description': f"{len(extreme)} submissions had corrections >10 points",
                'affected_count': len(extreme),
                'examples': extreme[['student_name', 'ai_score', 'human_score', 'score_diff']].head(3).to_dict('records')
            })
        
        return patterns
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on patterns"""
        recommendations = []
        
        # Over-scoring recommendations
        if analysis['over_score_percentage'] > 60:
            recommendations.append(
                f"⚠️ AI over-scores {analysis['over_score_percentage']:.0f}% of the time. "
                "Consider adding stricter completion requirements to prompts."
            )
            recommendations.append(
                f"💡 Reduce AI scores by {abs(analysis['avg_score_diff']):.1f} points as a baseline adjustment."
            )
        
        # Under-scoring recommendations
        if analysis['under_score_percentage'] > 60:
            recommendations.append(
                f"⚠️ AI under-scores {analysis['under_score_percentage']:.0f}% of the time. "
                "Consider relaxing prompt requirements or giving more credit for partial work."
            )
        
        # Inconsistency recommendations
        if 'patterns' in analysis:
            for pattern in analysis['patterns']:
                if pattern['type'] == 'inconsistent':
                    recommendations.append(
                        "⚠️ AI grading is inconsistent. Consider adding more specific rubric criteria to prompts."
                    )
                
                if pattern['type'] == 'extreme_corrections':
                    recommendations.append(
                        f"⚠️ {pattern['affected_count']} submissions needed major corrections (>10 points). "
                        "Review these cases to identify what the AI is missing."
                    )
        
        return recommendations
    
    def get_correction_adjustment(self, assignment_id: int = None) -> float:
        """Calculate recommended score adjustment based on correction history"""
        corrections = self.get_corrections(assignment_id)
        
        if corrections.empty or len(corrections) < 5:
            return 0.0  # Not enough data
        
        # Calculate median adjustment (more robust than mean)
        median_diff = corrections['score_diff'].median()
        
        # Only recommend adjustment if pattern is consistent
        if abs(median_diff) > 2 and len(corrections) >= 10:
            return median_diff
        
        return 0.0
    
    def apply_learned_adjustment(self, ai_score: float, assignment_id: int = None) -> Tuple[float, str]:
        """Apply learned adjustment to a new AI score"""
        adjustment = self.get_correction_adjustment(assignment_id)
        
        if adjustment == 0:
            return ai_score, "No adjustment (insufficient correction data)"
        
        adjusted_score = max(0, min(37.5, ai_score + adjustment))
        reason = f"Adjusted by {adjustment:+.1f} points based on {len(self.get_corrections(assignment_id))} previous corrections"
        
        return adjusted_score, reason
    
    def get_correction_summary_for_prompt(self, assignment_id: int = None, limit: int = 5) -> str:
        """Generate a summary of recent corrections to include in AI prompts"""
        corrections = self.get_corrections(assignment_id).head(limit)
        
        if corrections.empty:
            return ""
        
        summary = "RECENT HUMAN CORRECTIONS (learn from these):\n\n"
        
        for _, row in corrections.iterrows():
            summary += f"Student: {row['student_name']}\n"
            summary += f"  AI Score: {row['ai_score']:.1f} → Human Score: {row['human_score']:.1f} (diff: {row['score_diff']:+.1f})\n"
            
            if row['human_feedback']:
                summary += f"  Reason: {row['human_feedback'][:200]}...\n"
            
            summary += "\n"
        
        analysis = self.analyze_patterns(assignment_id)
        if analysis['recommendations']:
            summary += "KEY PATTERNS:\n"
            for rec in analysis['recommendations'][:3]:
                summary += f"- {rec}\n"
        
        return summary


def main():
    """Test the correction analyzer"""
    analyzer = CorrectionAnalyzer()
    
    # Get all corrections
    corrections = analyzer.get_corrections()
    print(f"Total corrections: {len(corrections)}")
    
    # Analyze patterns
    analysis = analyzer.analyze_patterns()
    print("\nAnalysis:")
    print(json.dumps(analysis, indent=2, default=str))
    
    # Get adjustment recommendation
    adjustment = analyzer.get_correction_adjustment()
    print(f"\nRecommended adjustment: {adjustment:+.1f} points")


if __name__ == "__main__":
    main()
