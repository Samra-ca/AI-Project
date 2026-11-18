import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { DashboardStats } from '../types'

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getDashboard()
      .then((data) => setStats(data as DashboardStats))
      .catch((err: Error) => setError(err.message))
  }, [])

  return { stats, error }
}
