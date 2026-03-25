declare module 'd3-org-chart' {
  export class OrgChart {
    container(el: string | HTMLDivElement): this;
    data(data: Record<string, unknown>[]): this;
    nodeWidth(fn: () => number): this;
    nodeHeight(fn: () => number): this;
    nodeContent(fn: (d: Record<string, unknown>) => string): this;
    render(): this;
  }
}
