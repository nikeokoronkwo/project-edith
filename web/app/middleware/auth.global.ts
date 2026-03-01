import { authClient } from '@/utils/auth'

export default defineNuxtRouteMiddleware(async (to, from) => {
  const { data: session } = await authClient.useSession(useFetch)
  
  const publicRoutes = ['/login', '/']
  
  if (publicRoutes.includes(to.path)) {
    if (session.value?.session) {
      return navigateTo('/dashboard')
    }
  } else {
    if (!session.value?.session) {
      return navigateTo('/login')
    }
  }
})
