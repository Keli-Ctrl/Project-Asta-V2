import React from 'react';
import { Wallet, Activity, TrendingUp, TrendingDown } from 'lucide-react';

interface Account {
  id: string;
  broker: string;
  login: string;
  balance: number;
  equity: number;
  currency: string;
}

interface Position {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  volume: number;
  entryPrice: number;
  currentPrice: number;
  profit: number;
}

export const LivePortfolioOverview: React.FC<{ accounts: Account[], positions: Position[] }> = ({ accounts, positions }) => {
  const totalBalance = accounts.reduce((acc, curr) => acc + curr.balance, 0);
  const totalEquity = accounts.reduce((acc, curr) => acc + curr.equity, 0);
  const totalProfit = positions.reduce((acc, curr) => acc + curr.profit, 0);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 text-sm font-medium">Total Balance</h3>
          <Wallet className="text-blue-500 w-5 h-5" />
        </div>
        <p className="text-3xl font-bold text-white">${totalBalance.toLocaleString()}</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 text-sm font-medium">Total Equity</h3>
          <Activity className="text-purple-500 w-5 h-5" />
        </div>
        <p className="text-3xl font-bold text-white">${totalEquity.toLocaleString()}</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-slate-400 text-sm font-medium">Floating Profit</h3>
          {totalProfit >= 0 ? (
            <TrendingUp className="text-green-500 w-5 h-5" />
          ) : (
            <TrendingDown className="text-red-500 w-5 h-5" />
          )}
        </div>
        <p className={`text-3xl font-bold ${totalProfit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
          {totalProfit >= 0 ? '+' : ''}${totalProfit.toLocaleString()}
        </p>
      </div>

      <div className="md:col-span-3 bg-slate-900 border border-slate-800 rounded-lg overflow-hidden shadow-xl mt-4">
        <div className="px-6 py-4 border-b border-slate-800">
          <h3 className="text-white font-semibold">Active Positions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="text-slate-500 text-sm border-b border-slate-800">
                <th className="px-6 py-3">Symbol</th>
                <th className="px-6 py-3">Side</th>
                <th className="px-6 py-3">Volume</th>
                <th className="px-6 py-3">Entry</th>
                <th className="px-6 py-3">Current</th>
                <th className="px-6 py-3 text-right">Profit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {positions.map((pos) => (
                <tr key={pos.id} className="text-slate-300 hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">{pos.symbol}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${pos.side === 'BUY' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                      {pos.side}
                    </span>
                  </td>
                  <td className="px-6 py-4">{pos.volume}</td>
                  <td className="px-6 py-4">${pos.entryPrice.toFixed(5)}</td>
                  <td className="px-6 py-4">${pos.currentPrice.toFixed(5)}</td>
                  <td className={`px-6 py-4 text-right font-semibold ${pos.profit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {pos.profit >= 0 ? '+' : ''}{pos.profit.toFixed(2)}
                  </td>
                </tr>
              ))}
              {positions.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">No active positions</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
