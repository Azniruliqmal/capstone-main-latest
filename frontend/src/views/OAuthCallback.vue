<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <div v-if="loading" class="flex items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-lg text-gray-600">Processing login...</span>
        </div>
        
        <div v-else-if="error" class="text-center">
          <div class="text-red-600 text-lg font-medium mb-4">Login Failed</div>
          <p class="text-gray-600 mb-6">{{ error }}</p>
          <button 
            @click="goToLogin"
            class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
        
        <div v-else class="text-center">
          <div class="text-green-600 text-lg font-medium mb-4">Login Successful!</div>
          <p class="text-gray-600 mb-6">Redirecting to your dashboard...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    // Get access token and user data from URL params (if backend redirects with them)
    // Or handle the OAuth code exchange here
    const urlParams = new URLSearchParams(window.location.search)
    const accessToken = urlParams.get('access_token')
    const userParam = urlParams.get('user')
    
    if (accessToken && userParam) {
      // If backend passes token directly in URL
      const userData = JSON.parse(decodeURIComponent(userParam))
      
      // Store authentication data
      authStore.setAuth(accessToken, userData)
      
      // Redirect to projects page after successful login
      setTimeout(() => {
        router.push({ name: 'ProjectsView' })
      }, 1500)
    } else {
      // Handle OAuth callback with code parameter (standard OAuth flow)
      const code = urlParams.get('code')
      const state = urlParams.get('state')
      const errorParam = urlParams.get('error')
      
      if (errorParam) {
        error.value = `OAuth error: ${errorParam}`
        loading.value = false
        return
      }
      
      if (!code) {
        error.value = 'No authorization code received'
        loading.value = false
        return
      }
      
      // In a real implementation, you would send the code to your backend
      // For now, we'll redirect to login with an error
      error.value = 'OAuth callback handling not fully implemented'
      loading.value = false
    }
  } catch (err) {
    console.error('OAuth callback error:', err)
    error.value = 'Failed to process login callback'
    loading.value = false
  }
})

function goToLogin() {
  router.push({ name: 'Login' })
}
</script>
