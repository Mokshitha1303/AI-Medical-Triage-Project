import { TriageResponse } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export async function submitSymptoms(symptoms: string): Promise<TriageResponse> {
  const res = await fetch(`${API_URL}/api/triage/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symptoms }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Triage request failed')
  }
  return res.json()
}
