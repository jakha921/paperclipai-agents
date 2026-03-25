import { useDocumentTemplates } from '@/features/documents/hooks';
import { Link } from 'react-router-dom';

export default function DocumentTemplatesPage() {
  const { data: templates, isLoading } = useDocumentTemplates();

  if (isLoading) return <div className="p-6">Загрузка...</div>;

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Шаблоны документов
      </h1>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Название</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Код</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Формат</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Статус</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {(templates ?? []).map((tpl) => (
              <tr key={tpl.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-900">{tpl.name}</td>
                <td className="px-4 py-3 text-slate-500 font-mono text-xs">{tpl.code}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 uppercase">
                    {tpl.output_format}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      tpl.is_active
                        ? 'bg-green-50 text-green-700'
                        : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {tpl.is_active ? 'Активен' : 'Отключён'}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <Link
                    to={`/documents/generate?template=${tpl.code}`}
                    className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
                  >
                    Создать документ
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {templates?.length === 0 && (
          <div className="text-center py-12 text-slate-500">Нет шаблонов</div>
        )}
      </div>
    </div>
  );
}
