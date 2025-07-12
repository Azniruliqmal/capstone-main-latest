<template>
  <div class="transition-all duration-300" :class="sidebarExpanded ? 'ml-64' : 'ml-16'">
    <!-- Header Section Start -->
    <div
      class="w-full relative bg-background-primary h-20 flex flex-row items-center justify-between py-[15px] pl-[19px] pr-[104px] box-border gap-0 text-left text-2xl text-white font-inter z-30 border-b border-gray-700"
      style="position: sticky; top: 0;"
    >
      <div class="flex flex-col items-start justify-start">
        <h1 class="relative leading-[28.8px] font-inter-bold">Projects</h1>
      </div>
      <div class="flex flex-row items-center justify-start gap-4 text-sm text-text-secondary">
        <div class="w-60 rounded-lg bg-background-tertiary h-10 flex flex-row items-center justify-start py-0 px-4 box-border gap-2 shadow-md transition-all duration-200 focus-within:ring-2 focus-within:ring-secondary hover:shadow-lg border border-gray-600">
          <img class="w-7 h-7 object-cover" alt="" src="../assets/icon/Search Icon.svg" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search projects..."
            class="leading-[26.8px] bg-transparent outline-none text-white placeholder-text-muted w-full rounded-md transition-all duration-200 font-inter-regular"
          />
        </div>
        <div class="w-[120px] rounded-lg bg-gray-200 h-10 hidden flex-row items-center justify-center gap-2 text-secondary">
          <img class="w-4 h-4" alt="" src="../assets/icon/Search Icon.svg" />
          <div class="leading-[16.8px] font-inter-semibold">AI Assistant</div>
        </div>
        <div class="w-[120px] rounded-lg bg-secondary h-10 flex flex-row items-center justify-center gap-1 cursor-pointer text-black hover:bg-secondary-hover transition-colors" @click="goToNewProject">
          <img class="w-4 h-4 object-cover" alt="" src="../assets/icon/Plus Icon.svg" />
          <div class="leading-[16.8px] font-inter-semibold">New Project</div>
        </div>
      </div>
    </div>
    <!-- Header Section End -->

    <!-- Project Filter Tabs -->
    <div class="w-full relative flex flex-row items-center justify-start gap-4 text-left text-sm text-text-secondary font-inter p-4">
      <div
        v-for="tab in ['All Projects', 'Active', 'In Review', 'Completed']"
        :key="tab"
        :class="[
          'rounded-lg h-10 flex flex-row items-center justify-center cursor-pointer px-4 transition-colors whitespace-nowrap',
          tab === 'All Projects' ? 'min-w-[110px]' : tab === 'In Review' ? 'min-w-[90px]' : 'min-w-[80px]',
          activeTab === tab ? 'bg-secondary text-black font-inter-semibold' : 'bg-gray-700 font-inter-medium text-text-secondary hover:bg-gray-600'
        ]"
        @click="setTab(tab)"
      >
        <div class="relative leading-[16.8px]">{{ tab }}</div>
      </div>
    </div>

    <!-- Projects Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 px-4 py-8">
      <!-- Project Card -->
      <div
        v-for="(project, idx) in filteredProjects"
        :key="project.title + idx"
        class="bg-background-secondary rounded-xl p-6 shadow-lg flex flex-col border border-gray-700 hover:border-gray-600 transition-colors"
        style="min-height: 280px;"
      >
        <!-- Card Header -->
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1 pr-4">
            <h2 class="text-xl font-inter-bold text-white">{{ project.title }}</h2>
            <p class="text-text-muted font-inter-regular text-sm mt-1">{{ project.description || 'No description' }}</p>
          </div>
          <span :class="['text-xs font-inter-bold px-3 py-1 rounded whitespace-nowrap', getStatusColor(project.status)]">{{ project.status }}</span>
        </div>
        
        <!-- Spacer to push footer content to bottom -->
        <div class="flex-1"></div>
        
        <!-- Card Footer - Budget, Scripts, Created info -->
        <div class="text-text-muted font-inter-regular text-sm mb-4 space-y-1">
          <div class="flex justify-between items-center">
            <span>Budget:</span> 
            <span class="text-white font-inter-semibold">RM {{ project.budget_total || 'N/A' }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Scenes:</span> 
            <span class="text-white font-inter-semibold">{{ project.scripts_count || 0 }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Created:</span> 
            <span class="text-white font-inter-semibold">{{ formatDate(project.created_at) }}</span>
          </div>
        </div>
        
        <!-- Action Buttons - Always at bottom -->
        <div class="flex items-center gap-3 text-sm">
          <button
            class="flex-1 rounded-md bg-gray-700 h-9 flex items-center justify-center text-sm text-text-secondary cursor-pointer transition hover:bg-gray-600 font-inter-medium disabled:opacity-50 disabled:cursor-not-allowed"
            @click="onViewButtonContainerClick(project)"
            :disabled="loadingProjectId === project.title"
            type="button"
          >
            <div v-if="loadingProjectId === project.title" class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4 text-secondary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="relative leading-[16.8px]">Opening...</span>
            </div>
            <div v-else class="relative leading-[16.8px]">View Details</div>
          </button>
          <!-- Menu Button -->
          <div class="relative">
            <button
              @click="toggleProjectMenu(idx)"
              class="w-9 h-9 rounded-md bg-gray-700 flex items-center justify-center cursor-pointer transition hover:bg-gray-600"
              type="button"
            >
              <svg class="w-5 h-5 text-text-secondary" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
              </svg>
            </button>
            <!-- Dropdown Menu -->
            <div
              v-if="openMenuIndex === idx"
              class="absolute right-0 top-10 mt-1 w-48 bg-background-secondary rounded-lg shadow-xl border border-gray-600 z-50"
            >
              <div class="py-1">
                <button
                  @click="editProject(project, idx)"
                  class="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-700 transition-colors font-inter-medium flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                  Edit Project
                </button>
                <button
                  @click="duplicateProject(project, idx)"
                  class="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-700 transition-colors font-inter-medium flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                  </svg>
                  Duplicate
                </button>
                <button
                  @click="exportProject(project, idx)"
                  class="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-700 transition-colors font-inter-medium flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                  Export
                </button>
                <div class="border-t border-gray-600 my-1"></div>
                <!-- Change Status Submenu -->
                <div class="relative">
                  <button
                    @click="toggleStatusSubmenu(idx)"
                    class="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-700 transition-colors font-inter-medium flex items-center justify-between"
                  >
                    <div class="flex items-center gap-2">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                      Change Status
                    </div>
                    <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-90': openStatusSubmenu === idx }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                  </button>
                  <!-- Status Options -->
                  <div v-if="openStatusSubmenu === idx" class="absolute left-full top-0 ml-1 bg-gray-800 rounded-md shadow-lg border border-gray-600 py-1 min-w-[120px] z-50">
                    <button
                      v-for="statusOption in statusOptions"
                      :key="statusOption.value"
                      @click="changeProjectStatus(project, statusOption)"
                      class="w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-700 transition-colors font-inter-medium flex items-center gap-2"
                      :class="{ 'bg-gray-700': project.status === statusOption.value }"
                    >
                      <div :class="['w-2 h-2 rounded-full', statusOption.dotColor]"></div>
                      {{ statusOption.label }}
                    </button>
                  </div>
                </div>
                <div class="border-t border-gray-600 my-1"></div>
                <button
                  @click="deleteProject(project, idx)"
                  class="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-700 hover:text-red-300 transition-colors font-inter-medium flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Create New Project Card -->
      <div
        class="border-2 border-secondary rounded-xl p-6 shadow-lg flex flex-col items-center justify-center gap-4 bg-background-secondary min-h-[220px] cursor-pointer transition hover:shadow-xl hover:border-secondary-hover"
        @click="goToNewProject"
      >
        <div class="flex items-center justify-center mb-2">
          <div class="bg-background-tertiary rounded-full w-12 h-12 flex items-center justify-center border border-gray-600">
            <span class="text-secondary text-3xl font-inter-bold leading-none">+</span>
          </div>
        </div>
        <h2 class="text-lg font-inter-bold text-white text-center">Create New Project</h2>
        <p class="text-text-muted text-center font-inter-regular text-sm leading-snug">Start a new film project<br />with AI-powered script analysis</p>
      </div>
    </div>

    <!-- Edit Project Modal -->
    <div 
      v-if="showEditModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeEditModal"
    >
      <div 
        class="bg-background-secondary rounded-xl p-6 w-full max-w-md mx-4 border border-gray-600"
        @click.stop
      >
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-inter-bold text-white">Edit Project</h2>
          <button 
            @click="closeEditModal"
            class="text-text-muted hover:text-white transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveProjectEdit" class="space-y-4">
          <!-- Project Title -->
          <div>
            <label class="block text-sm font-inter-medium text-white mb-2">Project Title</label>
            <input
              v-model="editForm.title"
              type="text"
              required
              class="w-full rounded-lg bg-background-tertiary border border-gray-600 px-4 py-3 text-white placeholder-text-muted focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-200 font-inter-regular"
              placeholder="Enter project title..."
            />
          </div>

          <!-- Project Description -->
          <div>
            <label class="block text-sm font-inter-medium text-white mb-2">Description</label>
            <textarea
              v-model="editForm.description"
              rows="3"
              class="w-full rounded-lg bg-background-tertiary border border-gray-600 px-4 py-3 text-white placeholder-text-muted focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-200 font-inter-regular resize-none"
              placeholder="Enter project description..."
            ></textarea>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center gap-3 pt-4">
            <button
              type="button"
              @click="closeEditModal"
              class="flex-1 rounded-lg bg-gray-700 h-10 flex items-center justify-center text-sm text-text-secondary hover:bg-gray-600 transition-colors font-inter-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isUpdating || !editForm.title.trim()"
              class="flex-1 rounded-lg bg-secondary h-10 flex items-center justify-center text-sm text-black hover:bg-secondary-hover transition-colors font-inter-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div v-if="isUpdating" class="flex items-center gap-2">
                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Updating...</span>
              </div>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'

// Inject sidebar state from App.vue or provide/inject
const sidebarExpanded = inject('sidebarExpanded', ref(false))

const projectStore = useProjectStore()

const activeTab = ref('All Projects')
const searchQuery = ref('')
const openMenuIndex = ref(-1)
const openStatusSubmenu = ref(-1)
const loadingProjectId = ref('')

// Edit Project Modal state
const showEditModal = ref(false)
const editingProject = ref<any>(null)
const editForm = ref({
  title: '',
  description: ''
})
const isUpdating = ref(false)

const statusOptions = [
  { value: 'ACTIVE', label: 'Active', color: 'bg-yellow-400 text-black', dotColor: 'bg-yellow-400' },
  { value: 'REVIEW', label: 'In Review', color: 'bg-blue-500 text-white', dotColor: 'bg-blue-500' },
  { value: 'COMPLETED', label: 'Completed', color: 'bg-green-400 text-black', dotColor: 'bg-green-400' }
]

const router = useRouter()

// Load projects when component mounts
onMounted(async () => {
  if (projectStore.isLoggedIn) {
    await projectStore.fetchProjects()
  }
})

// Helper functions
const getStatusColor = (status: string): string => {
  const statusOption = statusOptions.find(opt => opt.value === status.toUpperCase())
  return statusOption ? statusOption.color : 'bg-gray-400 text-white'
}

const formatDate = (dateString: string): string => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  } catch {
    return 'N/A'
  }
}

const filteredProjects = computed(() => {
  let filtered = projectStore.projects
  if (activeTab.value === 'Active') filtered = filtered.filter(p => p.status === 'ACTIVE')
  else if (activeTab.value === 'In Review') filtered = filtered.filter(p => p.status === 'REVIEW')
  else if (activeTab.value === 'Completed') filtered = filtered.filter(p => p.status === 'COMPLETED')
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    filtered = filtered.filter(
      p =>
        (p.title && p.title.toLowerCase().includes(q)) ||
        (p.description && p.description.toLowerCase().includes(q)) ||
        (p.script_filename && p.script_filename.toLowerCase().includes(q))
    )
  }
  
  // Sort projects: newest first, then by status priority (REVIEW > ACTIVE > COMPLETED)
  return filtered.sort((a, b) => {
    // First sort by creation date (newest first)
    const dateA = new Date(a.created_at || '1970-01-01')
    const dateB = new Date(b.created_at || '1970-01-01')
    
    // If dates are different, sort by date (newest first)
    if (dateA.getTime() !== dateB.getTime()) {
      return dateB.getTime() - dateA.getTime()
    }
    
    // If dates are the same, sort by status priority
    const statusPriority = { 'REVIEW': 3, 'ACTIVE': 2, 'COMPLETED': 1 }
    const priorityA = statusPriority[a.status] || 0
    const priorityB = statusPriority[b.status] || 0
    
    return priorityB - priorityA
  })
})

function setTab(tab: string) {
  activeTab.value = tab
}

function toggleProjectMenu(index: number) {
  openMenuIndex.value = openMenuIndex.value === index ? -1 : index
  openStatusSubmenu.value = -1 // Close status submenu when toggling main menu
}

function toggleStatusSubmenu(index: number) {
  openStatusSubmenu.value = openStatusSubmenu.value === index ? -1 : index
}

async function changeProjectStatus(project: any, statusOption: any) {
  try {
    console.log('🔄 Attempting to change project status:', {
      projectId: project.id,
      projectTitle: project.title,
      currentStatus: project.status,
      newStatus: statusOption.value,
      newLabel: statusOption.label
    });
    
    // Update in the store first (this will update the backend and reactive state)
    const success = await projectStore.updateProjectStatus(project.id, statusOption.value, statusOption.color)
    
    console.log('📡 Update result:', success);
    
    if (success) {
      // Close menus
      openMenuIndex.value = -1
      openStatusSubmenu.value = -1
      
      console.log('✅ Project status updated successfully');
      
      // Show success notification
      showNotification(`Project status updated to ${statusOption.label}`, 'success')
    } else {
      console.log('❌ Project status update failed');
      // Show error notification if update failed
      showNotification('Failed to update project status', 'error')
    }
  } catch (error) {
    console.error('❌ Error updating project status:', error)
    showNotification('Failed to update project status', 'error')
  }
}

function onViewButtonContainerClick(project: any) {
  // Set loading state
  loadingProjectId.value = project.id
  
  // Set the selected project in the store
  projectStore.setSelectedProject(project.id)
  
  // Show loading notification
  showNotification(`Loading "${project.title}" analysis...`, 'info')
  
  // Small delay for better UX
  setTimeout(() => {
    // Navigate to Script Analysis page
    router.push({ name: 'ScriptBreakdown' })
    
    console.log('Navigating to Script Analysis for project:', project.title)
    
    // Reset loading state
    loadingProjectId.value = ''
  }, 500)
}

function showNotification(message: string, type: 'success' | 'error' | 'info' = 'success') {
  // Simple notification implementation
  const notification = document.createElement('div')
  notification.className = `fixed top-4 right-4 z-50 px-4 py-3 rounded-lg text-white font-inter-medium transition-all duration-300 ${
    type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'
  }`
  notification.textContent = message
  document.body.appendChild(notification)
  
  setTimeout(() => {
    notification.style.opacity = '0'
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification)
      }
    }, 300)
  }, 2000)
}

function editProject(project: any, index: number) {
  console.log('Opening edit modal for project:', project.title)
  
  // Set the project being edited
  editingProject.value = project
  
  // Pre-fill the form with current values
  editForm.value = {
    title: project.title || '',
    description: project.description || ''
  }
  
  // Show the modal
  showEditModal.value = true
  
  // Close the dropdown menu
  openMenuIndex.value = -1
}

function closeEditModal() {
  showEditModal.value = false
  editingProject.value = null
  editForm.value = {
    title: '',
    description: ''
  }
  isUpdating.value = false
}

async function saveProjectEdit() {
  if (!editingProject.value || !editForm.value.title.trim()) {
    return
  }

  isUpdating.value = true

  try {
    console.log('🔄 Saving project edits:', {
      projectId: editingProject.value.id,
      updates: editForm.value
    })

    // Update the project via the store
    const success = await projectStore.updateProject(editingProject.value.id, {
      title: editForm.value.title.trim(),
      description: editForm.value.description.trim()
    })

    if (success) {
      console.log('✅ Project updated successfully')
      showNotification(`Project "${editForm.value.title}" updated successfully`, 'success')
      closeEditModal()
    } else {
      console.log('❌ Project update failed')
      showNotification('Failed to update project', 'error')
    }
  } catch (error) {
    console.error('❌ Error updating project:', error)
    showNotification('Failed to update project', 'error')
  } finally {
    isUpdating.value = false
  }
}

function duplicateProject(project: any, index: number) {
  console.log('Duplicating project:', project.title)
  openMenuIndex.value = -1
  // Implement duplicate functionality
  const duplicatedProject = {
    ...project,
    title: `${project.title} (Copy)`,
    id: undefined // Remove ID so it gets a new one
  }
  // For now, just add to local array - in a real app you'd call an API
  projectStore.projects.unshift(duplicatedProject)
}

function exportProject(project: any, index: number) {
  console.log('Exporting project:', project.title)
  openMenuIndex.value = -1
  // Implement export functionality
  const dataStr = JSON.stringify(project, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  const exportFileDefaultName = `${project.title.replace(/\s+/g, '_')}_export.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

function deleteProject(project: any, index: number) {
  console.log('Deleting project:', project.title)
  openMenuIndex.value = -1
  // Implement delete functionality with confirmation
  if (confirm(`Are you sure you want to delete "${project.title}"? This action cannot be undone.`)) {
    projectStore.removeProject(project.id)
  }
}

function onNewProjectContainerClick() {
  // Add your code here
}

function goToNewProject() {
  router.push({ name: 'NewProject' })
}

// Close menu when clicking outside
function handleClickOutside(event: Event) {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    openMenuIndex.value = -1
    openStatusSubmenu.value = -1
  }
}

// Handle keyboard events
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && showEditModal.value) {
    closeEditModal()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>