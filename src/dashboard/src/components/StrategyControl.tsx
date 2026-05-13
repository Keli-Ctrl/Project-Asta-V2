import React from 'react';
import { Settings, Play, Square, Percent } from 'lucide-react';

interface Strategy {
  id: string;
  name: string;
  enabled: boolean;
  weight: number;
  description: string;
}

interface StrategyControlProps {
  strategies: Strategy[];
  onToggle: (id: string) => void;
  onWeightChange: (id: string, weight: number) => void;
}

export const StrategyControl: React.FC<StrategyControlProps> = ({ strategies, onToggle, onWeightChange }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Settings className="text-slate-400 w-5 h-5" />
          <h3 className="text-white font-semibold">Strategy Control Panel</h3>
        </div>
      </div>
      <div className="p-4 space-y-4">
        {strategies.map((strategy) => (
          <div key={strategy.id} className="bg-slate-800/50 border border-slate-700/50 p-4 rounded-lg">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h4 className="text-white font-medium">{strategy.name}</h4>
                <p className="text-slate-400 text-xs mt-1">{strategy.description}</p>
              </div>
              <button
                onClick={() => onToggle(strategy.id)}
                className={`p-2 rounded-md transition-colors ${
                  strategy.enabled 
                    ? 'bg-red-500/10 text-red-500 hover:bg-red-500/20' 
                    : 'bg-green-500/10 text-green-500 hover:bg-green-500/20'
                }`}
              >
                {strategy.enabled ? <Square size={18} /> : <Play size={18} />}
              </button>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Allocation Weight</span>
                  <span>{strategy.weight}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={strategy.weight}
                  onChange={(e) => onWeightChange(strategy.id, parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>
              <div className="bg-slate-800 p-2 rounded text-blue-500">
                <Percent size={16} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
