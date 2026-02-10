import { useState, useEffect } from 'react';
import { getRunningModels } from '../../api/models';
import type { CustomModel } from '../../api/models';

export default function ClusterStatusTab() {
  const [running, setRunning] = useState<CustomModel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRunningModels().then(setRunning).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-400">Loading cluster status...</p>;

  return (
    <div className="space-y-6">
      {/* Cluster nodes - static config based on known hardware */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Cluster Nodes</h3>
        <div className="grid grid-cols-2 gap-4">
          {[
            { name: 'Mac Studio 1 (Scheduler)', spec: 'M3 Ultra, 512GB', ip: '169.254.150.1', role: 'scheduler' },
            { name: 'Mac Studio 2 (Worker)', spec: 'M4 Max, 128GB', ip: '169.254.150.2', role: 'worker' },
            { name: 'DGX Spark 1', spec: 'GB10, 128GB', ip: '169.254.150.3', role: 'gpu' },
            { name: 'DGX Spark 2', spec: 'GB10, 128GB', ip: '169.254.150.4', role: 'gpu' },
          ].map((node) => (
            <div key={node.name} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900 dark:text-white">{node.name}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  node.role === 'gpu'
                    ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
                    : 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
                }`}>
                  {node.role}
                </span>
              </div>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{node.spec}</p>
              <p className="text-xs text-gray-400 font-mono">{node.ip}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Running models */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Running Models ({running.length})
        </h3>
        {running.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500">No models currently deployed.</p>
        ) : (
          <div className="space-y-2">
            {running.map((m) => (
              <div key={m.id} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3 flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{m.name}</span>
                  <span className="ml-2 text-xs text-gray-400 font-mono">{m.model_id}</span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-green-600 dark:text-green-400">{m.server_url}</span>
                  {m.container_id && (
                    <p className="text-xs text-gray-400 font-mono">{m.container_id}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Benchmarks reference */}
      <div className="bg-gray-50 dark:bg-gray-900/30 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Performance Reference</h3>
        <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
          <p>DGX Spark (vLLM FP8): Qwen prefill ~19,742 tok/s, decode ~49.9 tok/s</p>
          <p>DGX Spark (vLLM MXFP4): GPT-OSS decode ~48.0 tok/s</p>
          <p>Mac 1 (MLX 8-bit): GPT-OSS prefill ~1,330, decode ~56.8 tok/s</p>
          <p>Mac 2 (MLX Q8): Qwen prefill ~1,344, decode ~71.8 tok/s</p>
        </div>
      </div>
    </div>
  );
}
