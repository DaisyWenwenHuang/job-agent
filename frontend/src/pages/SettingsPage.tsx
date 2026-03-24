import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { configApi } from '../api/client'
import type { JobConfig } from '../types'

export default function SettingsPage() {
  const qc = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data: config, isLoading } = useQuery({
    queryKey: ['config'],
    queryFn: () => configApi.get().then(r => r.data as JobConfig),
  })

  const [localConfig, setLocalConfig] = useState<JobConfig | null>(null)
  const current = localConfig ?? config

  const save = useMutation({
    mutationFn: (cfg: JobConfig) => configApi.put(cfg),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['config'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  if (isLoading || !current) return <div className="text-center py-12 text-gray-400">Loading...</div>

  const update = (patch: Partial<JobConfig>) => {
    setLocalConfig({ ...(localConfig ?? config!), ...patch })
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

      <div className="space-y-6">
        {/* Target Roles */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-3">Target Roles</h3>
          <textarea
            rows={4}
            value={current.target_roles.join('\n')}
            onChange={e => update({ target_roles: e.target.value.split('\n').filter(Boolean) })}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-200"
            placeholder="One role per line"
          />
          <p className="text-xs text-gray-400 mt-1">One role per line</p>
        </div>

        {/* Location */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-3">Location</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500">City</label>
              <input value={current.location.city}
                onChange={e => update({ location: { ...current.location, city: e.target.value } })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-blue-200" />
            </div>
            <div>
              <label className="text-xs text-gray-500">State</label>
              <input value={current.location.state}
                onChange={e => update({ location: { ...current.location, state: e.target.value } })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-blue-200" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Max miles (onsite)</label>
              <input type="number" value={current.location.max_miles_onsite}
                onChange={e => update({ location: { ...current.location, max_miles_onsite: Number(e.target.value) } })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-blue-200" />
            </div>
          </div>
        </div>

        {/* Score threshold + apply limit */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-3">Scoring & Applying</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-700">Min Claude score to show</label>
              <div className="flex items-center gap-2">
                <input type="range" min={0} max={100} step={5}
                  value={current.min_claude_score}
                  onChange={e => update({ min_claude_score: Number(e.target.value) })}
                  className="w-28" />
                <span className="text-sm font-medium w-8 text-right">{current.min_claude_score}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-700">Daily apply limit</label>
              <input type="number" value={current.daily_apply_limit}
                onChange={e => update({ daily_apply_limit: Number(e.target.value) })}
                className="w-20 border border-gray-200 rounded px-2 py-1 text-sm text-right" />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-gray-700">Auto-apply (no review)</label>
              <input type="checkbox" checked={current.apply_automatically}
                onChange={e => update({ apply_automatically: e.target.checked })}
                className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* Scheduler */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-3">Scheduler</h3>
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-700">Daily run time</label>
            <input type="time" value={current.scheduler.run_time}
              onChange={e => update({ scheduler: { ...current.scheduler, run_time: e.target.value } })}
              className="border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
        </div>

        <button
          onClick={() => save.mutate(current)}
          disabled={save.isPending}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {saved ? '✓ Saved!' : save.isPending ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
