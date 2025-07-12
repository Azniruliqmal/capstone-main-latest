import { useProjectStore } from '../stores/projectStore'
import { useRouter } from 'vue-router'

export function useAuth() {
  const store = useProjectStore()
  const router = useRouter()

  const login = async (email: string, password: string): Promise<boolean> => {
    const success = await store.login(email, password)
    if (success) {
      router.push({ name: 'ProjectsView' })
    }
    return success
  }

  const register = async (userData: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }): Promise<boolean> => {
    const success = await store.register(userData)
    if (success) {
      router.push({ name: 'ProjectsView' })
    }
    return success
  }

  const logout = () => {
    store.logout()
    router.push({ name: 'Login' })
  }

  return { 
    login, 
    register,
    logout, 
    isLoggedIn: store.isLoggedIn,
    user: store.user,
    error: store.error,
    isLoading: store.isLoading
  }
}