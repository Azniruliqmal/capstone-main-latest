import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('userData')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface LoginData {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface ProjectData {
  id: string
  title: string
  description?: string
  status: string
  created_at: string
  updated_at: string
  budget_total?: number
  estimated_duration_days?: number
  script_filename?: string
}

export interface CreateProjectData {
  title: string
  description?: string
  file: File
}

export const authAPI = {
  async login(data: LoginData) {
    const response = await api.post('/auth/login', data)
    return response.data
  },

  async register(data: RegisterData) {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  async getProfile() {
    const response = await api.get('/auth/profile')
    return response.data
  },

  async logout() {
    try {
      await api.post('/auth/logout')
    } finally {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('userData')
    }
  }
}

export const projectsAPI = {
  async getProjects(): Promise<ProjectData[]> {
    const response = await api.get('/projects/')
    return response.data.projects
  },

  async getProject(projectId: string): Promise<ProjectData> {
    const response = await api.get(`/projects/${projectId}`)
    return response.data
  },

  async createProject(data: CreateProjectData) {
    const formData = new FormData()
    formData.append('title', data.title)
    if (data.description) {
      formData.append('description', data.description)
    }
    formData.append('file', data.file)

    const response = await api.post('/create-project-with-script', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async updateProject(projectId: string, data: Partial<ProjectData>) {
    const response = await api.put(`/projects/${projectId}`, data)
    return response.data
  },

  async deleteProject(projectId: string) {
    const response = await api.delete(`/projects/${projectId}`)
    return response.data
  },

  async getProjectAnalysis(projectId: string) {
    const response = await api.get(`/projects/${projectId}/analysis`)
    return response.data
  },

  async updateProjectAnalysis(projectId: string, analysisData: any) {
    const response = await api.put(`/projects/${projectId}/analysis`, analysisData)
    return response.data
  }
}

export const scriptAPI = {
  async analyzeScript(scriptContent: string) {
    const response = await api.post('/analyze-script', {
      script_content: scriptContent
    })
    return response.data
  },

  async analyzeScriptFile(file: File) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/analyze-script-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }
}

export default api
