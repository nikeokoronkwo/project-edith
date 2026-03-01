<template>
  <div class="new-report-root">
    <h1 class="page-title">Submit Field Report</h1>

    <form @submit.prevent="onSubmit" class="report-form">
      <div class="form-group">
        <label for="heroAlias" class="form-label">Hero Alias</label>
        <input
          id="heroAlias"
          v-model="form.heroAlias"
          type="text"
          class="form-input"
          placeholder="e.g. Night Shift"
        />
        <p v-if="errors.heroAlias" class="error-msg">{{ errors.heroAlias }}</p>
      </div>

      <div class="form-group">
        <label for="description" class="form-label">Description</label>
        <textarea
          id="description"
          v-model="form.description"
          class="form-textarea"
          rows="4"
          placeholder="What happened? Be specific."
        ></textarea>
        <p v-if="errors.description" class="error-msg">{{ errors.description }}</p>
      </div>

      <div class="form-group">
        <label for="resources" class="form-label">Affected Resources (comma separated)</label>
        <input
          id="resources"
          v-model="resourcesText"
          type="text"
          class="form-input"
          placeholder="e.g. vibranium, energy_cells"
        />
      </div>

      <div class="form-group">
        <label for="locations" class="form-label">Affected Locations (comma separated)</label>
        <input
          id="locations"
          v-model="locationsText"
          type="text"
          class="form-input"
          placeholder="e.g. Wakanda, East Africa"
        />
      </div>

      <div class="form-group">
        <label for="related" class="form-label">Related Report IDs (comma separated)</label>
        <input
          id="related"
          v-model="relatedText"
          type="text"
          class="form-input"
          placeholder="rpt-001, rpt-002"
        />
      </div>

      <div class="form-actions">
        <button
          type="submit"
          :disabled="isLoading"
          class="submit-btn"
        >
          <Icon v-if="isLoading" name="svg-spinners:ring-resize" class="w-5 h-5" />
          <span>{{ isLoading ? 'Submitting...' : 'Send Report' }}</span>
        </button>
      </div>

      <div v-if="formError" class="submit-error">
        {{ formError }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' });
import { ref, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useCreateReport } from '@/composables/useCreateReport';
import { z } from 'zod';

const router = useRouter();
const { submitReport, isLoading, error: submitError } = useCreateReport();

const form = reactive({
  heroAlias: '',
  description: '',
  affectedResources: [] as string[],
  affectedLocations: [] as string[],
  relatedReportIds: [] as string[],
  timeStarted: ''
});

const resourcesText = ref('');
const locationsText = ref('');
const relatedText = ref('');

const errors = reactive<Record<string, string>>({});
const formError = ref<string>('');

const schema = z.object({
  heroAlias: z.string().min(1),
  description: z.string().min(10)
});

function toArray(str: string) {
  return str
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
}

watch(resourcesText, (v) => { form.affectedResources = toArray(v); });
watch(locationsText, (v) => { form.affectedLocations = toArray(v); });
watch(relatedText, (v) => { form.relatedReportIds = toArray(v); });

async function onSubmit() {
  Object.keys(errors).forEach(k => delete errors[k]);
  formError.value = '';

  const result = schema.safeParse(form);
  if (!result.success) {
    result.error.errors.forEach(e => {
      if (e.path[0]) errors[e.path[0] as string] = e.message;
    });
    return;
  }

  const payload = { ...form };
  if (!payload.timeStarted) {
    payload.timeStarted = new Date().toISOString();
  }

  const res = await submitReport(payload as any);
  if (res.success) {
    router.push('/reports');
  } else {
    formError.value = res.error || 'Failed to submit';
  }
}
</script>

<style scoped>
.new-report-root {
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 24px;
}

.report-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 0.875rem;
  margin-bottom: 4px;
  color: var(--foreground);
}

.form-input,
.form-textarea {
  padding: 8px 10px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--foreground);
}

.error-msg {
  color: #f87171;
  font-size: 0.75rem;
  margin-top: 2px;
}

.form-actions {
  margin-top: 12px;
}

.submit-btn {
  background: var(--shield-600);
  color: white;
  padding: 10px 16px;
  border-radius: var(--radius);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-error {
  color: #f87171;
  font-size: 0.875rem;
  margin-top: 8px;
}
</style>