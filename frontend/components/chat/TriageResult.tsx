import { TriageResponse } from '@/lib/types'

const URGENCY_CONFIG = {
  er: {
    label: 'Emergency Room — Go Now',
    bg: 'bg-red-50 border-red-200',
    badge: 'bg-red-100 text-red-800',
    icon: '🚨',
  },
  urgent_care: {
    label: 'Urgent Care',
    bg: 'bg-orange-50 border-orange-200',
    badge: 'bg-orange-100 text-orange-800',
    icon: '⚠️',
  },
  gp: {
    label: 'See Your Doctor',
    bg: 'bg-yellow-50 border-yellow-200',
    badge: 'bg-yellow-100 text-yellow-800',
    icon: '🩺',
  },
  self_care: {
    label: 'Self-Care at Home',
    bg: 'bg-green-50 border-green-200',
    badge: 'bg-green-100 text-green-800',
    icon: '✅',
  },
}

const PROBABILITY_COLORS: Record<string, string> = {
  high: 'text-red-600 font-medium',
  medium: 'text-orange-500 font-medium',
  low: 'text-gray-400',
}

export default function TriageResult({ data }: { data: TriageResponse }) {
  const config = URGENCY_CONFIG[data.urgency_level] ?? URGENCY_CONFIG.self_care
  const confidence = Math.round(data.confidence_score * 100)

  return (
    <div className={`rounded-xl border p-5 space-y-4 ${config.bg}`}>
      {/* Urgency badge */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold ${config.badge}`}>
          <span>{config.icon}</span>
          {config.label}
        </span>
        <span className="text-xs text-gray-500">
          Confidence: {confidence}%
          {data.bypassed_ai && ' · Safety rule triggered'}
          {data.flagged_for_review && ' · Flagged for doctor review'}
        </span>
      </div>

      {/* Possible conditions */}
      {data.conditions_suggested.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Possible conditions</h3>
          <ul className="space-y-1">
            {data.conditions_suggested.map((c, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className={`w-12 shrink-0 ${PROBABILITY_COLORS[c.probability] ?? 'text-gray-400'}`}>
                  {c.probability}
                </span>
                <span className="text-gray-700">
                  <span className="font-medium">{c.name}</span>
                  {c.description && ` — ${c.description}`}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended actions */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Recommended actions</h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
          {data.recommended_actions.map((a, i) => (
            <li key={i}>{a}</li>
          ))}
        </ul>
      </div>

      {/* Follow-up questions */}
      {data.follow_up_questions.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">The doctor may ask</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-500">
            {data.follow_up_questions.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-gray-400 border-t border-current/10 pt-3">{data.disclaimer}</p>
    </div>
  )
}
