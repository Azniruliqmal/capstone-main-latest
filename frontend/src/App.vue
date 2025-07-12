<template>
  <div class="flex min-h-screen">
    <Sidebar v-if="showSidebar" @toggle="handleSidebarToggle" />
    <main class="flex-1 bg-background-primary text-white min-h-screen font-inter">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, provide, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from './stores/projectStore'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const projectStore = useProjectStore()

const noSidebarRoutes = ['/login', '/guest'] // add more routes if needed

const showSidebar = computed(() => !noSidebarRoutes.includes(route.path))
const sidebarExpanded = ref(false)

provide('sidebarExpanded', sidebarExpanded)

function handleSidebarToggle(expanded: boolean) {
  sidebarExpanded.value = expanded
}

// Watch route changes to update sidebar visibility
watch(() => route.path, () => {
  // You can add any logic here if needed when route changes
})

// Initialize store when app starts
onMounted(async () => {
  await projectStore.fetchProjects()
})
</script>
