import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import type {
  TaxConfiguration,
  EmployeeSalary,
  Payroll,
  PayrollStatus,
  BulkCalculateRequest,
  BulkCalculateResult,
} from './types';

// Tax Configurations
export function useTaxConfigurations() {
  return useQuery({
    queryKey: ['tax-configurations'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: TaxConfiguration[]; count: number }>(
        '/payroll/tax-configs/',
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

// Employee Salaries
export function useEmployeeSalaries(filters?: { employee?: number; is_active?: boolean }) {
  return useQuery({
    queryKey: ['employee-salaries', filters],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: EmployeeSalary[]; count: number }>(
        '/payroll/salaries/',
        { params: filters },
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateEmployeeSalary() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (salaryData: Partial<EmployeeSalary>) => {
      const { data } = await apiClient.post<EmployeeSalary>('/payroll/salaries/', salaryData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-salaries'] });
    },
  });
}

export function useUpdateEmployeeSalary() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data: salaryData }: { id: number; data: Partial<EmployeeSalary> }) => {
      const { data } = await apiClient.patch<EmployeeSalary>(
        `/payroll/salaries/${id}/`,
        salaryData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-salaries'] });
    },
  });
}

// Payrolls
export function usePayrolls(filters?: { month?: number; year?: number; status?: PayrollStatus }) {
  return useQuery({
    queryKey: ['payrolls', filters],
    queryFn: async () => {
      const { data } = await apiClient.get<{ results: Payroll[]; count: number }>(
        '/payroll/payrolls/',
        { params: filters },
      );
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function usePayroll(id: number) {
  return useQuery({
    queryKey: ['payrolls', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Payroll>(`/payroll/payrolls/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function usePayslip(id: number) {
  return useQuery({
    queryKey: ['payrolls', id, 'payslip'],
    queryFn: async () => {
      const { data } = await apiClient.get<Payroll>(`/payroll/payrolls/${id}/payslip/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCalculatePayroll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.post<Payroll>(`/payroll/payrolls/${id}/calculate/`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
  });
}

export function useBulkCalculatePayroll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (requestData: BulkCalculateRequest) => {
      const { data } = await apiClient.post<BulkCalculateResult>(
        '/payroll/payrolls/bulk_calculate/',
        requestData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
  });
}

export function useApprovePayroll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.post<Payroll>(`/payroll/payrolls/${id}/approve/`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
  });
}

export function useMarkPaidPayroll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, paid_date }: { id: number; paid_date?: string }) => {
      const { data } = await apiClient.post<Payroll>(`/payroll/payrolls/${id}/mark_paid/`, {
        paid_date,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
  });
}
