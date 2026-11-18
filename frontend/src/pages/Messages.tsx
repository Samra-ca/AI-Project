import { MessageSquare, Send, Upload } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { MessageTable } from '../components/MessageTable'
import { PageHeader } from '../components/PageHeader'
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
  const [sender, setSender] = useState('')
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function load() {
    api
      .getMessages()
      .then((data) => setMessages(data as ApiMessage[]))
      .catch((err: Error) => setError(err.message))
  }

  useEffect(load, [])

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!sender.trim() || !text.trim()) return
    setBusy(true)
    setError(null)
    try {
      await api.addMessage(sender.trim(), text.trim())
      setSender('')
      setText('')
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add message')
    } finally {
      setBusy(false)
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      await api.uploadMessages(file)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setBusy(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div>
      <PageHeader
        icon={MessageSquare}
        title="Message Center"
        subtitle="Upload a pack or add messages one at a time"
        action={
          <>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt"
              onChange={handleUpload}
              className="hidden"
              id="upload-input"
            />
            <label
              htmlFor="upload-input"
              className="flex cursor-pointer items-center gap-2 rounded-lg bg-white/15 px-4 py-2 text-sm font-medium text-white hover:bg-white/25"
            >
              <Upload size={16} />
              Upload .txt
            </label>
          </>
        }
      />
      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
      {busy && <p className="mb-4 text-sm text-violet-600">Processing - re-running the plan...</p>}

      <form
        onSubmit={handleAdd}
        className="mb-6 flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-end"
      >
        <div className="flex-1">
          <label className="mb-1 block text-xs font-medium text-slate-500">Sender</label>
          <input
            value={sender}
            onChange={(e) => setSender(e.target.value)}
            placeholder="e.g. Finance, email"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none"
          />
        </div>
        <div className="flex-[2]">
          <label className="mb-1 block text-xs font-medium text-slate-500">Message</label>
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type the new message..."
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={busy}
          className="flex items-center justify-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-60"
        >
          <Send size={16} />
          Add
        </button>
      </form>

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
