<template>
  <div class="min-h-screen bg-background flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-secondary mb-4">
          <Icon name="heroicons:shield-check" class="w-10 h-10 text-primary" />
        </div>
        <h1 class="text-3xl font-bold text-foreground mb-2">SENTINEL</h1>
        <p class="text-muted-foreground text-sm">SHIELD Economic Analysis System</p>
      </div>

      <div class="bg-card border border-border p-8 rounded-lg">
        <h2 class="text-xl font-semibold text-foreground mb-6">Agent Authentication</h2>

        <form @submit="onSubmit" class="space-y-4">
          <FormField name="email" v-slot="{ field }">
            <FormItem>
              <FormLabel class="text-foreground text-sm">Agent Email</FormLabel>
              <FormControl>
                <Input
                  v-bind="field"
                  type="email"
                  placeholder="agent@shield.gov"
                  :disabled="loading"
                  class="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField name="password" v-slot="{ field }">
            <FormItem>
              <FormLabel class="text-foreground text-sm">Password</FormLabel>
              <FormControl>
                <Input
                  v-bind="field"
                  type="password"
                  placeholder="••••••••"
                  :disabled="loading"
                  class="bg-background border-border text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-primary"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <Button
            type="submit"
            class="w-full bg-primary text-primary-foreground hover:bg-primary/90"
            :disabled="loading"
          >
            <Icon v-if="loading" name="svg-spinners:ring-resize" class="w-4 h-4 mr-2" />
            {{ loading ? 'Authenticating...' : 'Access Sentinel' }}
          </Button>
        </form>
      </div>

      <p class="text-center text-muted-foreground text-sm mt-6">
        Classified Access Level Required
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { toast } from "vue-sonner"
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod/v4'

definePageMeta({
  layout: false
})

const router = useRouter()

const loginSchema = toTypedSchema(
  z.object({
    email: z.email('Invalid email address'),
    password: z.string().min(6, 'Password must be at least 6 characters')
  })
)

const form = useForm({
  validationSchema: loginSchema,
  initialValues: {
    email: '',
    password: ''
  }
})

const loading = ref(false)

const session = authClient.useSession()

watch(session, (newSession) => {
  if (newSession) {
    toast('Welcome back, Agent')
    router.push('/dashboard')
  }
})

const onSubmit = form.handleSubmit(handleSubmit)

async function handleSubmit(values: { email: string; password: string }) {
  loading.value = true

  try {
    const { error } = await authClient.signIn.email({
      email: values.email,
      password: values.password
    })

    if (error) {
      toast(error.message || 'Authentication failed')
    }
  } catch (e) {
    toast('An unexpected error occurred')
  } finally {
    loading.value = false
  }
}
</script>
