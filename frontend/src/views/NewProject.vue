<template>
  <div class="transition-all duration-300" :class="sidebarExpanded ? 'ml-64' : 'ml-16'">
    <!-- Header Section Start -->
    <div
      class="w-full relative bg-background-primary h-20 flex flex-row items-center justify-between py-[15px] pl-[19px] pr-[104px] box-border gap-0 text-left text-2xl text-white font-inter z-30 border-b border-gray-700"
      style="position: sticky; top: 0;"
    >
      <div class="flex flex-col items-start justify-start">
        <h1 class="relative leading-[28.8px] font-inter-bold">New Project</h1>
      </div>
      <div class="flex flex-row items-center justify-start gap-4 text-sm text-text-secondary">
        <div class="w-[120px] rounded-lg bg-secondary h-10 flex flex-row items-center justify-center gap-1 cursor-pointer text-black hover:bg-secondary-hover transition-colors" @click="$router.back()">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          <div class="leading-[16.8px] font-inter-semibold">Back</div>
        </div>
      </div>
    </div>
    <!-- Header Section End -->

    <!-- Main Content -->
    <div class="bg-background-primary px-4 py-8 flex items-center justify-center" style="min-height: calc(100vh - 80px);">
      <div class="max-w-4xl w-full">
        <!-- Upload Section Header -->
        <div class="mb-8 text-center">
          <h2 class="text-white text-xl font-inter-bold mb-2">Upload Your Script</h2>
          <p class="text-text-muted font-inter-regular">Upload your PDF script to start scene analysis with AI</p>
        </div>

        <!-- Upload Card -->
        <div class="flex justify-center mb-8">
          <div
            class="border-2 border-secondary rounded-xl bg-background-secondary flex flex-col items-center justify-center py-12 px-8 w-full max-w-2xl transition hover:border-secondary-hover relative"
            :class="{ 'pointer-events-none opacity-75': isGenerating }"
            @drop="onDrop"
            @dragover.prevent
            @dragenter.prevent
          >
            <!-- Loading Overlay -->
            <div v-if="isGenerating" class="absolute inset-0 bg-background-secondary bg-opacity-90 rounded-xl flex flex-col items-center justify-center z-10">
              <div class="mb-4">
                <!-- Spinning Animation -->
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-secondary"></div>
              </div>
              <h3 class="text-white font-inter-semibold text-lg mb-2">
                Analyzing Script...
              </h3>
              <p class="text-text-muted font-inter-regular text-sm mb-4 text-center">
                {{ currentAnalysisStep }}
              </p>
              <!-- Progress Bar -->
              <div class="w-64 bg-gray-700 rounded-full h-2 mb-2">
                <div 
                  class="bg-secondary h-2 rounded-full transition-all duration-300 ease-out"
                  :style="{ width: analysisProgress + '%' }"
                ></div>
              </div>
              <p class="text-text-muted font-inter-regular text-xs">
                {{ Math.round(analysisProgress) }}% Complete
              </p>
            </div>

            <!-- Normal Upload UI -->
            <div class="flex items-center justify-center mb-4">
              <div class="bg-background-tertiary rounded-full w-16 h-16 flex items-center justify-center border border-gray-600">
                <svg class="w-8 h-8 text-secondary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
            </div>
            <h3 class="text-secondary font-inter-semibold text-lg mb-2 text-center">
              Drop your script here or click to browse
            </h3>
            <p class="text-text-muted font-inter-regular text-sm mb-6 text-center">
              Supports PDF, TXT, FDX, FOUNTAIN formats
            </p>
            <label class="inline-block">
              <input type="file" class="hidden" @change="onFileChange" accept=".pdf,.txt,.fdx,.fountain" />
              <span class="bg-secondary hover:bg-secondary-hover text-black font-inter-semibold px-6 py-2 rounded-lg transition cursor-pointer">
                Choose File
              </span>
            </label>
            <div v-if="selectedFile" class="mt-4 text-white font-inter-medium">
              Selected: {{ selectedFile.name }}
            </div>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="flex justify-end">
          <button
            class="bg-secondary hover:bg-secondary-hover text-black font-inter-semibold px-8 py-3 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            @click="onGenerate"
            :disabled="!selectedFile || isGenerating"
          >
            <svg v-if="isGenerating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-black" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isGenerating ? 'Analyzing...' : 'Generate' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'

// Inject sidebar state from App.vue or provide/inject
const sidebarExpanded = inject('sidebarExpanded', ref(false))

const router = useRouter()
const selectedFile = ref<File | null>(null)
const projectStore = useProjectStore()
const isGenerating = ref(false)
const analysisProgress = ref(0)
const currentAnalysisStep = ref('')

// Analysis steps for progress indication
const analysisSteps = [
  'Uploading script...',
  'Reading document structure...',
  'Identifying scenes and characters...',
  'Analyzing locations and props...',
  'Calculating budget estimates...',
  'Generating timeline...',
  'Finalizing project data...'
]

// Handle file input
function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    console.log('File selected:', selectedFile.value.name)
  }
}

// Handle drag and drop
function onDrop(event: DragEvent) {
  event.preventDefault()
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
    console.log('File dropped:', selectedFile.value.name)
  }
}

// Simulate analysis progress
function simulateProgress() {
  let stepIndex = 0
  const progressInterval = setInterval(() => {
    if (stepIndex < analysisSteps.length) {
      currentAnalysisStep.value = analysisSteps[stepIndex]
      analysisProgress.value = ((stepIndex + 1) / analysisSteps.length) * 100
      stepIndex++
    } else {
      clearInterval(progressInterval)
    }
  }, 1500) // Each step takes 1.5 seconds
}

// Handle Generate button with Zarul's analyzeAndSave function
async function onGenerate() {
  if (!selectedFile.value) {
    alert('Please select a file first.')
    return
  }

  isGenerating.value = true
  analysisProgress.value = 0
  currentAnalysisStep.value = 'Starting analysis...'

  try {
    // Start progress simulation
    simulateProgress()

    // Use the store's analyzeAndSave function
    const result = await projectStore.analyzeAndSave(selectedFile.value)

    // Check if the analysis was successful
    if (result && result.success) {
      // Wait for progress simulation to complete
      await new Promise(resolve => {
        const checkProgress = () => {
          if (analysisProgress.value >= 100) {
            resolve(true)
          } else {
            setTimeout(checkProgress, 100)
          }
        }
        checkProgress()
      })

      // Show success message briefly
      currentAnalysisStep.value = 'Analysis complete! Redirecting...'
      
      // Navigate back to projects after a short delay
      setTimeout(() => {
        router.push({ name: 'ScriptBreakdown' })
      }, 1000)
    } else {
      throw new Error(result?.message || 'Script analysis failed')
    }

  } catch (error: any) {
    console.error('Error analyzing script:', error)
    
    // Show error to user
    currentAnalysisStep.value = `Error: ${error.message || 'Failed to analyze script'}`
    
    // Reset state after showing error
    setTimeout(() => {
      isGenerating.value = false
      analysisProgress.value = 0
      currentAnalysisStep.value = ''
    }, 3000)
  } finally {
    // This will run regardless of success or failure
    // We don't set isGenerating to false here since we handle it in success/error cases
  }
}
</script>
