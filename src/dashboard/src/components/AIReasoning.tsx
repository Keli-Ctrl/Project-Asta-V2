import React from 'react';
import { Brain, MessageSquare, ShieldCheck, Zap } from 'lucide-react';

interface AIAnalysis {
  id: string;
  timestamp: string;
  symbol: string;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
  reasoning: string;
  regime: string;
}

export const AIReasoning: React.FC<{ analysis: AIAnalysis[] }> = ({ analysis }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden h-full flex flex-col">
      <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Brain className="text-purple-500 w-5 h-5" />
          <h3 className="text-white font-semibold">AI Reasoning Layer</h3>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {analysis.map((item) => (
          <div key={item.id} className="border-l-2 border-purple-500 bg-slate-800/30 p-4 rounded-r-lg">
            <div className="flex justify-between items-start mb-2">
              <span className="text-white font-bold text-sm">{item.symbol}</span>
              <span className="text-slate-500 text-[10px]">{new Date(item.timestamp).toLocaleTimeString()}</span>
            </div>
            
            <div className="flex space-x-3 mb-3">
              <div className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                item.sentiment === 'BULLISH' ? 'bg-green-500/10 text-green-500' : 
                item.sentiment === 'BEARISH' ? 'bg-red-500/10 text-red-500' : 'bg-slate-500/10 text-slate-500'
              }`}>
                {item.sentiment}
              </div>
              <div className="flex items-center text-[10px] text-slate-400">
                <Zap size={10} className="mr-1 text-yellow-500" />
                Confidence: {(item.confidence * 100).toFixed(0)}%
              </div>
              <div className="flex items-center text-[10px] text-slate-400">
                <ShieldCheck size={10} className="mr-1 text-blue-500" />
                Regime: {item.regime}
              </div>
            </div>

            <div className="flex items-start space-x-2">
              <MessageSquare size={14} className="text-slate-500 mt-1 flex-shrink-0" />
              <p className="text-slate-300 text-xs leading-relaxed italic">
                "{item.reasoning}"
              </p>
            </div>
          </div>
        ))}
        {analysis.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-600 py-10">
            <Brain size={48} className="mb-4 opacity-20" />
            <p>Waiting for AI signal analysis...</p>
          </div>
        )}
      </div>
    </div>
  );
};
