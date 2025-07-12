<template>
  <div class="w-1/2 bg-background-secondary flex flex-col h-full">
    <!-- Elements Header - Sticky -->
    <div class="flex-shrink-0 p-6 border-b border-gray-700 bg-background-secondary sticky top-0 z-10">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-white text-lg font-inter-bold mb-1">Elements Breakdown</h2>
          <p class="text-text-muted text-sm font-inter-regular">
            <template v-if="selectedSceneNumber">
              Scene Number: {{ selectedSceneNumber }} {{ selectedScene?.heading }}
            </template>
            <template v-else>
              Select a scene to view elements breakdown.
            </template>
          </p>
        </div>
        <button
          @click="$emit('show-ai')"
          class="bg-secondary text-black px-4 py-2 rounded-lg font-inter-semibold text-sm hover:bg-secondary-hover transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
          AI Assistant
        </button>
      </div>
      
      <!-- Element Tabs -->
      <div class="flex gap-2 mb-4">
        <button
          v-for="tab in elementTabs"
          :key="tab"
          @click="$emit('tab-change', tab)"
          :class="[
            'px-4 py-2 rounded-lg font-inter-semibold text-sm transition-colors',
            activeTab === tab
              ? 'bg-secondary text-black'
              : 'bg-background-tertiary text-white hover:bg-gray-700'
          ]"
        >
          {{ tab }}
        </button>
      </div>
    </div>

    <!-- Elements Content - Scrollable -->
    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="selectedSceneNumber && filteredElements.length">
        <div
          v-for="(element, idx) in filteredElements"
          :key="element.type + element.name + idx"
          class="flex items-start gap-4 mb-6 p-4 bg-background-tertiary rounded-lg border border-gray-700"
        >
          <!-- Element Type Badge -->
          <div class="flex-shrink-0">
            <span
              :class="[
                'text-xs font-inter-bold px-3 py-1 rounded whitespace-nowrap',
                element.type === 'Cast' ? 'bg-secondary text-black' :
                element.type === 'Props' ? 'bg-[#1DE9B6] text-black' :
                'bg-[#A259FF] text-black'
              ]"
            >
              {{ element.type.toUpperCase() }}
            </span>
          </div>
          
          <!-- Element Details -->
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="text-white font-inter-semibold text-sm">{{ element.name }}</h3>
              <span class="text-text-muted text-xs bg-gray-700 rounded-full w-6 h-6 flex items-center justify-center">
                {{ element.count || 1 }}
              </span>
            </div>
            <div v-if="element.description" class="text-text-muted text-sm font-inter-regular">
              {{ element.description }}
            </div>
          </div>
          
          <!-- Element Actions -->
          <div class="flex items-center gap-2">
            <button class="text-text-muted hover:text-secondary transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
            <button class="text-text-muted hover:text-red-400 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
      <div v-else class="text-center mt-20">
        <div class="text-text-muted font-inter-regular">
          Please select a scene to see its elements.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props
const props = defineProps<{
  selectedSceneNumber: number | null
  selectedScene: any
  activeTab: string
  elementTabs: string[]
  filteredElements: any[]
}>()

// Emits
const emit = defineEmits<{
  'tab-change': [tab: string]
  'show-ai': []
}>()
</script>
