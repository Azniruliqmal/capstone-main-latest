<template>
  <div class="transition-all duration-300" :class="sidebarExpanded ? 'ml-64' : 'ml-16'">
    <!-- Header Section -->
    <div
      class="w-full relative bg-background-primary h-20 flex flex-row items-center justify-between py-[15px] pl-[19px] pr-[104px] box-border gap-0 text-left text-2xl text-white font-inter z-30 border-b border-gray-700"
      style="position: sticky; top: 0;"
    >
      <div class="flex items-center gap-6">
        <h1 class="relative leading-[28.8px] font-inter-bold">Budget Management</h1>
        <div class="flex items-center gap-4">
          <select
            v-model="selectedProjectLocal"
            class="bg-background-tertiary text-secondary font-inter-semibold rounded-lg px-4 py-2 focus:outline-none border border-gray-600 focus:border-secondary transition-colors"
          >
            <option
              v-for="project in projects"
              :key="project.title"
              :value="project.title"
              class="bg-background-tertiary text-white"
            >
              {{ project.title }}
            </option>
          </select>
          
          <!-- Confirm Button -->
          <button
            @click="confirmProjectChange"
            :disabled="selectedProjectLocal === selectedProjectTitle"
            :class="[
              'px-4 py-2 rounded-lg font-inter-semibold text-sm transition-colors',
              selectedProjectLocal === selectedProjectTitle
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-secondary text-black hover:bg-secondary-hover cursor-pointer'
            ]"
          >
            Confirm
          </button>
        </div>
      </div>
      <div class="flex flex-row items-center justify-start gap-4 text-sm text-text-secondary">
        <div class="w-[100px] rounded-lg bg-gray-700 h-10 flex flex-row items-center justify-center gap-2 text-text-secondary cursor-pointer hover:bg-gray-600 transition-colors">
          <img class="w-4 h-4" alt="" src="../assets/icon/download.svg" />
          <div class="leading-[16.8px] font-inter-medium">Export</div>
        </div>
        <div class="w-[120px] rounded-lg bg-secondary h-10 flex flex-row items-center justify-center gap-1 cursor-pointer text-black hover:bg-secondary-hover transition-colors" @click="showAI = true">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
          <div class="leading-[16.8px] font-inter-semibold">AI Assistant</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="bg-background-primary h-[calc(100vh-80px)] overflow-y-auto">
      <div class="p-6">
        <div class="max-w-7xl mx-auto flex flex-col gap-6">
          <!-- Budget Summary Cards -->
          <div v-if="false" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="bg-background-secondary rounded-xl p-6 flex flex-col gap-2 border border-gray-700">
              <div class="flex items-center gap-2 text-text-muted text-sm font-inter-regular">
                Total Budget
                <svg class="w-4 h-4 text-secondary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <path d="M12 8v4l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="text-2xl font-inter-bold text-white">{{ summary.totalBudget }}</div>
              <div class="text-text-muted text-xs font-inter-regular">Approved budget</div>
            </div>
            <div class="bg-background-secondary rounded-xl p-6 flex flex-col gap-2 border border-gray-700">
              <div class="flex items-center gap-2 text-text-muted text-sm font-inter-regular">
                Spent
                <svg class="w-4 h-4 text-secondary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="text-2xl font-inter-bold text-white">{{ summary.spent }}</div>
              <div class="text-text-muted text-xs font-inter-regular">{{ summary.spentPercent }}% of budget</div>
            </div>
            <div class="bg-background-secondary rounded-xl p-6 flex flex-col gap-2 border border-gray-700">
              <div class="flex items-center gap-2 text-text-muted text-sm font-inter-regular">
                Remaining
                <svg class="w-4 h-4 text-secondary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <div class="text-2xl font-inter-bold text-white">{{ summary.remaining }}</div>
              <div class="text-text-muted text-xs font-inter-regular">{{ summary.remainingPercent }}% remaining</div>
            </div>
            <div class="bg-background-secondary rounded-xl p-6 flex flex-col gap-2 border border-gray-700">
              <div class="flex items-center gap-2 text-text-muted text-sm font-inter-regular">
                Projected Total
                <svg class="w-4 h-4 text-secondary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <path d="M12 8v4l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="text-2xl font-inter-bold text-white">{{ summary.projectedTotal }}</div>
              <div class="text-text-muted text-xs font-inter-regular">{{ summary.projectedNote }}</div>
            </div>
          </div>

          <!-- Budget Breakdown -->
          <div class="bg-background-secondary rounded-2xl p-8 border border-gray-700">
            <div class="flex items-center justify-between mb-6">
              <div class="text-lg font-inter-bold text-white">Budget Breakdown by Category</div>
              <div class="flex items-center gap-2">
                <button class="bg-background-tertiary rounded-lg px-3 py-2 text-text-muted hover:text-white transition-colors flex items-center gap-1 border border-gray-600">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
                <button class="bg-background-tertiary rounded-lg px-3 py-2 text-text-muted hover:text-white transition-colors flex items-center gap-1 border border-gray-600">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 8v4l2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
            <div v-if="breakdown.length" class="space-y-5">
              <template v-for="cat in breakdown" :key="cat.name">
                <div v-if="cat.name !== 'SFX & VFX' && cat.name !== 'Miscellaneous'" class="mb-5">
                  <div class="flex items-center justify-between mb-2">
                    <div class="font-inter-semibold text-white" :style="{ color: cat.color }">{{ cat.name }}</div>
                    <div class="flex items-center gap-3">
                      <div class="font-inter-semibold text-white" :style="{ color: cat.color }">{{ cat.amount }}</div>
                      <button 
                        @click="editBudgetCategory(cat)"
                        class="bg-background-tertiary hover:bg-gray-600 rounded-lg p-2 transition-colors border border-gray-600 text-text-muted hover:text-white"
                        title="Edit budget amount"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div class="flex items-center gap-4">
                    <div class="flex-1 h-3 rounded-lg bg-background-tertiary relative overflow-hidden">
                      <div
                        class="h-3 rounded-lg absolute left-0 top-0 transition-all duration-300"
                        :style="{ width: cat.percent + '%', background: cat.color }"
                      ></div>
                    </div>
                    <div class="text-text-muted text-xs w-14 font-inter-regular">{{ cat.percent }}%</div>
                  </div>
                </div>
              </template>
            </div>
            <div v-else class="text-center py-12">
              <div class="text-text-muted font-inter-regular mb-4">No budget data available for this project.</div>
              <div class="text-text-muted text-sm font-inter-regular">Budget breakdown will appear here once the project has budget information.</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Assistant Panel -->
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="transform translate-x-full"
      enter-to-class="transform translate-x-0"
      leave-active-class="transition-transform duration-300 ease-in"
      leave-from-class="transform translate-x-0"
      leave-to-class="transform translate-x-full"
    >
      <AIChatPanel v-if="showAI" class="fixed top-0 right-0 z-50" @close="showAI = false" />
    </Transition>

    <!-- Budget Edit Modal -->
    <div v-if="editingCategory" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-background-secondary rounded-xl p-6 w-full max-w-md border border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-inter-bold text-white">Edit Budget Category</h3>
          <button @click="cancelBudgetEdit" class="text-text-muted hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-text-secondary text-sm font-inter-medium mb-2">Category</label>
            <div class="text-white font-inter-semibold" :style="{ color: editingCategory.color }">
              {{ editingCategory.name }}
            </div>
          </div>
          
          <div>
            <label class="block text-text-secondary text-sm font-inter-medium mb-2">Amount (RM)</label>
            <input
              v-model="editAmount"
              type="number"
              min="0"
              step="0.01"
              class="w-full px-4 py-3 rounded-lg bg-background-tertiary text-white border border-gray-600 focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all font-inter-regular"
              placeholder="Enter amount"
            />
          </div>
        </div>
        
        <div class="flex gap-3 mt-6">
          <button
            @click="cancelBudgetEdit"
            class="flex-1 py-3 px-4 rounded-lg bg-background-tertiary text-text-secondary hover:text-white transition-colors border border-gray-600 font-inter-medium"
          >
            Cancel
          </button>
          <button
            @click="saveBudgetEdit"
            class="flex-1 py-3 px-4 rounded-lg bg-secondary text-black hover:bg-secondary-hover transition-colors font-inter-semibold"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, watch, onMounted } from 'vue'
import AIChatPanel from '../components/AIChatPanel.vue'
import { useProjectStore } from '../stores/projectStore'

const sidebarExpanded = inject('sidebarExpanded', ref(false))

const showAI = ref(false)
const projectStore = useProjectStore()
const projects = computed(() => projectStore.projects)
const selectedProjectTitle = ref(projectStore.selectedProjectTitle || projects.value[0]?.title || '')
const selectedProjectLocal = ref(selectedProjectTitle.value)

// Find the selected project object
const selectedProject = computed(() =>
  projects.value.find(p => p.title === selectedProjectTitle.value)
)

// Watch for prop changes to sync local state
watch(() => projectStore.selectedProjectTitle, (newTitle) => {
  selectedProjectTitle.value = newTitle
  selectedProjectLocal.value = newTitle
})

// Handle project change
function onProjectChange() {
  projectStore.setSelectedProject(selectedProjectTitle.value)
}

// Confirm project change
function confirmProjectChange() {
  if (selectedProjectLocal.value !== selectedProjectTitle.value) {
    console.log('Confirming budget project change to:', selectedProjectLocal.value)
    selectedProjectTitle.value = selectedProjectLocal.value
    projectStore.setSelectedProject(selectedProjectLocal.value)
  }
}

// Helper: parse RM value to number
function parseRM(val: string | number | unknown): number {
  if (!val) return 0
  const stringVal = String(val)
  return Number(stringVal.replace(/[^\d.]/g, ''))
}

// Budget editing
const editingCategory = ref<any>(null)
const editAmount = ref('')

function editBudgetCategory(category: any) {
  editingCategory.value = category
  editAmount.value = parseRM(category.amount).toString()
}

async function saveBudgetEdit() {
  if (!editingCategory.value || !selectedProject.value) return
  
  try {
    const newAmount = Number(editAmount.value)
    if (isNaN(newAmount) || newAmount < 0) {
      alert('Please enter a valid amount')
      return
    }
    
    // Update the project budget data
    const project = selectedProject.value
    if (project.scriptBreakdown?.budget) {
      // Find the category key
      const categoryKey = Object.keys(project.scriptBreakdown.budget).find(key =>
        formatCategoryName(key) === editingCategory.value.name
      )
      
      if (categoryKey) {
        project.scriptBreakdown.budget[categoryKey] = `RM ${newAmount}`
        
        // Update analysis data if it exists
        if (project.analysis_data?.script_breakdown?.budget) {
          project.analysis_data.script_breakdown.budget[categoryKey] = `RM ${newAmount}`
        }
        
        // Note: For demo projects, changes are only temporary
        // In a real application, you would save to backend here
      }
    }
    
    editingCategory.value = null
    editAmount.value = ''
  } catch (error) {
    console.error('Failed to save budget edit:', error)
    alert('Failed to save changes. Please try again.')
  }
}

function cancelBudgetEdit() {
  editingCategory.value = null
  editAmount.value = ''
}

// Budget summary logic
const summary = computed(() => {
  const project = selectedProject.value
  if (!project?.scriptBreakdown?.budget) {
    return {
      totalBudget: 'RM 0',
      spent: 'RM 0',
      spentPercent: 0,
      remaining: 'RM 0',
      remainingPercent: 0,
      projectedTotal: 'RM 0',
      projectedNote: 'No data'
    }
  }

  const budgetObj = project.scriptBreakdown.budget
  
  // Sum all categories for total
  const totalBudget = Object.values(budgetObj)
    .map(v => parseRM(v))
    .reduce((a, b) => a + b, 0)
  
  // Calculate spent, remaining, and projected amounts
  const spentPercent = 75 // Demo percentage
  const spent = Math.round(totalBudget * (spentPercent / 100))
  const remaining = totalBudget - spent
  const remainingPercent = Math.round((remaining / totalBudget) * 100)
  const projected = Math.round(totalBudget * 0.97)
  const projectedDiff = totalBudget - projected
  
  return {
    totalBudget: `RM ${totalBudget.toLocaleString()}`,
    spent: `RM ${spent.toLocaleString()}`,
    spentPercent,
    remaining: `RM ${remaining.toLocaleString()}`,
    remainingPercent,
    projectedTotal: `RM ${projected.toLocaleString()}`,
    projectedNote: projectedDiff > 0 ? `${Math.round((projectedDiff / totalBudget) * 100)}% under budget` : 'On track'
  }
})

// Budget breakdown by category with improved colors
const categoryColors: Record<string, string> = {
  talent: '#00C6FB',
  location: '#FFD233', 
  propsSet: '#3DD65B',
  wardrobeMakeup: '#A259FF',
  sfxVfx: '#FF6B6B',
  crew: '#FF9900',
  miscellaneous: '#FFB300'
}

const breakdown = computed(() => {
  const project = selectedProject.value
  if (!project?.scriptBreakdown?.budget) {
    return []
  }

  const budgetObj = project.scriptBreakdown.budget
  const total = Object.values(budgetObj)
    .map(v => parseRM(v))
    .reduce((a, b) => a + b, 0)
  
  if (total === 0) return []

  return Object.entries(budgetObj)
    .map(([key, val]) => {
      const amount = parseRM(val)
      return {
        name: formatCategoryName(key),
        amount: `RM ${amount.toLocaleString()}`,
        percent: +(amount / total * 100).toFixed(1),
        color: categoryColors[key] || '#888888'
      }
    })
    .filter(item => item.percent > 0)
    .sort((a, b) => b.percent - a.percent) // Sort by percentage descending
})

// Helper function to format category names
function formatCategoryName(key: string): string {
  const nameMap: Record<string, string> = {
    talent: 'Talent',
    location: 'Location',
    propsSet: 'Props & Set',
    wardrobeMakeup: 'Wardrobe & Makeup',
    sfxVfx: 'SFX & VFX',
    crew: 'Crew',
    miscellaneous: 'Miscellaneous'
  }
  
  return nameMap[key] || key
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, s => s.toUpperCase())
}

// Watch for project changes
watch(selectedProject, (newProject) => {
  if (newProject) {
    projectStore.setSelectedProject(newProject.title)
  }
}, { immediate: true })

// Load projects when component mounts
onMounted(async () => {
  console.log('BudgetView mounted, loading projects...')
  // Ensure demo projects are loaded if no projects exist
  if (projects.value.length === 0) {
    await projectStore.fetchProjects()
  }
  
  // Set default project if none selected
  if (!selectedProjectTitle.value && projects.value.length > 0) {
    selectedProjectTitle.value = projects.value[0].title
    selectedProjectLocal.value = projects.value[0].title
  }
  
  console.log('BudgetView projects loaded:', projects.value.length)
  console.log('Selected project:', selectedProjectTitle.value)
  console.log('Selected project budget:', selectedProject.value?.scriptBreakdown?.budget)
})
</script>

<style scoped>
div[style*="linear-gradient"] {
  background: linear-gradient(90deg, #00C6FB 0%, #005BEA 100%) !important;
}
</style>
