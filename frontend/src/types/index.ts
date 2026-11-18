export interface DashboardStats {
  totalStudents: number
  totalTeams: number
  staffCount: number
  judgeCount: number
  approvedBudget: number
  estimatedExpenditure: number
  remainingBudget: number
  processedMessages: number
  acceptedMessages: number
  rejectedMessages: number
}

export interface ModelTraceEntry {
  callNumber: number
  modelName: string
  area: 'reading' | 'venue' | 'schedule' | 'food' | 'judging' | 'budget'
  input: string
  output: string
  inputTokens: number
  outputTokens: number
  totalTokens: number
  durationMs: number
}
