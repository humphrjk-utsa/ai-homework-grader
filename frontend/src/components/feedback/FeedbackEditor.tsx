import { useState, useEffect } from 'react';
import type { AIFeedback, TechnicalAnalysis, ComprehensiveFeedback, DetailedFeedback } from '../../types';
import EditableList from './EditableList';

interface FeedbackEditorProps {
  aiFeedback: AIFeedback | null;
  editedFeedback: AIFeedback | null;
  editing: boolean;
  onSave: (feedback: AIFeedback) => void;
  maxScore: number;
}

function emptyDetailedFeedback(): DetailedFeedback {
  return {
    reflection_assessment: [],
    analytical_strengths: [],
    business_application: [],
    areas_for_development: [],
    recommendations: [],
  };
}

function emptyTechnicalAnalysis(): TechnicalAnalysis {
  return { code_strengths: [], code_suggestions: [], technical_observations: [] };
}

function emptyComprehensiveFeedback(): ComprehensiveFeedback {
  return { instructor_comments: '', detailed_feedback: emptyDetailedFeedback() };
}

/** Deep-clone feedback for safe editing, filling in missing fields */
function cloneFeedback(src: AIFeedback | null, maxScore: number): AIFeedback {
  if (!src) {
    return {
      final_score: 0,
      max_points: maxScore,
      component_scores: {},
      component_percentages: {},
      technical_analysis: emptyTechnicalAnalysis(),
      comprehensive_feedback: emptyComprehensiveFeedback(),
    };
  }
  const ta = src.technical_analysis || emptyTechnicalAnalysis();
  const cf = src.comprehensive_feedback || emptyComprehensiveFeedback();
  const df = cf.detailed_feedback || emptyDetailedFeedback();
  return {
    ...src,
    max_points: src.max_points || maxScore,
    technical_analysis: {
      code_strengths: [...(ta.code_strengths || [])],
      code_suggestions: [...(ta.code_suggestions || [])],
      technical_observations: [...(ta.technical_observations || [])],
    },
    comprehensive_feedback: {
      instructor_comments: cf.instructor_comments || '',
      detailed_feedback: {
        reflection_assessment: [...(df.reflection_assessment || [])],
        analytical_strengths: [...(df.analytical_strengths || [])],
        business_application: [...(df.business_application || [])],
        areas_for_development: [...(df.areas_for_development || [])],
        recommendations: [...(df.recommendations || [])],
      },
    },
  };
}

export default function FeedbackEditor({
  aiFeedback,
  editedFeedback,
  editing,
  onSave,
  maxScore,
}: FeedbackEditorProps) {
  // Use edited version if available, otherwise fall back to AI version
  const source = editedFeedback || aiFeedback;
  const [draft, setDraft] = useState<AIFeedback>(() => cloneFeedback(source, maxScore));

  useEffect(() => {
    setDraft(cloneFeedback(editedFeedback || aiFeedback, maxScore));
  }, [aiFeedback, editedFeedback, maxScore]);

  const ta = draft.technical_analysis || emptyTechnicalAnalysis();
  const cf = draft.comprehensive_feedback || emptyComprehensiveFeedback();
  const df = cf.detailed_feedback || emptyDetailedFeedback();

  const updateTA = (field: keyof TechnicalAnalysis, value: string[]) => {
    setDraft({
      ...draft,
      technical_analysis: { ...ta, [field]: value },
    });
  };

  const updateDF = (field: keyof DetailedFeedback, value: string[]) => {
    setDraft({
      ...draft,
      comprehensive_feedback: {
        ...cf,
        detailed_feedback: { ...df, [field]: value },
      },
    });
  };

  const updateInstructorComments = (value: string) => {
    setDraft({
      ...draft,
      comprehensive_feedback: { ...cf, instructor_comments: value },
    });
  };

  const handleSave = () => onSave(draft);

  const inputCls = 'px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500';

  return (
    <div className="space-y-5">
      {/* Score */}
      {editing && (
        <div className="flex items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Score</label>
            <input
              type="number"
              min={0}
              max={maxScore}
              step={0.5}
              value={draft.final_score ?? ''}
              onChange={(e) => setDraft({ ...draft, final_score: Number(e.target.value) })}
              className={`mt-1 w-28 ${inputCls}`}
            />
          </div>
          <div className="text-sm text-gray-400 dark:text-gray-500 mt-6">/ {maxScore}</div>
        </div>
      )}

      {/* Code Strengths */}
      <EditableList
        items={ta.code_strengths || []}
        onChange={(v) => updateTA('code_strengths', v)}
        editing={editing}
        label="Code Strengths"
        labelColor="text-green-700 dark:text-green-400"
        placeholder="Add a strength..."
      />

      {/* Analytical Strengths */}
      <EditableList
        items={df.analytical_strengths || []}
        onChange={(v) => updateDF('analytical_strengths', v)}
        editing={editing}
        label="Analytical Strengths"
        labelColor="text-green-700 dark:text-green-400"
        placeholder="Add an analytical strength..."
      />

      {/* Code Suggestions */}
      <EditableList
        items={ta.code_suggestions || []}
        onChange={(v) => updateTA('code_suggestions', v)}
        editing={editing}
        label="Code Suggestions"
        labelColor="text-amber-700 dark:text-amber-400"
        placeholder="Add a suggestion..."
      />

      {/* Areas for Development */}
      <EditableList
        items={df.areas_for_development || []}
        onChange={(v) => updateDF('areas_for_development', v)}
        editing={editing}
        label="Areas for Development"
        labelColor="text-amber-700 dark:text-amber-400"
        placeholder="Add an area for development..."
      />

      {/* Recommendations */}
      <EditableList
        items={df.recommendations || []}
        onChange={(v) => updateDF('recommendations', v)}
        editing={editing}
        label="Recommendations"
        labelColor="text-blue-700 dark:text-blue-400"
        placeholder="Add a recommendation..."
      />

      {/* Reflection Assessment */}
      <EditableList
        items={df.reflection_assessment || []}
        onChange={(v) => updateDF('reflection_assessment', v)}
        editing={editing}
        label="Reflection Assessment"
        labelColor="text-purple-700 dark:text-purple-400"
        placeholder="Add a reflection note..."
      />

      {/* Technical Observations */}
      <EditableList
        items={ta.technical_observations || []}
        onChange={(v) => updateTA('technical_observations', v)}
        editing={editing}
        label="Technical Observations"
        labelColor="text-gray-700 dark:text-gray-300"
        placeholder="Add an observation..."
      />

      {/* Instructor Comments */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Instructor Comments</h3>
        {editing ? (
          <textarea
            value={cf.instructor_comments || ''}
            onChange={(e) => updateInstructorComments(e.target.value)}
            rows={4}
            className={`mt-1 w-full ${inputCls}`}
            placeholder="Overall instructor assessment..."
          />
        ) : cf.instructor_comments ? (
          <div className="mt-1 text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap bg-gray-50 dark:bg-gray-900/30 p-3 rounded">
            {cf.instructor_comments}
          </div>
        ) : null}
      </div>

      {/* Save button */}
      {editing && (
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
        >
          Save Feedback Edits
        </button>
      )}
    </div>
  );
}
