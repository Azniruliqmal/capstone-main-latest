import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '../views/ProjectsView.vue'
import ScriptBreakdown from '../views/ScriptBreakdown.vue'
import BudgetView from '../views/BudgetView.vue'
import LoginView from '../views/LoginView.vue'
import GuestAccessView from '../views/GuestAccessView.vue'
import { useProjectStore } from '../stores/projectStore'

const routes = [
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/guest', name: 'GuestAccess', component: GuestAccessView },
  { 
    path: '/', 
    redirect: (to) => {
      // Check if user is logged in, if not redirect to login
      const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
      return isLoggedIn ? { name: 'ProjectsView' } : { name: 'Login' }
    }
  },
  { 
    path: '/projects', 
    name: 'ProjectsView', 
    component: ProjectsView,
    meta: { requiresAuth: true }
  },
  { 
    path: '/breakdown', 
    name: 'ScriptBreakdown', 
    component: ScriptBreakdown,
    meta: { requiresAuth: true }
  },
  { 
    path: '/budget', 
    name: 'BudgetView', 
    component: BudgetView,
    meta: { requiresAuth: true }
  },
  {
    path: '/new-project',
    name: 'NewProject',
    component: () => import('../views/NewProject.vue'),
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Enhanced navigation guard
router.beforeEach((to, from, next) => {
  // Public routes that don't require authentication
  const publicRoutes = ['Login', 'GuestAccess']
  
  if (publicRoutes.includes(to.name)) {
    // If user is already logged in and tries to access login/guest, redirect to projects
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
    if (isLoggedIn) {
      next({ name: 'ProjectsView' })
    } else {
      next()
    }
    return
  }

  // Check authentication for protected routes
  let isLoggedIn = false
  let store = null
  
  try {
    store = useProjectStore()
    store.initializeFromStorage() // Initialize store from localStorage
    
    // Check if guest access has expired
    if (store.user?.type === 'guest') {
      if (!store.checkGuestAccess()) {
        next({ name: 'Login' })
        return
      }
    }
    
    isLoggedIn = store.isLoggedIn
  } catch {
    // Fallback to localStorage if store is not available
    isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
    
    // Check guest expiry manually if store is not available
    const userData = localStorage.getItem('userData')
    if (userData) {
      const user = JSON.parse(userData)
      if (user.type === 'guest' && user.expiresAt) {
        if (new Date() > new Date(user.expiresAt)) {
          localStorage.removeItem('isLoggedIn')
          localStorage.removeItem('userData')
          localStorage.removeItem('guestAccessStart')
          isLoggedIn = false
        }
      }
    }
  }

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
