"use client"

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

export default function Dashboard() {
  const [signals, setSignals] = useState<any[]>([])

  useEffect(() => {
    // 1. Fetch initial data on load
    const fetchInitialData = async () => {
      const { data, error } = await supabase
        .from('trading_signals')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10)
      
      if (data) setSignals(data)
    }

    fetchInitialData()

    // 2. Subscribe to LIVE incoming signals
    const channel = supabase
      .channel('live-signals')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'trading_signals' },
        (payload) => {
          console.log('New signal detected!', payload.new)
          // Add the new signal to the top of the list and keep only the latest 10
          setSignals((currentSignals) => [payload.new, ...currentSignals].slice(0, 10))
        }
      )
      .subscribe()

    // Cleanup subscription on unmount
    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  // Helper function to clean up the long confidence percentages
  const formatConfidence = (conf: string) => {
    const num = parseFloat(conf)
    return isNaN(num) ? conf : `${num.toFixed(2)}%`
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white p-10">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">MarketPulse AI Terminal</h1>
            <p className="text-gray-400">Live intelligent signal extraction & regime analysis</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span className="text-sm font-mono text-green-500 uppercase tracking-widest">Live Stream Active</span>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden shadow-2xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-800 border-b border-gray-700 text-sm uppercase tracking-wider text-gray-400">
                <th className="p-4">Ticker</th>
                <th className="p-4">Signal</th>
                <th className="p-4">Confidence</th>
                <th className="p-4">Tier</th>
                <th className="p-4">Time</th>
              </tr>
            </thead>
            <tbody>
              {signals?.map((signal) => (
                <tr key={signal.id} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors animate-in fade-in slide-in-from-top-2 duration-500">
                  <td className="p-4 font-mono font-bold text-blue-400">{signal.ticker}</td>
                  <td className="p-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      signal.direction_label === 'bullish' ? 'bg-green-500/20 text-green-400' : 
                      signal.direction_label === 'bearish' ? 'bg-red-500/20 text-red-400' : 
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {signal.direction_label.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-4 text-gray-300 font-mono">{formatConfidence(signal.confidence)}</td>
                  <td className="p-4 text-gray-300">{signal.regime_adjusted_tier}</td>
                  <td className="p-4 text-xs text-gray-500">
                    {new Date(signal.created_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  )
}