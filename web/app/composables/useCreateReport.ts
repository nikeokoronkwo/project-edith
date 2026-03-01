import { z } from 'zod';

export const createReportSchema = z.object({
  heroAlias: z.string().min(1, 'Hero alias is required').max(100, 'Hero alias too long'),
  description: z.string().min(10, 'Description must be at least 10 characters').max(5000, 'Description too long'),
  affectedResources: z.array(z.string()).default([]),
  affectedLocations: z.array(z.string()).default([]),
  relatedReportIds: z.array(z.string()).default([]),
  timeStarted: z.string().datetime().optional(),
});

export type CreateReportInput = z.infer<typeof createReportSchema>;

export interface CreateReportResponse {
  success: boolean;
  reportId: string;
  timestamp: string;
  message: string;
}

export function useCreateReport() {
  const { data, pending, error, execute } = useFetch<CreateReportResponse>('/api/reports/new', {
    method: 'POST',
    immediate: false,
    body: null
  });

  const isLoading = ref(false);
  const submitError = ref<string | null>(null);

  async function submitReport(input: CreateReportInput) {
    isLoading.value = true;
    submitError.value = null;

    const validation = createReportSchema.safeParse(input);
    if (!validation.success) {
      submitError.value = validation.error.errors.map(e => e.message).join(', ');
      isLoading.value = false;
      return { success: false, error: submitError.value };
    }

    try {
      const response = await $fetch<CreateReportResponse>('/api/reports/new', {
        method: 'POST',
        body: validation.data
      });

      return {
        success: response.success,
        reportId: response.reportId,
        timestamp: response.timestamp,
        message: response.message
      };
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'Failed to submit report';
      submitError.value = errorMessage;
      return { success: false, error: errorMessage };
    } finally {
      isLoading.value = false;
    }
  }

  return {
    submitReport,
    isLoading: computed(() => isLoading.value),
    error: computed(() => submitError.value)
  };
}

export function useLazyCreateReport() {
  const isLoading = ref(false);
  const submitError = ref<string | null>(null);

  async function submitReport(input: CreateReportInput) {
    isLoading.value = true;
    submitError.value = null;

    const validation = createReportSchema.safeParse(input);
    if (!validation.success) {
      submitError.value = validation.error.errors.map(e => e.message).join(', ');
      isLoading.value = false;
      return { success: false, error: submitError.value };
    }

    try {
      const response = await $fetch<CreateReportResponse>('/api/reports/new', {
        method: 'POST',
        body: validation.data
      });

      return {
        success: response.success,
        reportId: response.reportId,
        timestamp: response.timestamp,
        message: response.message
      };
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'Failed to submit report';
      submitError.value = errorMessage;
      return { success: false, error: errorMessage };
    } finally {
      isLoading.value = false;
    }
  }

  return {
    submitReport,
    isLoading: computed(() => isLoading.value),
    error: computed(() => submitError.value)
  };
}
