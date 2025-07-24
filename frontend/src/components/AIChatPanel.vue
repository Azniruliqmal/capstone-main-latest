<template>
  <div class="fixed top-20 right-0 w-[400px] h-[calc(100vh-80px)] bg-background-secondary border-l border-gray-700 flex flex-col z-50 shadow-2xl transform transition-all duration-300 ease-out">
    <!-- Header -->
    <div class="flex-shrink-0 bg-background-tertiary h-[60px] flex flex-row items-center justify-between py-4 px-5 border-b border-gray-700">
      <div class="flex flex-row items-center justify-start gap-3">
        <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </div>
        <div class="flex flex-col items-start justify-start">
          <div class="text-white font-inter-semibold text-sm">SceneSplit Assistant</div>
          <div class="text-text-muted font-inter-regular text-xs">Expert guidance for film production</div>
        </div>
      </div>
      <div class="flex flex-row items-center justify-start gap-2">
        <button 
          @click="minimized = !minimized"
          class="w-8 h-8 rounded-md bg-background-primary hover:bg-gray-600 transition-all duration-200 flex items-center justify-center transform hover:scale-105"
        >
          <svg class="w-4 h-4 text-text-muted transition-transform duration-200" :class="minimized ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
          </svg>
        </button>
        <button 
          @click="$emit('close')"
          class="w-8 h-8 rounded-md bg-background-primary hover:bg-red-600 transition-all duration-200 flex items-center justify-center transform hover:scale-105"
        >
          <svg class="w-4 h-4 text-text-muted hover:text-white transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Chat Messages Area -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 transform scale-95"
      enter-to-class="opacity-100 transform scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 transform scale-100"
      leave-to-class="opacity-0 transform scale-95"
    >
      <div v-if="!minimized" ref="messagesContainer" class="flex-1 overflow-y-auto p-5 space-y-4">
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="flex flex-row items-start justify-start gap-3">
        <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </div>
        <div class="flex-1 rounded-t-xl rounded-br-xl rounded-bl-sm bg-background-tertiary p-3 border border-gray-600">
          <div class="text-white font-inter-medium text-sm mb-2">Hello! I'm your AI filmmaking assistant.</div>
          
          <!-- Show different message based on whether we have a current project -->
          <template v-if="currentScriptId">
            <div class="text-text-muted font-inter-regular text-sm mb-2">
              You're currently working on: <span class="text-secondary font-inter-semibold">{{ projectStore.selectedProjectTitle }}</span>
            </div>
            <div class="text-text-muted font-inter-regular text-sm">
              Send me your feedback about this project's analysis, and I'll help improve the results for you.
            </div>
          </template>
          
          <template v-else>
            <div class="text-text-muted font-inter-regular text-sm mb-2">I can help you with:</div>
            <div class="text-text-muted font-inter-regular text-sm space-y-1">
              <div>• Script analysis and scene breakdowns</div>
              <div>• Budget estimation and cost planning</div>
              <div>• Filmmaking techniques and best practices</div>
              <div>• Equipment and crew recommendations</div>
              <div>• Pre and post-production guidance</div>
              <div>• Creative and technical filmmaking advice</div>
            </div>
          </template>
        </div>
      </div>

      
      <!-- Chat Messages -->
      <TransitionGroup
        name="message"
        tag="div"
        class="space-y-4"
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 transform translate-y-2"
        enter-to-class="opacity-100 transform translate-y-0"
      >
        <div v-for="(message, index) in messages" :key="message.id" class="flex gap-3" :class="message.type === 'user' ? 'justify-start' : 'justify-end'">
        <!-- User Message (Left aligned) -->
        <template v-if="message.type === 'user'">
          <div class="w-8 h-8 bg-background-primary rounded-full flex items-center justify-center flex-shrink-0">
            <div class="text-text-muted font-inter-semibold text-xs">{{ userInitials }}</div>
          </div>
          <div class="flex-1 max-w-[75%] rounded-t-xl rounded-br-xl rounded-bl-sm bg-background-primary p-3 border border-gray-600">
            <div class="text-white font-inter-regular text-sm">{{ message.content }}</div>
          </div>
        </template>

        <!-- AI Message (Right aligned) -->
        <template v-else>
          <div class="flex-1 max-w-[75%] rounded-t-xl rounded-bl-xl rounded-br-sm bg-background-tertiary p-3 border border-gray-600">
            <div class="text-white font-inter-regular text-sm whitespace-pre-wrap leading-relaxed" v-html="formatMessage(message.content)"></div>
            <div v-if="message.actions" class="mt-3 space-y-2">
              <button 
                v-for="action in message.actions" 
                :key="action.label"
                @click="handleAction(action)"
                class="w-full rounded-md bg-secondary h-8 flex items-center justify-center text-xs text-black font-inter-semibold hover:bg-secondary-hover transition-colors"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
          <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
        </template>
        </div>
      </TransitionGroup>

      <!-- Loading Message (Right aligned like AI) -->
      <div v-if="isLoading" class="flex gap-3 justify-end">
        <div class="flex-1 max-w-[75%] rounded-t-xl rounded-bl-xl rounded-br-sm bg-background-tertiary p-3 border border-gray-600">
          <div class="text-text-muted font-inter-regular text-sm">Thinking about your filmmaking question...</div>
        </div>
        <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-black animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      </div>
      </div>
    </Transition>

    <!-- Input Area -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 transform translate-y-2"
      enter-to-class="opacity-100 transform translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 transform translate-y-0"
      leave-to-class="opacity-0 transform translate-y-2"
    >
      <div v-if="!minimized" class="flex-shrink-0 bg-background-tertiary border-t border-gray-700 p-4">
        <div class="flex gap-3">
          <input
            v-model="currentMessage"
            @keypress.enter="sendMessage"
            type="text"
            :placeholder="currentScriptId 
              ? 'Share your feedback about this project analysis...' 
              : 'Ask about filmmaking, budgeting, or script analysis...'"
            class="flex-1 rounded-lg bg-background-primary border border-gray-600 h-10 px-4 text-white placeholder-text-muted focus:outline-none focus:border-secondary transition-colors font-inter-regular text-sm"
          />
          <button 
            @click="sendMessage"
            :disabled="!currentMessage.trim() || isLoading"
            class="w-10 h-10 rounded-lg bg-secondary hover:bg-secondary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { sendChatMessage, uploadScriptFile, type ChatMessage } from '../api/chatApi'
import { useProjectStore } from '../stores/projectStore'

// Define emits
const emit = defineEmits(['close', 'navigate', 'refresh-budget'])

// Store
const projectStore = useProjectStore()

// Reactive state
const minimized = ref(false)
const currentMessage = ref('')
const isLoading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const userInitials = ref('YU') // You can make this dynamic

const messages = ref<ChatMessage[]>([])

// Get current project/script ID for feedback
const currentScriptId = computed(() => {
  // Try to get script ID from selected project
  const selectedProject = projectStore.projects.find(p => p.title === projectStore.selectedProjectTitle)
  
  if (selectedProject?.type === 'api-script' && selectedProject.script_id) {
    return selectedProject.script_id
  }
  
  // Fallback to current script if available
  return projectStore.currentScript?.id || null
})

// Watch for script changes and ensure data is loaded
watch(currentScriptId, async (newScriptId) => {
  if (newScriptId && (!projectStore.currentScript || projectStore.currentScript.id !== newScriptId)) {
    console.log('🔄 Script ID changed, fetching script data:', newScriptId)
    await projectStore.fetchScript(newScriptId)
  }
}, { immediate: true })

// Auto-scroll to bottom when messages change
watch(messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// Auto-scroll when loading state changes
watch(isLoading, async () => {
  await nextTick()
  scrollToBottom()
})

// Auto-scroll function
function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Functions
async function sendMessage() {
  if (!currentMessage.value.trim() || isLoading.value) return

  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    type: 'user',
    content: currentMessage.value,
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const query = currentMessage.value
  currentMessage.value = ''
  isLoading.value = true

  try {
    let response
    
    // If we have a current script ID, use chatWithScript
    if (currentScriptId.value) {
      console.log('🤖 Starting chat with script ID:', currentScriptId.value)
      console.log('🤖 User query:', query)
      
      // Ensure we have the script data loaded
      if (!projectStore.currentScript || projectStore.currentScript.id !== currentScriptId.value) {
        console.log('🔄 Loading script data before chat...')
        await projectStore.fetchScript(currentScriptId.value)
      }
      
      const chatResponse = await projectStore.chatWithScript(currentScriptId.value, query)
      console.log('🤖 Chat response received:', chatResponse)
      
      if (chatResponse) {
        response = {
          response: chatResponse,
          actions: []  // Remove all action buttons
        }
        console.log('🤖 Chat response processed successfully')
      } else {
        // Fallback to feedback if chat fails
        console.log('❌ Chat failed, falling back to feedback for script ID:', currentScriptId.value)
        
        // Check if user wants reanalysis based on keywords
        const requestReanalysis = /\b(reanalyze|re-analyze|analyze again|update analysis|wrong|incorrect|fix|improve)\b/i.test(query)
        
        // Check if feedback seems negative (might want to set approved = false)
        const approved = !/\b(wrong|bad|incorrect|terrible|awful|hate|dislike)\b/i.test(query)
        
        const feedbackResult = await projectStore.provideFeedback(
          currentScriptId.value,
          query,
          approved,
          requestReanalysis
        )
      
      if (feedbackResult && feedbackResult.success) {
        let responseText = `Thank you for your feedback! ${feedbackResult.message}`
        
        if (requestReanalysis) {
          responseText += '\n\n🔄 I detected that you want a reanalysis, so I\'ve requested the system to update the analysis.'
        }
        
        if (!approved) {
          responseText += '\n\n⚠️ I noted some concerns in your feedback and marked this for review.'
        }
        
        responseText += `\n\n**Action taken:** ${feedbackResult.action_taken}\n**Script status:** ${feedbackResult.status}`
        
        if (feedbackResult.feedback_processed) {
          responseText += '\n\n✅ Your feedback has been processed and the analysis may be updated.'
        }
        
        response = {
          response: responseText,
          actions: feedbackResult.feedback_processed ? [
            { label: 'View Updated Analysis', action: 'view-analysis' },
            { label: 'Refresh Budget', action: 'refresh-budget' }
          ] : [
            { label: 'View Current Analysis', action: 'view-analysis' }
          ]
        }
        } else {
          response = {
            response: 'I was unable to process your feedback at this time. Please try again later.',
            actions: []
          }
        }
      }
    } else {
      // Fallback to regular chat API if no script is selected
      response = await sendChatMessage({
        message: query,
        history: messages.value.slice(-10) // Send last 10 messages for context
      })
    }
    
    const aiMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'ai',
      content: response.response || 'Sorry, I encountered an error processing your request.',
      timestamp: new Date(),
      actions: response.actions || []
    }

    messages.value.push(aiMessage)
  } catch (error) {
    console.error('Error sending message:', error)
    
    const errorMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'ai',
      content: 'I\'m sorry, I\'m having trouble connecting to the server right now. Please try again later.',
      timestamp: new Date()
    }

    messages.value.push(errorMessage)
  } finally {
    isLoading.value = false
  }
}

function triggerFileUpload() {
  fileInput.value?.click()
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    await uploadFile(file)
  }
}

async function handleFileDrop(event: DragEvent) {
  event.preventDefault()
  const file = event.dataTransfer?.files[0]
  
  if (file) {
    await uploadFile(file)
  }
}

async function uploadFile(file: File) {
  // Validate file type
  const allowedTypes = ['application/pdf', 'text/plain', 'text/x-fountain']
  const allowedExtensions = ['.pdf', '.txt', '.fountain', '.fdx']
  
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
    const errorMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'ai',
      content: 'Please upload a valid script file (PDF, TXT, or FDX format).',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
    return
  }

  // Add user message about file upload
  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    type: 'user',
    content: `Uploaded script file: ${file.name}`,
    timestamp: new Date()
  }
  messages.value.push(userMessage)

  isLoading.value = true

  try {
    const data = await uploadScriptFile(file)
    
    const aiMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'ai',
      content: `Great! I've analyzed your script "${file.name}". Here's what I found:\n\n` +
               `• **${data.script_breakdown?.scenes?.length || 0} scenes** identified\n` +
               `• **${data.script_breakdown?.characters?.length || 0} characters** found\n` +
               `• **${data.script_breakdown?.locations?.length || 0} locations** detected\n` +
               `• **${data.script_breakdown?.props?.length || 0} props** identified\n\n` +
               `The script analysis is complete! You can now view the detailed breakdown in the main interface.`,
      timestamp: new Date(),
      actions: [
        { label: 'View Full Analysis', action: 'view-analysis' },
        { label: 'Generate Budget', action: 'generate-budget' }
      ]
    }

    messages.value.push(aiMessage)
  } catch (error) {
    console.error('Error uploading file:', error)
    
    const errorMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'ai',
      content: 'I encountered an error while analyzing your script. Please make sure the file is valid and try again.',
      timestamp: new Date()
    }

    messages.value.push(errorMessage)
  } finally {
    isLoading.value = false
  }
}

function handleAction(action: { label: string; action: string }) {
  switch (action.action) {
    case 'view-analysis':
      // Navigate to script analysis view
      console.log('Navigate to script analysis')
      // You could emit an event to parent or use router
      emit('navigate', 'analysis')
      break
    case 'generate-budget':
      // Navigate to budget generation
      console.log('Navigate to budget generation')
      emit('navigate', 'budget')
      break
    case 'refresh-budget':
      // Refresh the current budget view
      console.log('Refreshing budget data')
      emit('refresh-budget')
      break
    default:
      console.log('Unknown action:', action.action)
  }
}

function formatMessage(content: string): string {
  // Simple markdown-like formatting for AI responses
  return content
    // Bold text **text** -> <strong>text</strong>
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-inter-semibold">$1</strong>')
    // Bullet points • text -> styled bullets
    .replace(/^• (.*$)/gm, '<div class="flex items-start gap-2 my-1"><span class="text-secondary text-xs mt-1">•</span><span>$1</span></div>')
    // Line breaks
    .replace(/\n/g, '<br/>')
}

// Lifecycle
onMounted(() => {
  // Optionally load previous chat history or initialize
})
</script>

<style scoped>
/* Add any component-specific styles here */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>