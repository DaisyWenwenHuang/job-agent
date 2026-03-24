const colors: Record<string, string> = {
  pending_review: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-blue-100 text-blue-800',
  rejected: 'bg-red-100 text-red-800',
  applied: 'bg-green-100 text-green-800',
  skipped: 'bg-gray-100 text-gray-500',
  submitted: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  requires_manual: 'bg-orange-100 text-orange-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  remote: 'bg-teal-100 text-teal-700',
  hybrid: 'bg-purple-100 text-purple-700',
  onsite: 'bg-gray-100 text-gray-700',
}

export default function StatusBadge({ status }: { status: string }) {
  const cls = colors[status] ?? 'bg-gray-100 text-gray-600'
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${cls}`}>
      {status.replace('_', ' ')}
    </span>
  )
}
