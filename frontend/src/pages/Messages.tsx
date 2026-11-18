import { useEffect, useState } from 'react'
import { MessageTable } from '../components/MessageTable'
import { api } from '../services/api'

interface ApiMessage {
  id: number
  sender: string
  date: string
  content: string
  status: string
}

export function Messages() {
  const [messages, setMessages] = useState<ApiMessage[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getMessages()
      .then((data) => setMessages(data as ApiMessage[]))
      .catch((err: Error) => setError(err.message))
  }, [])

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">Message Center</h1>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <MessageTable
        rows={messages.map((m) => ({
          id: String(m.id),
          sender: m.sender,
          date: m.date,
          content: m.content,
          status: m.status as 'accepted' | 'partially_accepted' | 'rejected' | 'pending',
        }))}
      />
    </div>
  )
}
