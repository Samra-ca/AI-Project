import { Check, ShieldAlert, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Badge } from '../components/Badge'
import { PageHeader } from '../components/PageHeader'
import { api } from '../services/api'

interface ValidationCheck {
  checkName: string
  passed: boolean
  details: string
}

interface Decision {
  id: number
  sender: string
  message: string
  area: string
  decisionText: string
  accepted: boolean
  reason: string
}

export function Validation() {
  const [checks, setChecks] = useState<ValidationCheck[]>([])
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<number | null>(null)

  function load() {
    api
      .getValidation()
      .then((data) => setChecks(data as ValidationCheck[]))
      .catch((err: Error) => setError(err.message))
    api
      .getDecisions()
      .then((data) => setDecisions(data as Decision[]))
      .catch((err: Error) => setError(err.message))
  }

  useEffect(load, [])

  async function handleApprove(id: number) {
    setBusyId(id)
    setError(null)
    try {
      await api.approveDecision(id)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Approve failed')
    } finally {
      setBusyId(null)
    }
  }

  async function handleReject(id: number) {
    setBusyId(id)
    setError(null)
    try {
      await api.rejectDecision(id)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Reject failed')
    } finally {
      setBusyId(null)
    }
  }

  const rejected = decisions.filter((d) => !d.accepted)

  return (
    <div>
      <PageHeader
        icon={ShieldAlert}
        title="Validation & Rejections"
        subtitle="Six final checks, plus every rejected message and why"
      />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      {busyId !== null && (
        <p className="mb-4 text-sm text-violet-600">
          Re-running the plan with this change - this calls the model again, so it can take
          ~30 seconds...
        </p>
      )}

      <h2 className="mb-2 text-sm font-semibold text-slate-700">Validation Checks</h2>
      <ul className="mb-6 space-y-2">
        {checks.map((check) => (
          <li
            key={check.checkName}
            className="flex items-start justify-between rounded-xl border border-slate-200 bg-white p-3 shadow-sm"
          >
            <div>
              <p className="text-sm font-medium text-slate-800">{check.checkName}</p>
              <p className="text-xs text-slate-500">{check.details}</p>
            </div>
            <Badge tone={check.passed ? 'green' : 'red'}>
              {check.passed ? 'PASS' : 'FAIL'}
            </Badge>
          </li>
        ))}
      </ul>

      <h2 className="mb-2 text-sm font-semibold text-slate-700">
        Rejected Messages ({rejected.length})
      </h2>
      <ul className="space-y-2">
        {rejected.length === 0 && (
          <li className="rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-400 shadow-sm">
            Nothing rejected right now.
          </li>
        )}
        {rejected.map((d) => (
          <li
            key={d.id}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs text-slate-400">
                  {d.sender} &middot; <span className="capitalize">{d.area}</span>
                </p>
                <p className="mt-1 text-sm text-slate-800">{d.message}</p>
                <p className="mt-1 text-xs text-red-500">{d.reason}</p>
              </div>
              <div className="flex shrink-0 gap-2">
                <button
                  type="button"
                  onClick={() => handleApprove(d.id)}
                  disabled={busyId === d.id}
                  className="flex items-center gap-1 rounded-lg bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                >
                  <Check size={14} />
                  Approve
                </button>
                <button
                  type="button"
                  onClick={() => handleReject(d.id)}
                  disabled={busyId === d.id}
                  className="flex items-center gap-1 rounded-lg bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 disabled:opacity-60"
                >
                  <X size={14} />
                  Confirm Reject
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
