const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8001'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init)
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(body || `${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  getDashboard: () => request('/api/dashboard'),
  getMessages: () => request('/api/messages'),
  getPlanCurrent: () => request('/api/plan/current'),
  getPlanHistory: () => request('/api/plan/history'),
  getTrace: () => request('/api/trace'),
  getValidation: () => request('/api/validation'),
  getBudget: () => request('/api/budget'),
  getDecisions: () => request('/api/decisions'),

  runPlan: () => request('/api/run', { method: 'POST' }),
  runUpdate: () => request('/api/update', { method: 'POST' }),

  addMessage: (sender: string, message: string) =>
    request('/api/messages/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender, message }),
    }),

  uploadMessages: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request('/api/messages/upload', { method: 'POST', body: formData })
  },

  approveDecision: (id: number) => request(`/api/decisions/${id}/approve`, { method: 'POST' }),
  rejectDecision: (id: number) => request(`/api/decisions/${id}/reject`, { method: 'POST' }),
}
