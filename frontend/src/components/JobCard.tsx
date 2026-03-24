import { Link } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { Job } from '../types'
import { jobsApi } from '../api/client'
import StatusBadge from './StatusBadge'
import ScoreBar from './ScoreBar'

export default function JobCard({ job }: { job: Job }) {
  const qc = useQueryClient()

  const setStatus = useMutation({
    mutationFn: (status: string) => jobsApi.updateStatus(job.id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })

  const sourceColor = job.source === 'linkedin' ? 'bg-blue-600' : 'bg-orange-500'

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <Link to={`/jobs/${job.id}`} className="font-semibold text-gray-900 hover:text-blue-600 line-clamp-1">
            {job.title}
          </Link>
          <p className="text-sm text-gray-600 truncate">{job.company}</p>
        </div>
        <span className={`text-white text-xs font-bold px-2 py-0.5 rounded uppercase shrink-0 ${sourceColor}`}>
          {job.source}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {job.remote_type && <StatusBadge status={job.remote_type} />}
        {job.employment_type && (
          <span className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded">
            {job.employment_type}
          </span>
        )}
        {job.location && (
          <span className="text-xs text-gray-500 flex items-center gap-1">
            📍 {job.location}
          </span>
        )}
      </div>

      <div className="mb-3">
        <ScoreBar score={job.claude_score} />
        {job.claude_summary && (
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{job.claude_summary}</p>
        )}
      </div>

      {job.status === 'pending_review' ? (
        <div className="flex gap-2">
          <button
            onClick={() => setStatus.mutate('approved')}
            disabled={setStatus.isPending}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-1.5 rounded transition-colors disabled:opacity-50"
          >
            Approve
          </button>
          <button
            onClick={() => setStatus.mutate('rejected')}
            disabled={setStatus.isPending}
            className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 text-sm font-medium py-1.5 rounded transition-colors disabled:opacity-50"
          >
            Reject
          </button>
          <button
            onClick={() => setStatus.mutate('skipped')}
            disabled={setStatus.isPending}
            className="px-3 bg-gray-100 hover:bg-gray-200 text-gray-500 text-sm font-medium py-1.5 rounded transition-colors disabled:opacity-50"
          >
            Skip
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <StatusBadge status={job.status} />
          <Link to={`/jobs/${job.id}`} className="text-xs text-blue-500 hover:underline">
            View details →
          </Link>
        </div>
      )}
    </div>
  )
}
