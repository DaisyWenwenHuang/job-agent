import { useQuery } from '@tanstack/react-query'
import { applicationsApi } from '../api/client'
import type { Application } from '../types'
import StatusBadge from '../components/StatusBadge'

export default function ApplicationsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationsApi.list({ limit: 100 }).then(r => r.data as Application[]),
  })

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Applications</h1>
      {isLoading ? (
        <div className="text-center py-12 text-gray-400">Loading...</div>
      ) : !data?.length ? (
        <div className="text-center py-12 text-gray-400">No applications yet.</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Job</th>
                <th className="px-4 py-3 font-medium">Platform</th>
                <th className="px-4 py-3 font-medium">Method</th>
                <th className="px-4 py-3 font-medium">Applied</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.map(app => (
                <tr key={app.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-700 font-medium">{app.job_id.slice(0, 8)}…</td>
                  <td className="px-4 py-3">
                    <span className={`text-white text-xs font-bold px-2 py-0.5 rounded uppercase ${
                      app.platform === 'linkedin' ? 'bg-blue-600' : 'bg-orange-500'
                    }`}>{app.platform}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">{app.method ?? '—'}</td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(app.applied_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={app.status} />
                    {app.error_detail && (
                      <p className="text-xs text-red-400 mt-1 truncate max-w-xs">{app.error_detail}</p>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
