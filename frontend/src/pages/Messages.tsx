import { MessageTable } from '../components/MessageTable'

export function Messages() {
  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold text-white">Message Center</h1>
      <MessageTable rows={[]} />
    </div>
  )
}
