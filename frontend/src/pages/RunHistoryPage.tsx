import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { runsApi } from '../api/client'
import type { RunHistory } from '../types'
import StatusBadge from '../components/StatusBadge'

export default function RunHistoryPage() {
  const [expanded, setExpanded] = useState<string | null>(null)
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['runs'],
    queryFn: () => runsApi.list().then(r => r.data as RunHistory[]),
    refetchInterval: 10000,
  })

  const trigger = useMutation({
    mutationFn: () => runsApi.trigger(),
    onSuccess: () => setTimeout(() => qc.invalidateQueries({ queryKey: ['runs'] }), 2000),
  })

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Run History</h1>
        <button
          onClick={() => trigger.mutate()}
          disabled={trigger.isPending}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors disabled:opacity-50"
        >
          {trigger.isPending ? 'Triggering...' : '▶ Run Now'}
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-400">Loading...</div>
      ) : !data?.length ? (
        <div className="text-center py-12 text-gray-400">No runs yet. Click "Run Now" to start.</div>
      ) : (
        <div className="space-y-3">
          {data.map(run => (
            <div key={run.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div
                className="flex items-center gap-4 px-4 py-3 cursor-pointer hover:bg-gray-50"
                onClick={() => setExpanded(expanded === run.id ? null : run.id)}
              >
                <StatusBadge status={run.status} />
                <span className="text-sm text-gray-700 font-medium">
                  {new Date(run.started_at).toLocaleString()}
                </span>
                <span className="text-xs text-gray-400">{run.trigger}</span>
                <div className="flex gap-3 ml-auto text-xs text-gray-500">
                  <span>🔍 {run.jobs_scraped} scraped</span>
                  <span>✨ {run.jobs_new} new</span>
                  <span>🤖 {run.jobs_scored} scored</span>
                  <span>📬 {run.jobs_applied} applied</span>
                </div>
                <span className="text-gray-400">{expanded === run.id ? '▲' : '▼'}</span>
              </div>
              {expanded === run.id && run.log_output && (
                <div className="border-t border-gray-100 bg-gray-900 p-4">
                  <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap overflow-auto max-h-64">
                    {run.log_output}
                  </pre>
                </div>
              )}
              {expanded === run.id && run.error_message && (
                <div className="border-t border-red-100 bg-red-50 p-3">
                  <p className="text-xs text-red-600">{run.error_message}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
