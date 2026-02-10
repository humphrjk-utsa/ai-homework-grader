import { useState, useEffect } from 'react';
import { createTrainingJob, listTrainingJobs, getTrainingJob, cancelTrainingJob } from '../../api/training';
import type { TrainingJob } from '../../api/training';

interface Props {
  courseId: number;
}

const BASE_MODELS = [
  { id: 'Qwen/Qwen3-Coder-30B-A3B-Instruct', label: 'Qwen3 Coder 30B', desc: 'Fast, efficient code model' },
  { id: 'openai/gpt-oss-120b', label: 'GPT-OSS 120B', desc: 'Large reasoning model' },
  { id: 'meta-llama/Llama-3.3-70B-Instruct', label: 'Llama 3.3 70B', desc: 'General-purpose instruction model' },
];

export default function FineTuneTab({ courseId }: Props) {
  const [jobs, setJobs] = useState<TrainingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  // Wizard state
  const [showWizard, setShowWizard] = useState(false);
  const [baseModel, setBaseModel] = useState(BASE_MODELS[0].id);
  const [epochs, setEpochs] = useState(3);
  const [lr, setLr] = useState(2e-5);
  const [loraRank, setLoraRank] = useState(16);
  const [batchSize, setBatchSize] = useState(4);

  useEffect(() => {
    listTrainingJobs(courseId).then(setJobs).finally(() => setLoading(false));
  }, [courseId]);

  // Poll running jobs
  useEffect(() => {
    const running = jobs.filter((j) => ['pending', 'preparing', 'training'].includes(j.status));
    if (running.length === 0) return;

    const interval = setInterval(async () => {
      const updated = await Promise.all(running.map((j) => getTrainingJob(j.id)));
      setJobs((prev) =>
        prev.map((j) => {
          const u = updated.find((u) => u.id === j.id);
          return u || j;
        }),
      );
      if (updated.every((u) => u.status === 'completed' || u.status === 'failed')) {
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [jobs]);

  const handleLaunch = async () => {
    setCreating(true);
    try {
      const job = await createTrainingJob(courseId, {
        base_model: baseModel,
        epochs,
        learning_rate: lr,
        lora_rank: loraRank,
        batch_size: batchSize,
      });
      setJobs((prev) => [job, ...prev]);
      setShowWizard(false);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to create job');
    } finally {
      setCreating(false);
    }
  };

  const handleCancel = async (jobId: number) => {
    try {
      const updated = await cancelTrainingJob(jobId);
      setJobs((prev) => prev.map((j) => (j.id === updated.id ? updated : j)));
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to cancel');
    }
  };

  const statusColor: Record<string, string> = {
    pending: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
    preparing: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300',
    training: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
    completed: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
    failed: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  };

  const inputCls = 'mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500';

  if (loading) return <p className="text-gray-400">Loading jobs...</p>;

  return (
    <div className="space-y-6">
      {/* Launch button */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Fine-tune a model using reviewed submission data
        </p>
        <button
          onClick={() => setShowWizard(!showWizard)}
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
        >
          {showWizard ? 'Cancel' : 'New Fine-Tune Job'}
        </button>
      </div>

      {/* Wizard */}
      {showWizard && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Configure Fine-Tuning</h3>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Base Model</label>
            <select value={baseModel} onChange={(e) => setBaseModel(e.target.value)} className={inputCls}>
              {BASE_MODELS.map((m) => (
                <option key={m.id} value={m.id}>{m.label} - {m.desc}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Epochs
                <span className="ml-1 text-xs text-gray-400" title="Number of passes over the training data">(?)</span>
              </label>
              <input type="number" min={1} max={20} value={epochs} onChange={(e) => setEpochs(Number(e.target.value))} className={inputCls} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Learning Rate
                <span className="ml-1 text-xs text-gray-400" title="Controls how fast the model learns. Lower = more stable">(?)</span>
              </label>
              <input type="number" min={1e-6} max={1e-3} step={1e-6} value={lr} onChange={(e) => setLr(Number(e.target.value))} className={inputCls} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                LoRA Rank
                <span className="ml-1 text-xs text-gray-400" title="Higher = more trainable parameters. 8-32 is typical">(?)</span>
              </label>
              <select value={loraRank} onChange={(e) => setLoraRank(Number(e.target.value))} className={inputCls}>
                {[8, 16, 32, 64].map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Batch Size
                <span className="ml-1 text-xs text-gray-400" title="Samples per training step. Lower uses less memory">(?)</span>
              </label>
              <select value={batchSize} onChange={(e) => setBatchSize(Number(e.target.value))} className={inputCls}>
                {[1, 2, 4, 8].map((b) => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
          </div>

          <button
            onClick={handleLaunch}
            disabled={creating}
            className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {creating ? 'Launching...' : 'Launch Fine-Tuning'}
          </button>
        </div>
      )}

      {/* Job history */}
      {jobs.length === 0 ? (
        <p className="text-sm text-gray-400 dark:text-gray-500">No fine-tuning jobs yet.</p>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    Job #{job.id}
                  </span>
                  <span className="ml-2 text-xs text-gray-400">{job.base_model.split('/').pop()}</span>
                  <span className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${statusColor[job.status] || ''}`}>
                    {job.status}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">{job.training_samples} samples</span>
                  {['pending', 'preparing', 'training'].includes(job.status) && (
                    <button
                      onClick={() => handleCancel(job.id)}
                      className="text-xs text-red-500 hover:text-red-700"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
              {['preparing', 'training'].includes(job.status) && (
                <div className="mt-2 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-indigo-600 rounded-full h-2 transition-all"
                    style={{ width: `${job.progress_percent}%` }}
                  />
                </div>
              )}
              {job.error_message && (
                <p className="mt-2 text-xs text-red-500">{job.error_message}</p>
              )}
              <p className="mt-1 text-xs text-gray-400">
                Created {new Date(job.created_at).toLocaleString()}
                {job.completed_at && ` - Completed ${new Date(job.completed_at).toLocaleString()}`}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
