<template>
  <div class="min-h-screen flex items-center justify-center bg-background-primary relative overflow-hidden">
    <!-- Background Image -->
    <div 
      class="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-30"
      style="background-image: url('/src/assets/image/bg-posters.png')"
    ></div>
    
    <!-- Dark Overlay -->
    <div class="absolute inset-0 bg-black bg-opacity-10"></div>
    
    <div class="bg-background-secondary/50 backdrop-blur-sm rounded-2xl shadow-2xl p-12 w-full max-w-md flex flex-col items-center border border-gray-700/50 relative z-10">
      <!-- Logo -->
      <div class="flex items-center justify-center mb-6">
        <div class="flex flex-col items-center">
          <img 
            src="/src/assets/image/Logo.png" 
            alt="SceneSplit AI Logo" 
            class="h-20 w-auto mb-3"
          />
          <span class="text-2xl font-inter-bold text-white -mb-5">
            Scene<span class="text-secondary font-inter-regular italic">Split</span> AI
          </span>
        </div>
      </div>
      
      <p class="text-text-muted text-sm mb-8 font-inter-regular text-center">Your AI Buddy for Filmmakers</p>

      <!-- Login Form -->
      <form @submit.prevent="onLogin" class="w-full space-y-6">
        <!-- Email Field -->
        <div class="space-y-2">
          <label class="block text-text-secondary text-sm font-inter-medium" for="email">Email</label>
          <input
            v-model="email"
            id="email"
            type="email"
            required
            class="w-full px-4 py-3 rounded-lg bg-background-tertiary text-white border border-gray-600 focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all font-inter-regular placeholder-text-muted"
            placeholder="your@email.com"
          />
        </div>

        <!-- Password Field -->
        <div class="space-y-2">
          <label class="block text-text-secondary text-sm font-inter-medium" for="password">Password</label>
          <input
            v-model="password"
            id="password"
            type="password"
            required
            class="w-full px-4 py-3 rounded-lg bg-background-tertiary text-white border border-gray-600 focus:outline-none focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition-all font-inter-regular placeholder-text-muted"
            placeholder="••••••••"
          />
        </div>

        <!-- Forgot Password -->
        <div class="flex justify-end">
          <a href="#" class="text-text-muted text-sm hover:text-secondary transition-colors font-inter-regular">Forgot password?</a>
        </div>

        <!-- Login Button -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full bg-secondary text-black font-inter-semibold py-3 rounded-lg hover:bg-secondary-hover transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-black" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isLoading ? 'Signing In...' : 'Sign In' }}
        </button>

        <!-- Continue as Guest Button -->
        <button
          type="button"
          class="w-full border border-secondary text-secondary font-inter-semibold py-3 rounded-lg hover:bg-secondary hover:text-black transition-all duration-200"
          @click="goToGuest"
        >
          Continue as Guest
        </button>

        <!-- Divider -->
        <div class="flex items-center my-6">
          <div class="flex-1 h-px bg-gray-700"></div>
          <span class="mx-4 text-text-muted text-sm font-inter-regular">or</span>
          <div class="flex-1 h-px bg-gray-700"></div>
        </div>

        <!-- Social Login -->
        <div class="flex justify-center gap-4">
          <button 
            type="button" 
            class="bg-background-tertiary hover:bg-gray-600 rounded-lg p-3 transition-colors border border-gray-600"
            @click="socialLogin('google')"
          >
            <img 
              src="/src/assets/image/Google Icon.png" 
              alt="Google" 
              class="w-6 h-6"
            />
          </button>
          <button 
            type="button" 
            class="bg-background-tertiary hover:bg-gray-600 rounded-lg p-3 transition-colors border border-gray-600"
            @click="socialLogin('apple')"
          >
            <img 
              src="/src/assets/image/Apple Icon.png" 
              alt="Apple" 
              class="w-6 h-6"
            />
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          <div class="text-red-400 text-sm font-inter-regular text-center">{{ error }}</div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'
import { useAuth } from '../composables/useAuth'

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const router = useRouter()
const projectStore = useProjectStore()
const auth = useAuth()

// Demo users for testing
const demoUsers = [
  {
    email: 'admin@scenesplit.com',
    password: 'password123',
    name: 'Admin User',
    role: 'Administrator'
  },
  {
    email: 'director@scenesplit.com',
    password: 'director123',
    name: 'John Director',
    role: 'Director'
  },
  {
    email: 'producer@scenesplit.com',
    password: 'producer123',
    name: 'Sarah Producer',
    role: 'Producer'
  }
]

async function onLogin() {
  if (!email.value || !password.value) {
    error.value = 'Please enter both email and password'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    // Try real authentication first
    const success = await auth.login(email.value, password.value)
    if (!success) {
      // If real auth fails, try demo login
      await tryDemoLogin()
    }
  } catch (err: any) {
    console.error('Login error:', err)
    // Fallback to demo authentication
    await tryDemoLogin()
  } finally {
    isLoading.value = false
  }
}

async function tryDemoLogin() {
  // Check against demo users as fallback
  const user = demoUsers.find(u => u.email === email.value && u.password === password.value)
  
  if (user) {
    // Use manual login for demo
    projectStore.setLogin(true)
    router.push({ name: 'ProjectsView' })
  } else {
    error.value = 'Invalid credentials. Try demo: admin@scenesplit.com / password123'
  }
}

function goToGuest() {
  router.push({ name: 'GuestAccess' })
}

function socialLogin(provider: string) {
  error.value = `${provider} login is not implemented yet. Use demo credentials: admin@scenesplit.com / password123`
}
</script>