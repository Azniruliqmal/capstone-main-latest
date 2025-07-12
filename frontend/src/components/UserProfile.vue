<template>
  <div>
    <!-- User Profile Button -->
    <button
      @click="openModal"
      class="flex items-center w-full max-w-full overflow-hidden p-2 rounded-lg hover:bg-background-tertiary transition-colors"
      :class="sidebarExpanded ? 'gap-3 justify-start' : 'justify-center px-0'"
      style="min-width:0;"
    >
      <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
        <span class="text-black font-inter-semibold text-sm">{{ userInitials }}</span>
      </div>
      <div v-if="sidebarExpanded" class="flex flex-col text-left overflow-hidden flex-1 min-w-0">
        <span class="text-white font-inter-medium text-sm leading-tight whitespace-nowrap text-ellipsis overflow-hidden">{{ user?.name }}</span>
        <span class="text-text-muted font-inter-regular text-xs whitespace-nowrap text-ellipsis overflow-hidden">{{ user?.role }}</span>
      </div>
      <svg 
        v-if="sidebarExpanded"
        class="w-4 h-4 text-text-muted flex-shrink-0"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <!-- Modal Overlay -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-300"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="isModalOpen"
          class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          @click="closeModal"
        >
          <!-- Modal Content -->
          <Transition
            enter-active-class="transition ease-out duration-300"
            enter-from-class="opacity-0 scale-95 translate-y-4"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition ease-in duration-200"
            leave-from-class="opacity-100 scale-100 translate-y-0"
            leave-to-class="opacity-0 scale-95 translate-y-4"
          >
            <div
              v-if="isModalOpen"
              class="bg-background-secondary rounded-xl shadow-2xl border border-gray-700 w-full max-w-md mx-auto"
              @click.stop
            >
              <!-- Modal Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700">
                <h2 class="text-white font-inter-semibold text-lg">User Profile</h2>
                <button
                  @click="closeModal"
                  class="text-text-muted hover:text-white transition-colors p-1 rounded-lg hover:bg-background-tertiary"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <!-- User Info -->
              <div class="px-6 py-4 border-b border-gray-700">
                <div class="flex items-center space-x-4">
                  <div class="w-16 h-16 bg-secondary rounded-full flex items-center justify-center">
                    <span class="text-black font-inter-bold text-xl">{{ userInitials }}</span>
                  </div>
                  <div class="flex-1">
                    <div class="text-white font-inter-semibold text-lg">{{ user?.name }}</div>
                    <div class="text-text-muted text-sm font-inter-regular">{{ user?.email }}</div>
                    <div class="flex items-center mt-2">
                      <span 
                        :class="[
                          'inline-flex items-center px-3 py-1 rounded-full text-sm font-inter-medium',
                          user?.type === 'guest' 
                            ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' 
                            : 'bg-secondary/20 text-secondary border border-secondary/30'
                        ]"
                      >
                        {{ user?.role }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Guest Access Warning (if applicable) -->
              <div v-if="isGuestUser" class="px-6 py-4 bg-orange-500/10 border-b border-gray-700">
                <div class="flex items-center space-x-3">
                  <svg class="w-6 h-6 text-orange-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <div>
                    <div class="text-orange-400 font-inter-medium">Guest Access</div>
                    <div class="text-orange-300 text-sm font-inter-regular">
                      {{ daysRemaining }} {{ daysRemaining === 1 ? 'day' : 'days' }} remaining
                    </div>
                  </div>
                </div>
              </div>

              <!-- Menu Items -->
              <div class="py-2">
                <!-- Profile (disabled for guests) -->
                <button
                  :disabled="isGuestUser"
                  :class="[
                    'w-full flex items-center px-6 py-3 text-sm font-inter-regular transition-colors text-left',
                    isGuestUser 
                      ? 'text-text-muted cursor-not-allowed' 
                      : 'text-white hover:bg-background-tertiary'
                  ]"
                >
                  <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                  Profile Settings
                </button>

                <!-- Preferences -->
                <button
                  class="w-full flex items-center px-6 py-3 text-sm font-inter-regular text-white hover:bg-background-tertiary transition-colors text-left"
                >
                  <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  Preferences
                </button>

                <!-- Help & Support -->
                <button
                  class="w-full flex items-center px-6 py-3 text-sm font-inter-regular text-white hover:bg-background-tertiary transition-colors text-left"
                >
                  <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Help & Support
                </button>

                <hr class="my-2 border-gray-700">

                <!-- Upgrade (for guests) -->
                <button
                  v-if="isGuestUser"
                  @click="upgradeToFull"
                  class="w-full flex items-center px-6 py-3 text-sm font-inter-regular text-secondary hover:bg-secondary/10 transition-colors text-left"
                >
                  <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                  Upgrade to Full Access
                </button>

                <!-- Sign Out -->
                <button
                  @click="signOut"
                  class="w-full flex items-center px-6 py-3 text-sm font-inter-regular text-red-400 hover:bg-red-500/10 transition-colors text-left"
                >
                  <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  Sign Out
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'

// Inject sidebar expanded state
const sidebarExpanded = inject('sidebarExpanded', ref(true))

const isModalOpen = ref(false)
const router = useRouter()
const projectStore = useProjectStore()

const user = computed(() => projectStore.user)
const isGuestUser = computed(() => projectStore.isGuestUser)
const daysRemaining = computed(() => projectStore.daysUntilGuestExpiry)

const userInitials = computed(() => {
  if (!user.value?.name) return 'U'
  const names = user.value.name.split(' ')
  if (names.length === 1) return names[0].charAt(0).toUpperCase()
  return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase()
})

function openModal() {
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

function signOut() {
  projectStore.logout()
  closeModal()
  router.push({ name: 'Login' })
}

function upgradeToFull() {
  closeModal()
  router.push({ name: 'Login' })
}

// Close modal when pressing Escape key
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && isModalOpen.value) {
    closeModal()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
