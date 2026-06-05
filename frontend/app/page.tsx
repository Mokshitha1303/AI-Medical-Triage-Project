import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex flex-col items-center justify-center px-4">
      <div className="max-w-lg text-center space-y-6">
        <div className="text-5xl">🩺</div>
        <h1 className="text-4xl font-bold text-gray-900">AI Medical Triage</h1>
        <p className="text-lg text-gray-600">
          Describe your symptoms and get instant AI-powered triage guidance.
          All high-risk cases are reviewed by a doctor.
        </p>

        <div className="grid grid-cols-2 gap-3 text-sm text-left">
          {[
            { icon: '🚨', label: 'Emergency Room', color: 'text-red-600' },
            { icon: '⚠️', label: 'Urgent Care', color: 'text-orange-500' },
            { icon: '🩺', label: 'See Your Doctor', color: 'text-yellow-600' },
            { icon: '✅', label: 'Self-Care', color: 'text-green-600' },
          ].map(item => (
            <div key={item.label} className="flex items-center gap-2 bg-white rounded-lg p-3 shadow-sm border">
              <span>{item.icon}</span>
              <span className={`font-medium ${item.color}`}>{item.label}</span>
            </div>
          ))}
        </div>

        <Link
          href="/patient/chat"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-xl text-base font-semibold hover:bg-blue-700 transition-colors"
        >
          Start Symptom Check
        </Link>

        <p className="text-xs text-gray-400">
          Not a substitute for professional medical advice. In an emergency, call 911.
        </p>
      </div>
    </main>
  )
}
