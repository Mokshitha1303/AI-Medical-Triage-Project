'use client'
import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import TriageResult from './TriageResult'
import { submitSymptoms } from '@/lib/api'
import { Message, TriageResponse } from '@/lib/types'

const INITIAL_MESSAGE: Message = {
  role: 'assistant',
  content: 'Hello! Please describe your symptoms in as much detail as you can — what you feel, when it started, and how severe it is.',
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [triageResult, setTriageResult] = useState<TriageResponse | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, triageResult, loading])

  const handleSubmit = async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setTriageResult(null)
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)

    try {
      const data = await submitSymptoms(text)
      setTriageResult(data)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I've analysed your symptoms. Here is my assessment:",
      }])
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Something went wrong. Please try again.'
      setMessages(prev => [...prev, { role: 'assistant', content: message }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      {/* Header */}
      <div className="border-b px-6 py-4 bg-white">
        <h1 className="text-lg font-semibold text-gray-900">AI Medical Triage</h1>
        <p className="text-xs text-gray-400">Not a substitute for professional medical advice</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-white">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <span className="animate-pulse">●</span>
            <span className="animate-pulse delay-100">●</span>
            <span className="animate-pulse delay-200">●</span>
            <span className="ml-1">Analysing symptoms…</span>
          </div>
        )}
        {triageResult && <TriageResult data={triageResult} />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t px-6 py-4 bg-white flex gap-3">
        <textarea
          className="flex-1 border rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Describe your symptoms…"
          disabled={loading}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit()
            }
          }}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          className="px-5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  )
}
