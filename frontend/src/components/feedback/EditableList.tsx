import { useState } from 'react';

interface EditableListProps {
  items: string[];
  onChange: (items: string[]) => void;
  editing: boolean;
  label: string;
  labelColor?: string;
  placeholder?: string;
}

export default function EditableList({
  items,
  onChange,
  editing,
  label,
  labelColor = 'text-gray-700 dark:text-gray-300',
  placeholder = 'Add item...',
}: EditableListProps) {
  const [newItem, setNewItem] = useState('');

  const handleAdd = () => {
    const trimmed = newItem.trim();
    if (trimmed) {
      onChange([...items, trimmed]);
      setNewItem('');
    }
  };

  const handleRemove = (index: number) => {
    onChange(items.filter((_, i) => i !== index));
  };

  const handleEdit = (index: number, value: string) => {
    const updated = [...items];
    updated[index] = value;
    onChange(updated);
  };

  if (!editing) {
    if (!items || items.length === 0) return null;
    return (
      <div>
        <h3 className={`text-sm font-medium ${labelColor}`}>{label}</h3>
        <ul className="mt-1 list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div>
      <h3 className={`text-sm font-medium ${labelColor}`}>{label}</h3>
      <div className="mt-1 space-y-2">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-2">
            <textarea
              value={item}
              onChange={(e) => handleEdit(i, e.target.value)}
              rows={2}
              className="flex-1 px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            <button
              onClick={() => handleRemove(i)}
              className="mt-1 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-sm"
              title="Remove"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        ))}
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAdd())}
            placeholder={placeholder}
            className="flex-1 px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
          <button
            onClick={handleAdd}
            className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}
