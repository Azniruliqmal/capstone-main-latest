<template>
  <div class="w-1/2 bg-background-secondary border-r border-gray-700 flex flex-col h-full">
    <!-- Script Header - Sticky -->
    <div class="flex-shrink-0 p-6 border-b border-gray-700 bg-background-secondary sticky top-0 z-10">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-white text-lg font-inter-bold">Script Analysis</h2>
        </div>
        <div class="flex gap-3">
          <!-- Jump to Scene Dropdown -->
          <div class="relative">
            <select
              v-model="jumpToScene"
              @change="handleJumpToScene"
              class="bg-secondary text-black px-4 py-2 rounded-lg font-inter-semibold text-sm hover:bg-secondary-hover transition-colors appearance-none pr-8 cursor-pointer min-w-[180px]"
            >
              <option value="">Jump to Scene</option>
              <option v-for="scene in scenes" :key="scene.number" :value="scene.number">
                Scene {{ scene.number }} - {{ scene.heading }}
              </option>
            </select>
            <svg class="absolute right-2 top-3 w-3 h-3 text-black pointer-events-none" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
          </div>
          
          <!-- Export Button -->
          <button 
            @click="$emit('export-scenes')"
            class="text-text-secondary hover:text-white transition-colors bg-background-tertiary px-4 py-2 rounded-lg border border-gray-600 hover:border-secondary flex items-center gap-2"
            title="Export scene breakdown"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <span class="text-sm font-inter-medium">Export</span>
          </button>
        </div>
      </div>
      
      <!-- Project Selector -->
      <div class="flex items-center gap-4 mb-5">
        <label class="text-white font-inter-medium text-sm min-w-[45px]">Script:</label>
        <select
          v-model="selectedProjectLocal"
          class="bg-background-tertiary text-secondary font-inter-semibold rounded-lg px-4 py-2 focus:outline-none border border-gray-600 focus:border-secondary transition-colors flex-1"
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
        
        <!-- Status Indicators -->
        <div class="flex gap-3 items-center">
          <span
            v-if="selectedProject"
            :class="['text-xs font-inter-bold px-3 py-1 rounded whitespace-nowrap', getStatusColor(selectedProject.status)]"
          >
            {{ selectedProject.status }}
          </span>
        </div>
      </div>
      <!-- Scene Statistics -->
      <div class="flex items-center text-xs text-text-muted bg-background-tertiary rounded-lg px-4 py-3">
        <div class="flex gap-6">
          <span class="flex items-center gap-2">
            <div class="w-2 h-2 bg-secondary rounded-full"></div>
            <span class="font-inter-medium">{{ filteredScenes.length }} scenes</span>
          </span>
          <span class="flex items-center gap-2" v-if="selectedProject">
            <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
            <span class="font-inter-medium">{{ getTotalCharacters() }} characters</span>
          </span>
          <span class="flex items-center gap-2" v-if="selectedProject">
            <div class="w-2 h-2 bg-green-400 rounded-full"></div>
            <span class="font-inter-medium">{{ getTotalLocations() }} locations</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Scenes List - Scrollable -->
    <div class="flex-1 overflow-y-auto px-6 py-4">
      <div
        v-for="scene in filteredScenes"
        :key="scene.number"
        :class="[
          'mb-4 rounded-lg bg-background-tertiary p-5 cursor-pointer transition-all duration-200 border-2',
          selectedSceneNumber === scene.number
            ? 'border-secondary shadow-lg'
            : 'border-transparent hover:border-gray-600'
        ]"
        @click="$emit('scene-select', scene.number)"
      >
        <!-- Scene Header -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <span class="bg-secondary text-black font-inter-bold rounded-full w-8 h-8 flex items-center justify-center text-sm">
              {{ scene.number }}
            </span>
            <span class="font-inter-bold text-white text-base">{{ scene.heading }}</span>
          </div>
          <button class="text-text-muted hover:text-secondary transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
          </button>
        </div>
        
        <!-- Scene Description -->
        <div class="text-text-muted text-sm mb-3 font-inter-regular">{{ scene.notes }}</div>
        
        <!-- Scene Dialogue -->
        <div v-if="scene.dialogues && scene.dialogues.length" class="mb-3">
          <div v-for="(dialogue, idx) in scene.dialogues.slice(0, 2)" :key="idx" class="mb-2">
            <div class="text-secondary font-inter-semibold text-sm mb-1">{{ dialogue.character }}</div>
            <div class="text-white text-sm font-inter-regular">{{ dialogue.text }}</div>
          </div>
          <div v-if="scene.dialogues.length > 2" class="text-text-muted text-xs font-inter-regular">
            +{{ scene.dialogues.length - 2 }} more dialogues...
          </div>
        </div>
        
        <!-- Scene Elements Summary -->
        <div class="flex flex-wrap gap-4 text-xs">
          <div v-if="scene.characters && scene.characters.length" class="flex items-center gap-1 text-text-muted font-inter-regular">
            <svg class="w-3 h-3 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
            </svg>
            <span class="font-inter-semibold text-white">{{ scene.characters.length }}</span> Cast
          </div>
          <div v-if="scene.props && scene.props.length" class="flex items-center gap-1 text-text-muted font-inter-regular">
            <svg class="w-3 h-3 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
            </svg>
            <span class="font-inter-semibold text-white">{{ scene.props.length }}</span> Props
          </div>
          <div v-if="scene.location" class="flex items-center gap-1 text-text-muted font-inter-regular">
            <svg class="w-3 h-3 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
            </svg>
            <span class="font-inter-semibold text-white text-truncate">{{ scene.location }}</span>
          </div>
        </div>
      </div>
      
      <!-- No Scenes Message -->
      <div v-if="!filteredScenes.length" class="text-center py-12">
        <div class="text-text-muted font-inter-regular mb-4">No scenes found for this project.</div>
        <button
          @click="$emit('new-project')"
          class="bg-secondary text-black px-4 py-2 rounded-lg font-inter-semibold hover:bg-secondary-hover transition-colors"
        >
          Upload New Script
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

// Props
const props = defineProps<{
  projects: any[]
  selectedProjectTitle: string
  selectedProject: any
  scenes: any[]
  filteredScenes: any[]
  selectedSceneNumber: number | null
}>()

// Emits
const emit = defineEmits<{
  'project-change': [value: string]
  'scene-select': [sceneNumber: number]
  'new-project': []
  'export-scenes': []
  'jump-to-scene': [sceneNumber: number]
}>()

// Reactive data
const jumpToScene = ref('')
const selectedProjectLocal = ref(props.selectedProjectTitle)

// Watch for prop changes to sync local state
watch(() => props.selectedProjectTitle, (newTitle) => {
  selectedProjectLocal.value = newTitle
})

// Watch for selected scene changes to update the dropdown
watch(() => props.selectedSceneNumber, (newSceneNumber) => {
  if (newSceneNumber) {
    jumpToScene.value = newSceneNumber.toString()
  } else {
    jumpToScene.value = ''
  }
}, { immediate: true })

// Methods
function confirmProjectChange() {
  if (selectedProjectLocal.value !== props.selectedProjectTitle) {
    console.log('Confirming project change to:', selectedProjectLocal.value)
    emit('project-change', selectedProjectLocal.value)
  }
}

function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    'Active': 'bg-green-500 text-black',
    'Draft': 'bg-yellow-500 text-black', 
    'Completed': 'bg-blue-500 text-white',
    'Archived': 'bg-gray-500 text-white',
    'In Review': 'bg-orange-500 text-black'
  }
  return statusColors[status] || 'bg-gray-500 text-white'
}

function getTotalCharacters(): number {
  const characters = new Set<string>()
  props.scenes.forEach(scene => {
    if (scene.characters) {
      scene.characters.forEach(char => characters.add(char))
    }
  })
  return characters.size
}

function getTotalLocations(): number {
  const locations = new Set<string>()
  props.scenes.forEach(scene => {
    if (scene.location) {
      locations.add(scene.location)
    }
  })
  return locations.size
}

function handleJumpToScene() {
  if (jumpToScene.value) {
    const sceneNumber = parseInt(jumpToScene.value)
    emit('jump-to-scene', sceneNumber)
    // Don't reset the value here - let the watcher handle it
  }
}
</script>
