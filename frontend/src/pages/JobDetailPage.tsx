import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsApi } from '../api/client'
import type { Job } from '../types'
import StatusBadge from '../components/StatusBadge'
import ScoreBar from '../components/ScoreBar'

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: job, isLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.get(id!).then(r => r.data as Job),
  })

  const setStatus = useMutation({
    mutationFn: (status: string) => jobsApi.updateStatus(id!, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['job', id] })
      qc.invalidateQueries({ queryKey: ['jobs'] })
    },
  })

  const applyNow = useMutation({
    mutationFn: () => jobsApi.apply(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['job', id] }),
  })

  if (isLoading) return <div className="text-center py-12 text-gray-400">Loading...</div>
  if (!job) return <div className="text-center py-12 text-gray-500">Job not found</div>

  const reasoning: string[] = job.claude_reasoning ? JSON.parse(job.claude_reasoning) : []
  const redFlags: string[] = job.claude_red_flags ? JSON.parse(job.claude_red_flags) : []

  return (
    <div className="max-w-3xl">
      <button onClick={() => navigate(-1)} className="text-blue-500 hover:underline text-sm mb-4 block">
        ← Back
      </button>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
            <p className="text-lg text-gray-600 mt-1">{job.company}</p>
            <div className="flex flex-wrap gap-2 mt-2">
              {job.remote_type && <StatusBadge status={job.remote_type} />}
              {job.employment_type && (
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                  {job.employment_type}
                </span>
              )}
              {job.location && <span className="text-xs text-gray-500">📍 {job.location}</span>}
              {job.salary_range && <span className="text-xs text-gray-500">💰 {job.salary_range}</span>}
            </div>
          </div>
          <div className="flex flex-col items-end gap-2 shrink-0">
            <span className={`text-white text-xs font-bold px-2 py-1 rounded uppercase ${
              job.source === 'linkedin' ? 'bg-blue-600' : 'bg-orange-500'
            }`}>{job.source}</span>
            <StatusBadge status={job.status} />
            <a href={job.url} target="_blank" rel="noreferrer"
               className="text-xs text-blue-500 hover:underline">
              View original ↗
            </a>
          </div>
        </div>

        {/* Claude Score */}
        {job.claude_score !== null && (
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-gray-700 mb-2">AI Match Score</h3>
            <ScoreBar score={job.claude_score} />
            {job.claude_summary && (
              <p className="text-sm text-gray-600 mt-2">{job.claude_summary}</p>
            )}
            {reasoning.length > 0 && (
              <ul className="mt-3 space-y-1">
                {reasoning.map((r, i) => (
                  <li key={i} className="text-sm text-gray-600 flex gap-2">
                    <span className="text-blue-400 shrink-0">•</span>
                    {r}
                  </li>
                ))}
              </ul>
            )}
            {redFlags.length > 0 && (
              <div className="mt-3 bg-red-50 rounded p-3">
                <p className="text-xs font-semibold text-red-600 mb-1">Red flags:</p>
                {redFlags.map((f, i) => (
                  <p key={i} className="text-xs text-red-600">⚠ {f}</p>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        {job.status === 'pending_review' && (
          <div className="flex gap-3 mb-4">
            <button onClick={() => setStatus.mutate('approved')}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 rounded-lg transition-colors">
              ✓ Approve
            </button>
            <button onClick={() => setStatus.mutate('rejected')}
              className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 font-medium py-2 rounded-lg transition-colors">
              ✗ Reject
            </button>
            <button onClick={() => setStatus.mutate('skipped')}
              className="px-4 bg-gray-100 hover:bg-gray-200 text-gray-500 font-medium py-2 rounded-lg transition-colors">
              Skip
            </button>
          </div>
        )}
        {job.status === 'approved' && (
          <button onClick={() => applyNow.mutate()}
            disabled={applyNow.isPending}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors disabled:opacity-50 mb-4">
            {applyNow.isPending ? 'Applying...' : '🚀 Apply Now'}
          </button>
        )}
      </div>

      {/* Job Description */}
      {job.description && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Job Description</h3>
          <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed">
            {job.description}
          </pre>
        </div>
      )}
    </div>
  )
}
