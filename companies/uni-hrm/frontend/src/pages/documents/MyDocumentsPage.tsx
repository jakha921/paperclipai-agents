import { useGeneratedDocuments } from '@/features/documents/hooks';

export default function MyDocumentsPage() {
  const { data: docs, isLoading } = useGeneratedDocuments();

  if (isLoading) return <div className="p-6">Загрузка...</div>;

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Мои документы
      </h1>
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Тип документа</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Сотрудник</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Дата</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {(docs ?? []).map((doc) => (
              <tr key={doc.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium text-slate-900">{doc.template_name}</td>
                <td className="px-4 py-3 text-slate-600">{doc.employee_name}</td>
                <td className="px-4 py-3 text-slate-500">
                  {new Date(doc.generated_at).toLocaleDateString('ru-RU')}
                </td>
                <td className="px-4 py-3 text-right">
                  {doc.file_url && (
                    <a
                      href={doc.file_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
                    >
                      Скачать
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {docs?.length === 0 && (
          <div className="text-center py-12 text-slate-500">Нет документов</div>
        )}
      </div>
    </div>
  );
}
