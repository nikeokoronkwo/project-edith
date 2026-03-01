<template>
  <header class="h-14 border-b border-slate-700 bg-[#0d2137] flex items-center justify-between px-4">
    <div class="flex items-center gap-4">
      <SidebarTrigger class="text-slate-300 hover:text-white" />
      <div class="h-6 w-px bg-slate-700" />
      <h1 class="text-white font-semibold">{{ title }}</h1>
    </div>
    
    <div class="flex items-center gap-3">
      <button 
        @click="toggleJarvis"
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#1e3a5f] hover:bg-[#2a4a73] transition-colors"
      >
        <Icon name="heroicons:microphone" class="w-4 h-4 text-white" />
        <span class="text-sm text-white">JARVIS</span>
      </button>
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button class="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-[#1e3a5f] transition-colors">
            <div class="w-8 h-8 rounded-full bg-[#1e3a5f] flex items-center justify-center">
              <Icon name="heroicons:user" class="w-4 h-4 text-white" />
            </div>
            <span class="text-sm text-white">{{ userName }}</span>
            <Icon name="heroicons:chevron-down" class="w-4 h-4 text-slate-400" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-48">
          <DropdownMenuLabel class="text-slate-400">Agent Profile</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <Icon name="heroicons:user-circle" class="w-4 h-4 mr-2" />
            <span>Profile</span>
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Icon name="heroicons:cog-6-tooth" class="w-4 h-4 mr-2" />
            <span>Settings</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem @click="handleSignOut" class="text-red-400">
            <Icon name="heroicons:arrow-right-on-rectangle" class="w-4 h-4 mr-2" />
            <span>Sign Out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </header>
</template>

<script setup lang="ts">
import { SidebarTrigger } from '@/components/ui/sidebar'
import { toast } from 'vue-sonner'

defineProps<{
  title?: string
}>()

const emit = defineEmits<{
  toggleJarvis: []
}>()

const router = useRouter()
const session = authClient.useSession()

const userName = computed(() => session.value?.data?.user.name || 'Agent')

function toggleJarvis() {
  emit('toggleJarvis')
}

async function handleSignOut() {
  const { data, error } = await authClient.signOut()
  if (!error && data.success) {
    toast('Signed out successfully')
    router.push('/login')
  }
}
</script>
