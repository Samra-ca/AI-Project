import { useCallback, useEffect, useState } from 'react'
import { api } from '../services/api'
import type { DashboardStats } from '../types'

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refetch = useCallback(() => {
    return api
      .getDashboard()
      .then((data) => {
        setStats(data as DashboardStats)
        setError(null)
      })
      .catch((err: Error) => setError(err.message))
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { stats, error, refetch }
}
