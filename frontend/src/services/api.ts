const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8001'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
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
}
