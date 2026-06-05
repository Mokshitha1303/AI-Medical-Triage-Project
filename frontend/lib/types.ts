export interface ConditionSuggested {
  name: string
  probability: string
  description: string
}

export interface TriageResponse {
  session_id: string
  urgency_level: 'er' | 'urgent_care' | 'gp' | 'self_care'
  confidence_score: number
  conditions_suggested: ConditionSuggested[]
  reasoning: string
  recommended_actions: string[]
  follow_up_questions: string[]
  disclaimer: string
  flagged_for_review: boolean
  flag_reason: string | null
  bypassed_ai: boolean
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
}
