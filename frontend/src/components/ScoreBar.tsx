export default function ScoreBar({ score }: { score: number | null }) {
  if (score === null) return <span className="text-gray-400 text-sm">Not scored</span>

  const color =
    score >= 75 ? 'bg-green-500' :
    score >= 60 ? 'bg-yellow-500' :
    'bg-red-400'

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${score}%` }} />
      </div>
      <span className={`text-sm font-bold w-8 text-right ${
        score >= 75 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : 'text-red-500'
      }`}>{score}</span>
    </div>
  )
}
