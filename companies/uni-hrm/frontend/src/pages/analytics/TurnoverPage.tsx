import { useTurnoverStats } from '@/features/documents/hooks';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function TurnoverPage() {
  const { data: turnover, isLoading } = useTurnoverStats(12);

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Анализ текучести кадров
      </h1>
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        {isLoading ? (
          <div>Загрузка...</div>
        ) : (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={turnover ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="hired_count"
                stroke="#4F46E5"
                name="Принято"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="dismissed_count"
                stroke="#EF4444"
                name="Уволено"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="turnover_rate"
                stroke="#F59E0B"
                name="Коэф. текучести"
                strokeWidth={2}
                dot={{ r: 4 }}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
