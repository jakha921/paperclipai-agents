import { useState } from 'react';
import { useDocumentTemplates, useGenerateDocument } from '@/features/documents/hooks';
import { useSearchParams } from 'react-router-dom';
import type { GeneratedDocument } from '@/features/documents/types';

export default function GenerateDocumentPage() {
  const [searchParams] = useSearchParams();
  const [templateCode, setTemplateCode] = useState(searchParams.get('template') ?? '');
  const [employeeId, setEmployeeId] = useState('');
  const [generatedDoc, setGeneratedDoc] = useState<Pick<
    GeneratedDocument,
    'file_url' | 'id'
  > | null>(null);

  const { data: templates } = useDocumentTemplates();
  const generateMutation = useGenerateDocument();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const doc = await generateMutation.mutateAsync({
      template_code: templateCode,
      employee_id: employeeId,
    });
    setGeneratedDoc(doc);
  };

  return (
    <div className="p-6 max-w-2xl">
      <h1
        className="text-2xl font-bold text-slate-900 mb-6"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Создать документ
      </h1>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Шаблон</label>
            <select
              value={templateCode}
              onChange={(e) => setTemplateCode(e.target.value)}
              required
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Выберите шаблон</option>
              {(templates ?? []).map((t) => (
                <option key={t.code} value={t.code}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              ID Сотрудника
            </label>
            <input
              type="text"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              required
              placeholder="UUID сотрудника"
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={generateMutation.isPending}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {generateMutation.isPending ? 'Создание...' : 'Создать документ'}
          </button>
        </form>

        {generateMutation.isError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
            Ошибка при создании документа
          </div>
        )}

        {generatedDoc && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
            <p className="text-sm font-medium text-green-800">Документ создан!</p>
            {generatedDoc.file_url && (
              <a
                href={generatedDoc.file_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 bg-indigo-600 text-white px-3 py-1.5 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                Скачать PDF
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
