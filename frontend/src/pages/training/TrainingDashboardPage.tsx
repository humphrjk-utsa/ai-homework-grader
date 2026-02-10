import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import TrainingDataTab from './TrainingDataTab';
import FineTuneTab from './FineTuneTab';
import ModelsTab from './ModelsTab';
import ClusterStatusTab from './ClusterStatusTab';

const TABS = ['Training Data', 'Fine-Tune', 'Models', 'Cluster'] as const;
type Tab = (typeof TABS)[number];

export default function TrainingDashboardPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const id = Number(courseId);
  const [activeTab, setActiveTab] = useState<Tab>('Training Data');

  return (
    <div>
      <Link
        to={id ? `/courses/${id}` : '/courses'}
        className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
      >
        Back to {id ? 'course' : 'courses'}
      </Link>

      <h1 className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
        Training & Models
      </h1>
      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
        Fine-tune models on reviewed submissions and manage deployments
      </p>

      {/* Tabs */}
      <div className="mt-6 border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="mt-6">
        {activeTab === 'Training Data' && id && <TrainingDataTab courseId={id} />}
        {activeTab === 'Fine-Tune' && id && <FineTuneTab courseId={id} />}
        {activeTab === 'Models' && id && <ModelsTab courseId={id} />}
        {activeTab === 'Cluster' && <ClusterStatusTab />}
        {!id && activeTab !== 'Cluster' && (
          <p className="text-gray-400">Select a course to view training data.</p>
        )}
      </div>
    </div>
  );
}
