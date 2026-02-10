import { useState, useEffect } from 'react';
import { listModels, registerModel, deployModel, stopModel } from '../../api/models';
import type { CustomModel } from '../../api/models';

interface Props {
  courseId: number;
}

export default function ModelsTab({ courseId }: Props) {
  const [models, setModels] = useState<CustomModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState('');
  const [modelId, setModelId] = useState('');
  const [deploying, setDeploying] = useState<number | null>(null);

  const refresh = () => {
    listModels(courseId).then(setModels).finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, [courseId]);

  const handleRegister = async () => {
    if (!name || !modelId) return;
    try {
      await registerModel({ name, model_id: modelId, course_id: courseId });
      setName('');
      setModelId('');
      setShowAdd(false);
      refresh();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to register model');
    }
  };

  const handleDeploy = async (id: number) => {
    setDeploying(id);
    try {
      await deployModel(id);
      refresh();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to deploy');
    } finally {
      setDeploying(null);
    }
  };

  const handleStop = async (id: number) => {
    try {
      await stopModel(id);
      refresh();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to stop');
    }
  };

  const statusBadge: Record<string, string> = {
    available: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
    deploying: 'bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300',
    running: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
    stopped: 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-500',
    error: 'bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400',
  };

  const typeBadge: Record<string, string> = {
    base: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
    finetuned: 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
    custom: 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300',
  };

  const inputCls = 'mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500';

  if (loading) return <p className="text-gray-400">Loading models...</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Manage and deploy AI models for grading
        </p>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
        >
          {showAdd ? 'Cancel' : 'Register Model'}
        </button>
      </div>

      {/* Register form */}
      {showAdd && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Display Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="My Custom Model" className={inputCls} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Model ID / Path</label>
            <input value={modelId} onChange={(e) => setModelId(e.target.value)} placeholder="organization/model-name or /path/to/model" className={inputCls} />
          </div>
          <button
            onClick={handleRegister}
            disabled={!name || !modelId}
            className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            Register
          </button>
        </div>
      )}

      {/* Model list */}
      <div className="space-y-3">
        {models.map((m, idx) => (
          <div key={m.id ?? `builtin-${idx}`} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{m.name}</span>
                <span className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${typeBadge[m.model_type] || ''}`}>
                  {m.model_type}
                </span>
                <span className={`ml-1 px-2 py-0.5 rounded text-xs font-medium ${statusBadge[m.status] || ''}`}>
                  {m.status}
                </span>
              </div>
              <div className="flex items-center gap-2">
                {m.id && m.status === 'available' && (
                  <button
                    onClick={() => handleDeploy(m.id!)}
                    disabled={deploying === m.id}
                    className="px-3 py-1 text-xs font-medium rounded-md bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
                  >
                    {deploying === m.id ? 'Deploying...' : 'Deploy'}
                  </button>
                )}
                {m.id && m.status === 'running' && (
                  <button
                    onClick={() => handleStop(m.id!)}
                    className="px-3 py-1 text-xs font-medium rounded-md bg-red-600 text-white hover:bg-red-700"
                  >
                    Stop
                  </button>
                )}
              </div>
            </div>
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500 font-mono">{m.model_id}</p>
            {m.server_url && (
              <p className="mt-0.5 text-xs text-green-600 dark:text-green-400">{m.server_url}</p>
            )}
            {m.description && (
              <p className="mt-0.5 text-xs text-gray-400">{m.description}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
