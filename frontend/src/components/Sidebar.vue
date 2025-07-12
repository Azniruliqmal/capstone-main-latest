<template>
  <aside
    :class="[
      'bg-background-primary text-white transition-all duration-300 flex flex-col justify-between z-40 fixed top-0 left-0 h-screen border-r border-gray-700',
      expanded ? 'w-64' : 'w-16'
    ]"
    style="z-index: 40;"
  >
    <!-- Top Section -->
    <div>
      <!-- Logo and Toggle Section (only when expanded) -->
      <div v-if="expanded" class="flex items-center justify-between px-4 h-20 border-b border-gray-700">
        <div class="flex items-center gap-3">
          <img src="../assets/image/Logo.png" alt="SceneSplit Logo" class="h-12 w-12 object-contain" />
          <div class="flex flex-col">
            <span class="text-lg font-inter-bold text-white">
              Scene<span class="text-secondary font-inter-regular italic">Split</span>
            </span>
          </div>
        </div>
        <button
          class="p-1 hover:bg-gray-700 rounded transition-colors"
          @click="toggleSidebar"
          :aria-label="'Collapse sidebar'"
        >
          <svg class="w-5 h-5 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <!-- Hamburger menu when collapsed -->
      <div v-if="!expanded" class="flex justify-center items-center h-20 border-b border-gray-700">
        <button
          class="p-2 hover:bg-gray-700 rounded transition-colors"
          @click="toggleSidebar"
          :aria-label="'Expand sidebar'"
        >
          <svg class="w-6 h-6 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      <!-- Navigation Links -->
      <div class="flex flex-col gap-1 px-2 mt-4">
        <RouterLink to="/projects" custom v-slot="{ navigate, isActive }">
          <SidebarLink
            materialIcon="folder"
            label="Projects"
            :expanded="expanded"
            :active="isActive"
            @click="navigate"
            class="w-full max-w-full overflow-hidden"
          />
        </RouterLink>
        <RouterLink to="/breakdown" custom v-slot="{ navigate, isActive }">
          <SidebarLink
            materialIcon="list_alt"
            label="Script Breakdown"
            :expanded="expanded"
            :active="isActive"
            @click="navigate"
            class="w-full max-w-full overflow-hidden"
          />
        </RouterLink>
        <RouterLink to="/budget" custom v-slot="{ navigate, isActive }">
          <SidebarLink
            materialIcon="account_balance_wallet"
            label="Budget"
            :expanded="expanded"
            :active="isActive"
            @click="navigate"
            class="w-full max-w-full overflow-hidden"
          />
        </RouterLink>
      </div>
    </div>
    <!-- Bottom Section -->
    <!-- User Profile Section -->
    <div class="mt-auto px-2 pb-4 w-full border-t border-gray-700 pt-4">
      <UserProfile />
    </div>

  </aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'
import SidebarLink from './SidebarLink.vue'
import UserProfile from './UserProfile.vue'

const expanded = ref(false)
const showPopup = ref(false)
const router = useRouter()
const projectStore = useProjectStore()

const userName = computed(() => projectStore.user?.username || projectStore.user?.full_name || 'User')
const userRole = computed(() => projectStore.user?.is_active ? 'Active User' : 'Inactive User')
const userInitials = computed(() =>
  userName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
)

const emit = defineEmits(['toggle'])
watch(expanded, (val) => emit('toggle', val))

function toggleSidebar() {
  expanded.value = !expanded.value
}

function logout() {
  projectStore.logout()
  showPopup.value = false
  router.push({ name: 'Login' })
}
</script>
