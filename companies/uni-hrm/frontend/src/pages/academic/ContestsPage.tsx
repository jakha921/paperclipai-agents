import { useState } from 'react';
import { Trophy } from 'lucide-react';
import { usePositionContests, useCloseContest, useSetContestWinner } from '@/features/academic';
import type { ContestStatus } from '@/features/academic';
import { CONTEST_STATUS_LABELS, CONTEST_STATUS_COLORS } from '@/shared/constants/statuses';
import { useTranslation } from 'react-i18next';

export default function ContestsPage() {
  const { t } = useTranslation();
  const { data, isLoading } = usePositionContests();
  const closeContest = useCloseContest();
  const setWinner = useSetContestWinner();

  const [winnerModal, setWinnerModal] = useState<{ contestId: number } | null>(null);
  const [winnerId, setWinnerId] = useState('');

  const contests = data?.results ?? [];

  const handleSetWinner = () => {
    if (!winnerModal || !winnerId) return;
    setWinner.mutate(
      { id: winnerModal.contestId, winnerId: Number(winnerId) },
      {
        onSuccess: () => {
          setWinnerModal(null);
          setWinnerId('');
        },
      },
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'var(--font-heading)' }}>
          {t('academic.contests')}
        </h1>
        <p className="text-sm text-slate-500 mt-1">{t('academic.contestsDescription')}</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-slate-200 animate-pulse rounded-lg" />
            ))}
          </div>
        ) : contests.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <Trophy className="h-12 w-12 mb-3" />
            <p className="text-sm font-medium">{t('academic.noContests')}</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.department')}</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.position')}</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.deadline')}</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">{t('academic.status')}</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">{t('academic.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {contests.map((c) => (
                <tr key={c.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-900">{c.department}</td>
                  <td className="px-4 py-3 text-slate-600">{c.position}</td>
                  <td className="px-4 py-3 text-slate-600">{c.application_deadline}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {(c.status === 'OPEN' || c.status === 'REVIEWING') && (
                        <button
                          onClick={() => closeContest.mutate(c.id)}
                          disabled={closeContest.isPending}
                          className="px-3 py-1 text-xs font-medium bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors disabled:opacity-50"
                        >
                          {t('academic.close')}
                        </button>
                      )}
                      {c.status === 'REVIEWING' && (
                        <button
                          onClick={() => setWinnerModal({ contestId: c.id })}
                          className="px-3 py-1 text-xs font-medium bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 transition-colors"
                        >
                          {t('academic.assignWinner')}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Winner Modal */}
      {winnerModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-md w-full max-w-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold font-heading text-slate-900">
              {t('academic.assignWinner')}
            </h2>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                {t('academic.winnerId')}
              </label>
              <input
                type="number"
                value={winnerId}
                onChange={(e) => setWinnerId(e.target.value)}
                className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="ID"
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  setWinnerModal(null);
                  setWinnerId('');
                }}
                className="flex-1 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
              >
                {t('actions.cancel')}
              </button>
              <button
                onClick={handleSetWinner}
                disabled={!winnerId || setWinner.isPending}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {setWinner.isPending ? '...' : t('actions.save')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: ContestStatus }) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${CONTEST_STATUS_COLORS[status] ?? ''}`}
    >
      {CONTEST_STATUS_LABELS[status] ?? status}
    </span>
  );
}
