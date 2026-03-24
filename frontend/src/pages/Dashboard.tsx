import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { jobsApi, runsApi } from '../api/client'
import type { Job } from '../types'
import JobCard from '../components/JobCard'

const STATUS_TABS = [
  { label: 'Review Queue', value: 'pending_review' },
  { label: 'Approved', value: 'approved' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'All', value: '' },
]

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('pending_review')
  const [source, setSource] = useState('')
  const [minScore, setMinScore] = useState(0)

  const { data, isLoading } = useQuery({
    queryKey: ['jobs', activeTab, source, minScore],
    queryFn: () => jobsApi.list({
      status: activeTab || undefined,
      source: source || undefined,
      min_score: minScore > 0 ? minScore : undefined,
      limit: 50,
    }).then(r => r.data as Job[]),
    refetchInterval: 30000,
  })

  const { data: runStatus } = useQuery({
    queryKey: ['run-status'],
    queryFn: () => runsApi.status().then(r => r.data),
    refetchInterval: 5000,
  })

  const triggerRun = useMutation({
    mutationFn: () => runsApi.trigger(),
  })

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Job Dashboard</h1>
          {activeTab === 'pending_review' && data && (
            <p className="text-gray-500 text-sm mt-1">
              {data.length} jobs pending review
            </p>
          )}
        </div>
        <button
          onClick={() => triggerRun.mutate()}
          disabled={triggerRun.isPending || runStatus?.active}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {runStatus?.active ? (
            <><span className="animate-spin">⟳</span> Running...</>
          ) : (
            '▶ Run Now'
          )}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit">
        {STATUS_TABS.map(tab => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              activeTab === tab.value
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={source}
          onChange={e => setSource(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All Sources</option>
          <option value="linkedin">LinkedIn</option>
          <option value="indeed">Indeed</option>
        </select>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>Min score:</span>
          <input
            type="range" min={0} max={100} step={5}
            value={minScore}
            onChange={e => setMinScore(Number(e.target.value))}
            className="w-24"
          />
          <span className="w-6 text-right font-medium">{minScore || 'Any'}</span>
        </div>
      </div>

      {/* Job Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-400">Loading jobs...</div>
      ) : data?.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg">No jobs here yet.</p>
          <p className="text-sm mt-1">Click "Run Now" to scrape new jobs.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.map(job => <JobCard key={job.id} job={job} />)}
        </div>
      )}
    </div>
  )
}
