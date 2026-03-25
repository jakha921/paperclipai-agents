import { useEffect, useRef } from 'react';
import { GitFork } from 'lucide-react';
import { useOrgChart } from '../../features/departments/api';
import { PageHeader, Card, Skeleton } from '../../shared/ui';

export default function OrgChartPage() {
  const chartRef = useRef<HTMLDivElement>(null);
  const { data: nodes, isLoading } = useOrgChart();

  useEffect(() => {
    if (!nodes || !chartRef.current || nodes.length === 0) return;

    const initChart = async () => {
      try {
        const { OrgChart } = await import('d3-org-chart');
        const chart = new OrgChart();
        chart
          .container(chartRef.current as string & HTMLDivElement)
          .data(
            nodes.map((n) => ({
              ...n,
              nodeId: n.id,
              parentNodeId: n.parentId,
            })),
          )
          .nodeWidth(() => 200)
          .nodeHeight(() => 80)
          .nodeContent(
            (d: Record<string, unknown>) => `
            <div style="
              background: white;
              border: 1px solid #E2E8F0;
              border-radius: 8px;
              padding: 12px;
              font-family: 'Plus Jakarta Sans', sans-serif;
              box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            ">
              <div style="font-size:13px;font-weight:600;color:#0F172A">${(d.data as Record<string, unknown>).name}</div>
              <div style="font-size:11px;color:#64748B;margin-top:2px">${(d.data as Record<string, unknown>).code}</div>
              <div style="font-size:11px;color:#6366F1;margin-top:4px">${(d.data as Record<string, unknown>).employee_count} сотр.</div>
              ${(d.data as Record<string, unknown>).head_name ? `<div style="font-size:10px;color:#94A3B8;margin-top:2px">${(d.data as Record<string, unknown>).head_name}</div>` : ''}
            </div>
          `,
          )
          .render();
      } catch {
        // d3-org-chart failed to initialize — likely missing data or DOM not ready
      }
    };

    initChart();
  }, [nodes]);

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Орг. схема"
        description="Организационная структура университета"
      />
      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="p-8 flex justify-center">
            <Skeleton className="h-96 w-full" />
          </div>
        ) : !nodes || nodes.length === 0 ? (
          <div className="p-8 text-center">
            <GitFork className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">Нет данных для отображения</p>
          </div>
        ) : (
          <div ref={chartRef} style={{ width: '100%', height: '600px' }} />
        )}
      </Card>
    </div>
  );
}
