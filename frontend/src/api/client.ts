import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const jobsApi = {
  list: (params?: Record<string, unknown>) => api.get('/jobs', { params }),
  get: (id: string) => api.get(`/jobs/${id}`),
  updateStatus: (id: string, status: string) => api.patch(`/jobs/${id}/status`, { status }),
  apply: (id: string) => api.post(`/jobs/${id}/apply`),
  delete: (id: string) => api.delete(`/jobs/${id}`),
}

export const applicationsApi = {
  list: (params?: Record<string, unknown>) => api.get('/applications', { params }),
  get: (id: string) => api.get(`/applications/${id}`),
}

export const runsApi = {
  list: () => api.get('/runs'),
  get: (id: string) => api.get(`/runs/${id}`),
  status: () => api.get('/runs/status'),
  trigger: () => api.post('/runs/trigger'),
}

export const configApi = {
  get: () => api.get('/config'),
  put: (config: unknown) => api.put('/config', config),
}
