import { useEffect, useState } from 'react'
import { api } from '../services/api'

interface ValidationCheck {
  checkName: string
  passed: boolean
  details: string
}

export function Validation() {
  const [checks, setChecks] = useState<ValidationCheck[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getValidation()
      .then((data) => setChecks(data as ValidationCheck[]))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">Validation & Rejections</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <ul className="space-y-2">
        {checks.map((check) => (
          <li
            key={check.checkName}
            className="flex items-start justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-3"
          >
            <div>
              <p className="text-sm font-medium text-white">{check.checkName}</p>
              <p className="text-xs text-slate-400">{check.details}</p>
            </div>
            <span
              className={
                check.passed
                  ? 'rounded-full bg-emerald-600/20 px-2 py-0.5 text-xs text-emerald-300'
                  : 'rounded-full bg-red-600/20 px-2 py-0.5 text-xs text-red-300'
              }
            >
              {check.passed ? 'PASS' : 'FAIL'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
