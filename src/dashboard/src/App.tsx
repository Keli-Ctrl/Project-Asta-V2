import { useState, useEffect, useCallback } from 'react';
import { LivePortfolioOverview } from './components/LivePortfolioOverview';
import { MarketChart } from './components/MarketChart';
import { StrategyControl } from './components/StrategyControl';
import { AIReasoning } from './components/AIReasoning';
import { Activity, LayoutDashboard, History, Shield, Globe } from 'lucide-react';

// Mock data for initial state
const MOCK_CHART_DATA = [
  { time: '2023-05-12', open: 1.0850, high: 1.0870, low: 1.0840, close: 1.0865 },
  { time: '2023-05-13', open: 1.0865, high: 1.0890, low: 1.0860, close: 1.0880 },
  { time: '2023-05-14', open: 1.0880, high: 1.0910, low: 1.0875, close: 1.0905 },
  { time: '2023-05-15', open: 1.0905, high: 1.0920, low: 1.0890, close: 1.0915 },
];

function App() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [strategies, setStrategies] = useState<any[]>([
    { id: 'ema-trend', name: 'EMA Trend Follower', enabled: true, weight: 40, description: 'Dual EMA crossover strategy with ATR-based SL/TP.' },
    { id: 'rsi-mom', name: 'RSI Momentum', enabled: false, weight: 20, description: 'Mean reversion strategy targeting overbought/oversold levels.' },
    { id: 'liq-sweep', name: 'Liquidity Sweep', enabled: true, weight: 40, description: 'Smart money concept detecting liquidity grabs at session highs/lows.' },
  ]);
  const [aiAnalysis, setAiAnalysis] = useState<any[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');

  useEffect(() => {
    // Initial data fetch
    setAccounts([{
      id: 'acc_1',
      broker: 'IC Markets',
      login: '12345678',
      balance: 10500.25,
      equity: 10580.50,
      currency: 'USD'
    }]);

    setPositions([
      { id: 'pos_1', symbol: 'EURUSD', side: 'BUY', volume: 0.1, entryPrice: 1.0865, currentPrice: 1.0880, profit: 15.25 },
      { id: 'pos_2', symbol: 'GBPUSD', side: 'SELL', volume: 0.05, entryPrice: 1.2540, currentPrice: 1.2510, profit: 15.00 },
    ]);

    setAiAnalysis([
      {
        id: '1',
        timestamp: new Date().toISOString(),
        symbol: 'EURUSD',
        sentiment: 'BULLISH',
        confidence: 0.85,
        reasoning: 'Strong bullish engulfing on H1 near major support level. Macro sentiment shift following lower than expected CPI data.',
        regime: 'Trending Up'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        symbol: 'XAUUSD',
        sentiment: 'NEUTRAL',
        confidence: 0.45,
        reasoning: 'Price consolidating within a tight range. High volatility expected before FOMC minutes.',
        regime: 'Range Bound'
      }
    ]);

    // WebSocket connection
    const socket = new WebSocket('ws://localhost:8000/ws/market-data');
    
    socket.onopen = () => {
      setConnectionStatus('connected');
      console.log('Connected to Project Asta Backend');
    };

    socket.onclose = () => {
      setConnectionStatus('disconnected');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'ACCOUNT_UPDATE') {
        setAccounts(data.payload);
      } else if (data.type === 'POSITION_UPDATE') {
        setPositions(data.payload);
      } else if (data.type === 'AI_REASONING') {
        setAiAnalysis(prev => [data.payload, ...prev].slice(0, 20));
      }
    };

    return () => socket.close();
  }, []);

  const handleToggleStrategy = useCallback((id: string) => {
    setStrategies(prev => prev.map(s => s.id === id ? { ...s, enabled: !s.enabled } : s));
    // In production, call API: axios.post(`/api/strategies/${id}/toggle`)
  }, []);

  const handleWeightChange = useCallback((id: string, weight: number) => {
    setStrategies(prev => prev.map(s => s.id === id ? { ...s, weight } : s));
  }, []);

  return (
    <div className="min-h-screen bg-black text-slate-200 flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white">A</div>
            <span className="text-xl font-bold text-white tracking-tight">ASTA</span>
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
              {connectionStatus}
            </span>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <a href="#" className="flex items-center space-x-3 px-4 py-2 bg-blue-600/10 text-blue-500 rounded-lg font-medium">
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-4 py-2 text-slate-500 hover:bg-slate-900 hover:text-slate-300 rounded-lg transition-colors">
            <Activity size={20} />
            <span>Market Data</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-4 py-2 text-slate-500 hover:bg-slate-900 hover:text-slate-300 rounded-lg transition-colors">
            <History size={20} />
            <span>Trade History</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-4 py-2 text-slate-500 hover:bg-slate-900 hover:text-slate-300 rounded-lg transition-colors">
            <Shield size={20} />
            <span>Risk Settings</span>
          </a>
        </nav>

        <div className="p-4 mt-auto border-t border-slate-800">
          <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
              <span>System Health</span>
              <Globe size={12} />
            </div>
            <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
              <div className="bg-green-500 h-full w-[98%]"></div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-16 border-b border-slate-800 bg-slate-950/50 flex items-center justify-between px-8 backdrop-blur-md">
          <h2 className="text-white font-bold">Institutional Alpha Terminal</h2>
          <div className="flex items-center space-x-4">
            <span className="text-xs text-slate-500">Last update: 2 seconds ago</span>
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700"></div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 bg-[#020617] space-y-8">
          <LivePortfolioOverview accounts={accounts} positions={positions} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <MarketChart symbol="EURUSD" data={MOCK_CHART_DATA} />
            </div>
            <div>
              <AIReasoning analysis={aiAnalysis} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-8">
            <div>
              <StrategyControl 
                strategies={strategies} 
                onToggle={handleToggleStrategy} 
                onWeightChange={handleWeightChange} 
              />
            </div>
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-slate-500 italic">
               Risk Engine & Analytics visualization under construction...
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
