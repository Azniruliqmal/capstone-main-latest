import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  oauth_provider?: string
  is_verified: boolean
  profile_picture_url?: string
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<User | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  )

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const currentUser = computed(() => user.value)

  // Actions
  function setAuth(token: string, userData: User) {
    accessToken.value = token
    user.value = userData
    
    // Persist to localStorage
    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('isLoggedIn', 'true')
  }

  function logout() {
    accessToken.value = null
    user.value = null
    
    // Clear localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    localStorage.removeItem('isLoggedIn')
  }

  function updateUser(userData: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  // API request helper with auth header
  function getAuthHeaders() {
    return accessToken.value ? {
      'Authorization': `Bearer ${accessToken.value}`,
      'Content-Type': 'application/json'
    } : {
      'Content-Type': 'application/json'
    }
  }

  return {
    // State
    accessToken,
    user,
    
    // Getters
    isAuthenticated,
    currentUser,
    
    // Actions
    setAuth,
    logout,
    updateUser,
    getAuthHeaders
  }
})
