<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div v-if="error" class="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
      {{ error }}
    </div>

    <div>
      <label for="email" class="block text-sm font-medium text-gray-300 mb-2">
        Agent Email
      </label>
      <input
        id="email"
        v-model="form.email"
        type="email"
        :class="[
          'w-full px-4 py-3 bg-iron-800 border rounded-lg focus:ring-2 focus:ring-shield-500 focus:border-transparent outline-none transition-all',
          errors.email ? 'border-red-500' : 'border-iron-600'
        ]"
        placeholder="agent@shield.gov"
      />
      <p v-if="errors.email" class="mt-1 text-sm text-red-400">{{ errors.email }}</p>
    </div>

    <div>
      <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
        Password
      </label>
      <input
        id="password"
        v-model="form.password"
        type="password"
        :class="[
          'w-full px-4 py-3 bg-iron-800 border rounded-lg focus:ring-2 focus:ring-shield-500 focus:border-transparent outline-none transition-all',
          errors.password ? 'border-red-500' : 'border-iron-600'
        ]"
        placeholder="••••••••"
      />
      <p v-if="errors.password" class="mt-1 text-sm text-red-400">{{ errors.password }}</p>
    </div>

    <button
      type="submit"
      :disabled="loading"
      class="w-full bg-shield-600 hover:bg-shield-500 disabled:bg-shield-800 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
    >
      <Icon v-if="loading" name="svg-spinners:ring-resize" class="w-5 h-5" />
      <span>{{ loading ? 'Authenticating...' : 'Access Edith' }}</span>
    </button>

    <p class="text-center text-gray-500 text-sm">
      Restricted access. Authorized agents only.
    </p>
  </form>
</template>

<script setup lang="ts">
import { z } from 'zod'

const auth = useAuth()
const router = useRouter()

const loginSchema = z.object({
  email: z.string().email('Valid email required'),
  password: z.string().min(6, 'Password must be at least 6 characters')
})

const form = reactive({
  email: '',
  password: ''
})

const errors = reactive<Record<string, string>>({})
const loading = ref(false)
const error = ref('')

const emit = defineEmits<{
  success: []
}>()

async function handleSubmit() {
  Object.keys(errors).forEach(key => delete errors[key])
  error.value = ''
  
  const result = loginSchema.safeParse(form)
  
  if (!result.success) {
    result.error.errors.forEach(err => {
      if (err.path[0]) {
        errors[err.path[0] as string] = err.message
      }
    })
    return
  }

  loading.value = true
  
  try {
    const response = await authStore.signIn(form.email, form.password)
    
    if (response.success) {
      emit('success')
      router.push('/dashboard')
    } else {
      error.value = response.error || 'Authentication failed'
    }
  } catch (e) {
    error.value = 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}
</script>
