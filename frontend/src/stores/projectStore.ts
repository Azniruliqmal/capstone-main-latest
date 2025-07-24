import { defineStore } from "pinia";
import { ref, computed } from "vue";

// Authentication Types
interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

interface AuthResponse {
  success: boolean;
  user: User;
  access_token: string;
  token_type: string;
}

// Project Types  
interface Project {
  id: string;
  title: string;
  description?: string;
  status: string;
  user_id?: string;
  budget_total?: number;
  estimated_duration_days?: number;
  script_filename?: string;
  created_at: string;
  updated_at: string;
  scripts_count: number;
  analysis_data?: any;
  type?: string; // 'api-script' for uploaded scripts, undefined for demo projects
  script_id?: string; // ID of the associated script in database
  scriptBreakdown?: {
    scenes: any[];
    budget?: Record<string, string>;
    // ...other breakdown fields
  };
}

// Types
interface AnalysisData {
  script_data: any;
  cast_breakdown: any;
  cost_breakdown: any;
  location_breakdown: any;
  props_breakdown: any;
}

interface Script {
  id: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  status: string;
  total_scenes?: number;
  total_characters?: number;
  total_locations?: number;
  estimated_budget?: number;
  budget_category?: string;
  processing_time_seconds?: number;
  api_calls_used?: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

interface AnalysisResult {
  success: boolean;
  message: string;
  data: AnalysisData;
  analysis_data: AnalysisData;
  metadata: {
    filename: string;
    original_filename: string;
    file_size_bytes: number;
    processing_time_seconds: number;
    timestamp: string;
    api_calls_used: number;
  };
  optimization_info: {
    actual_calls_used: number;
    expected_calls: number;
  };
  save_request: {
    filename: string;
    original_filename: string;
    file_size_bytes: number;
    analysis_data: AnalysisData;
    processing_time_seconds: number;
    api_calls_used: number;
  };
}

interface SaveResponse {
  success: boolean;
  message: string;
  database_id: string;
  saved_at: string;
  metadata: any;
}

interface ScriptListResponse {
  success: boolean;
  data: Script[];
  pagination: {
    total: number;
    skip: number;
    limit: number;
    returned: number;
    has_more: boolean;
  };
  search_term?: string;
}

interface FeedbackResponse {
  success: boolean;
  message: string;
  script_id: string;
  feedback_processed: boolean;
  action_taken: string;
  status: string;
}

interface HealthCheck {
  status: string;
  service: string;
  timestamp: string;
  database: string;
  version: string;
}

export const useProjectStore = defineStore('project', () => {
  // Authentication State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(null);
  const isLoggedIn = ref<boolean>(false);
  
  // Project State
  const projects = ref<Project[]>([]);
  const currentProject = ref<Project | null>(null);
  const selectedProjectId = ref<string>('');
  const selectedProjectTitle = ref<string>('');
  
  // Analysis State
  const scripts = ref<Script[]>([]);
  const currentScript = ref<Script | null>(null);
  const currentAnalysis = ref<AnalysisData | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const lastAnalysisResult = ref<AnalysisResult | null>(null);
  const pagination = ref({
    total: 0,
    skip: 0,
    limit: 100,
    returned: 0,
    has_more: false
  });
  const searchTerm = ref<string>('');
  const statusFilter = ref<string>('');

  // Base API URL - adjust based on your environment
  const API_BASE = 'http://localhost:8000';
  
  // Initialize auth state from localStorage
  const initializeAuth = () => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    const loginStatus = localStorage.getItem('isLoggedIn');
    
    if (token && userData && loginStatus === 'true') {
      accessToken.value = token;
      user.value = JSON.parse(userData);
      isLoggedIn.value = true;
    }
  };

  // Initialize selected project state from localStorage
  const initializeSelectedProject = () => {
    const savedProjectId = localStorage.getItem('selectedProjectId');
    const savedProjectTitle = localStorage.getItem('selectedProjectTitle');
    
    if (savedProjectId) {
      selectedProjectId.value = savedProjectId;
      console.log('🔄 Restored selectedProjectId from localStorage:', savedProjectId);
    }
    
    if (savedProjectTitle) {
      selectedProjectTitle.value = savedProjectTitle;
      console.log('🔄 Restored selectedProjectTitle from localStorage:', savedProjectTitle);
    }
  };

  // Computed
  const totalScripts = computed(() => pagination.value.total);
  const completedScripts = computed(() => 
    scripts.value.filter(s => s.status === 'completed').length
  );
  const errorScripts = computed(() => 
    scripts.value.filter(s => s.status === 'error').length
  );
  const pendingScripts = computed(() => 
    scripts.value.filter(s => s.status.includes('pending')).length
  );
  const hasScripts = computed(() => scripts.value.length > 0);
  const isAnalyzing = computed(() => isLoading.value);

  // Helper function for API calls
  const apiCall = async (url: string, options: RequestInit = {}): Promise<any> => {
    try {
      // Add authorization header if user is logged in
      const headers: any = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      };
      
      if (accessToken.value) {
        headers['Authorization'] = `Bearer ${accessToken.value}`;
      }
      
      const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Handle authentication errors
        if (response.status === 401) {
          logout();
          throw new Error('Authentication required. Please log in again.');
        }
        
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (err) {
      if (err instanceof TypeError && err.message.includes('fetch')) {
        throw new Error('Network error: Unable to connect to server');
      }
      throw err;
    }
  };

  // Authentication Actions
  const login = async (email: string, password: string): Promise<boolean> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response: AuthResponse = await apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      
      // Store authentication data
      accessToken.value = response.access_token;
      user.value = response.user;
      isLoggedIn.value = true;
      
      // Persist to localStorage
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
      localStorage.setItem('isLoggedIn', 'true');
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const register = async (userData: RegisterRequest): Promise<boolean> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response: AuthResponse = await apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      });
      
      // Store authentication data
      accessToken.value = response.access_token;
      user.value = response.user;
      isLoggedIn.value = true;
      
      // Persist to localStorage
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
      localStorage.setItem('isLoggedIn', 'true');
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Registration failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const logout = () => {
    // Clear state
    accessToken.value = null;
    user.value = null;
    isLoggedIn.value = false;
    currentProject.value = null;
    projects.value = [];
    scripts.value = [];
    currentScript.value = null;
    currentAnalysis.value = null;
    selectedProjectId.value = '';
    selectedProjectTitle.value = '';
    
    // Clear localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('selectedProjectId');
    localStorage.removeItem('selectedProjectTitle');
  };

  // Demo data initialization
  const loadDemoData = () => {
    console.log('Loading demo data...')
    const demoProjects = [
      {
        id: 'demo-1',
        title: 'Penjaga Akhir Zaman',
        description: 'An epic fantasy adventure film about a mystical guardian protecting an ancient kingdom.',
        status: 'COMPLETED',
        user_id: 'demo-user',
        budget_total: 2500,
        estimated_duration_days: 90,
        script_filename: 'penjaga_akhir_zaman.pdf',
        created_at: new Date('2024-01-15').toISOString(),
        updated_at: new Date('2024-12-20').toISOString(),
        scripts_count: 1,
        // Additional demo fields for frontend compatibility
        genre: 'Fantasy/Adventure',
        dueDate: '2025-03-15',
        team: '8 members',
        statusColor: 'bg-yellow-400 text-black',
        createdAt: new Date('2024-01-15').toISOString(),
        scriptBreakdown: {
          scenes: [
            {
              number: 1,
              heading: 'EXT. HUTAN RIMBA - DAY',
              location: 'HULU LANGAT RETREAT',
              time: 'DAY',
              characters: ['LYRA', 'GUARDIAN SPIRIT'],
              props: ['Ancient sword', 'Mystical crystal', 'Ancient tome'],
              wardrobe: ['Warrior armor', 'Mystical robes'],
              sfx: ['Wind sounds', 'Mystical energy'],
              notes: 'Opening scene where Lyra discovers the ancient guardian spirit in the sacred forest.',
              budget: 'High',
              dialogues: [
                'LYRA: I can feel the ancient power calling to me.',
                'GUARDIAN SPIRIT: You have been chosen, young warrior.',
                'LYRA: But I am not ready for this responsibility.',
                'GUARDIAN SPIRIT: Readiness comes through trials, not through waiting.'
              ],
              estimatedDuration: '3-4 minutes'
            },
            {
              number: 2,
              heading: 'INT. LYRA\'S COTTAGE - NIGHT',
              location: 'Cottage',
              time: 'NIGHT',
              characters: ['LYRA', 'ELDER WOMAN'],
              props: ['Fireplace', 'Old books', 'Healing herbs'],
              wardrobe: ['Simple dress', 'Elder robes'],
              sfx: ['Fire crackling', 'Night sounds'],
              notes: 'Lyra returns home to seek wisdom from the village elder.',
              budget: 'Medium',
              dialogues: [
                'ELDER WOMAN: The spirits have spoken to you, haven\'t they?',
                'LYRA: How did you know?',
                'ELDER WOMAN: I have seen the signs. The kingdom needs its guardian.',
                'LYRA: I don\'t know if I can fulfill this destiny.'
              ],
              estimatedDuration: '2-3 minutes'
            },
            {
              number: 3,
              heading: 'EXT. TAMAN BOTANI - DAY',
              location: 'TAMAN BOTANI SHAH ALAM',
              time: 'DAY',
              characters: ['LYRA', 'CAPTAIN DRAKE', 'SOLDIERS'],
              props: ['Siege weapons', 'Banners', 'Weapons'],
              wardrobe: ['Battle armor', 'Military uniforms'],
              sfx: ['Battle sounds', 'War drums'],
              notes: 'The kingdom is under attack and Lyra must make her choice.',
              budget: 'High',
              dialogues: [
                'CAPTAIN DRAKE: The enemy approaches! We need the guardian now!',
                'LYRA: I am here. I will protect our people.',
                'CAPTAIN DRAKE: Are you certain you\'re ready?',
                'LYRA: I have to be.'
              ],
              estimatedDuration: '5-6 minutes'
            },
            {
              number: 4,
              heading: 'EXT. GUA TEMPURUNG - DAY',
              location: 'Gua Tempurung',
              time: 'DAY',
              characters: ['LYRA', 'GUARDIAN SPIRIT'],
              props: ['Ancient sword', 'Mystical crystal', 'Ancient tome'],
              wardrobe: ['Warrior armor', 'Mystical robes'],
              sfx: ['Wind sounds', 'Mystical energy'],
              notes: 'Opening scene where Lyra discovers the ancient guardian spirit in the sacred forest.',
              budget: 'High',
              dialogues: [
                'LYRA: I can feel the ancient power calling to me.',
                'GUARDIAN SPIRIT: You have been chosen, young warrior.',
                'LYRA: But I am not ready for this responsibility.',
                'GUARDIAN SPIRIT: Readiness comes through trials, not through waiting.'
              ],
              estimatedDuration: '3-4 minutes'
            },
            {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 5,
              heading: 'INT. LYRA\'S HOUSE - NIGHT',
              location: 'Cottage',
              time: 'NIGHT',
              characters: ['LYRA', 'ELDER WOMAN'],
              props: ['Fireplace', 'Old books', 'Healing herbs'],
              wardrobe: ['Simple dress', 'Elder robes'],
              sfx: ['Fire crackling', 'Night sounds'],
              notes: 'Lyra returns home to seek wisdom from the village elder.',
              budget: 'Medium',
              dialogues: [
                'ELDER WOMAN: The spirits have spoken to you, haven\'t they?',
                'LYRA: How did you know?',
                'ELDER WOMAN: I have seen the signs. The kingdom needs its guardian.',
                'LYRA: I don\'t know if I can fulfill this destiny.'
              ],
              estimatedDuration: '2-3 minutes'
            },
          ],
          budget: {
            talent: 'RM 4500',
            location: 'RM 38000',
            propsSet: 'RM 3200',
            wardrobeMakeup: 'RM 28000',
            sfxVfx: 'RM 650',
            crew: 'RM 350',
            miscellaneous: 'RM 700'
          }
        }
      },
      {
        id: 'demo-2',
        title: 'Polis Evolution 707',
        description: 'A gritty crime thriller set in the underground world of a major metropolitan city.',
        status: 'COMPLETED',
        user_id: 'demo-user',
        budget_total: 2000,
        estimated_duration_days: 75,
        script_filename: 'polis_evolution_707.pdf',
        created_at: new Date('2024-02-10').toISOString(),
        updated_at: new Date('2024-11-30').toISOString(),
        scripts_count: 2,
        // Additional demo fields
        genre: 'Crime/Thriller',
        dueDate: '2024-12-01',
        team: '12 members',
        statusColor: 'bg-green-400 text-black',
        createdAt: new Date('2024-02-10').toISOString(),
        scriptBreakdown: {
          scenes: [
            {
              number: 1,
              heading: 'EXT. CITY STREET - NIGHT',
              location: 'City Street',
              time: 'NIGHT',
              characters: ['DETECTIVE SARAH', 'INFORMANT'],
              props: ['Police badge', 'Cigarettes', 'Cell phone'],
              wardrobe: ['Detective coat', 'Street clothes'],
              sfx: ['City noise', 'Rain'],
              notes: 'Detective Sarah meets with an informant about the underground crime ring.',
              budget: 'Medium',
              dialogues: [
                'INFORMANT: You didn\'t hear this from me, Detective.',
                'DETECTIVE SARAH: I understand. What do you have?',
                'INFORMANT: The shipment comes in tomorrow night at pier 47.',
                'DETECTIVE SARAH: Are you certain about this?'
              ],
              estimatedDuration: '2-3 minutes'
            },
                        {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 1,
            },
            {
              number: 2,
              heading: 'INT. POLICE STATION - DAY',
              location: 'Police Station',
              time: 'DAY',
              characters: ['DETECTIVE SARAH', 'CAPTAIN JONES', 'OFFICER MIKE'],
              props: ['Evidence board', 'Files', 'Coffee cups'],
              wardrobe: ['Police uniforms', 'Detective clothes'],
              sfx: ['Office ambiance', 'Phone rings'],
              notes: 'Sarah briefs her team about the upcoming raid.',
              budget: 'Low',
              dialogues: [
                'CAPTAIN JONES: This could be the break we\'ve been waiting for.',
                'DETECTIVE SARAH: We need to be careful. These people are dangerous.',
                'OFFICER MIKE: What\'s the plan, Detective?',
                'DETECTIVE SARAH: We go in quiet and fast.'
              ],
              estimatedDuration: '3-4 minutes'
            }
          ],
          budget: {
            talent: 'RM 320000',
            location: 'RM 240000',
            propsSet: 'RM 180000',
            wardrobeMakeup: 'RM 150000',
            sfxVfx: 'RM 420000',
            crew: 'RM 380000',
            miscellaneous: 'RM 110000'
          }
        }
      },
      /*{
        id: 'demo-3',
        title: 'Tentang Matahari',
        description: 'A romantic drama about two musicians who find love through their shared passion for music.',
        status: 'COMPLETED',
        user_id: 'demo-user',
        budget_total: 950000,
        estimated_duration_days: 60,
        script_filename: 'tentang_matahari.pdf',
        created_at: new Date('2024-03-05').toISOString(),
        updated_at: new Date('2024-12-18').toISOString(),
        scripts_count: 1,
        // Additional demo fields
        genre: 'Romance/Drama',
        dueDate: '2025-02-28',
        team: '6 members',
        statusColor: 'bg-yellow-400 text-black',
        createdAt: new Date('2024-03-05').toISOString(),
        scriptBreakdown: {
          scenes: [
            {
              number: 1,
              heading: 'INT. JAZZ CLUB - NIGHT',
              location: 'Jazz Club',
              time: 'NIGHT',
              characters: ['MAYA', 'AUDIENCE'],
              props: ['Piano', 'Microphone', 'Stage lights'],
              wardrobe: ['Evening dress', 'Audience attire'],
              sfx: ['Jazz music', 'Applause'],
              notes: 'Maya performs a soulful jazz number at the intimate club.',
              budget: 'Medium',
              dialogues: [
                'MAYA: (singing) In the moonlight, I find my way...',
                'AUDIENCE MEMBER: Beautiful performance!',
                'MAYA: Thank you so much.'
              ],
              estimatedDuration: '4-5 minutes'
            },
            {
              number: 2,
              heading: 'EXT. CITY PARK - DAY',
              location: 'City Park',
              time: 'DAY',
              characters: ['MAYA', 'DAVID'],
              props: ['Guitar', 'Park bench', 'Sheet music'],
              wardrobe: ['Casual clothes', 'Musician attire'],
              sfx: ['Birds chirping', 'Guitar music'],
              notes: 'Maya meets David, a street musician, and they connect through music.',
              budget: 'Low',
              dialogues: [
                'DAVID: I heard you at the club last night. You have an amazing voice.',
                'MAYA: Thank you. Your guitar playing is beautiful too.',
                'DAVID: Would you like to play something together?',
                'MAYA: I\'d love to.'
              ],
              estimatedDuration: '3-4 minutes'
            }
          ],
          budget: {
            talent: 'RM 180000',
            location: 'RM 120000',
            propsSet: 'RM 95000',
            wardrobeMakeup: 'RM 85000',
            sfxVfx: 'RM 220000',
            crew: 'RM 180000',
            miscellaneous: 'RM 70000'
          }
        }
      },
      {
        id: 'demo-4',
        title: 'Space Horizon',
        description: 'A sci-fi epic about humanity\'s first mission to establish colonies beyond our solar system.',
        status: 'ACTIVE',
        user_id: 'demo-user',
        budget_total: 4200000,
        estimated_duration_days: 120,
        script_filename: 'space_horizon.pdf',
        created_at: new Date('2024-04-12').toISOString(),
        updated_at: new Date('2024-12-22').toISOString(),
        scripts_count: 3,
        // Additional demo fields
        genre: 'Sci-Fi/Adventure',
        dueDate: '2025-05-15',
        team: '15 members',
        statusColor: 'bg-gray-400 text-white',
        createdAt: new Date('2024-04-12').toISOString(),
        scriptBreakdown: {
          scenes: [
            {
              number: 1,
              heading: 'INT. SPACECRAFT BRIDGE - DAY',
              location: 'Spacecraft Bridge',
              time: 'DAY',
              characters: ['CAPTAIN NOVA', 'ENGINEER ZARA', 'PILOT ACE'],
              props: ['Control panels', 'Holographic displays', 'Communication devices'],
              wardrobe: ['Space uniforms', 'Technical gear'],
              sfx: ['Ship systems', 'Space ambiance'],
              notes: 'The crew prepares for the historic jump to the new solar system.',
              budget: 'Very High',
              dialogues: [
                'CAPTAIN NOVA: This is it, crew. Humanity\'s next great leap.',
                'ENGINEER ZARA: All systems are green, Captain.',
                'PILOT ACE: Course laid in for the Kepler system.',
                'CAPTAIN NOVA: Engage the quantum drive.'
              ],
              estimatedDuration: '4-5 minutes'
            },
            {
              number: 2,
              heading: 'EXT. ALIEN PLANET SURFACE - DAY',
              location: 'Alien Planet',
              time: 'DAY',
              characters: ['CAPTAIN NOVA', 'SCIENCE OFFICER KAI', 'SECURITY TEAM'],
              props: ['Scanning equipment', 'Weapons', 'Environmental suits'],
              wardrobe: ['Space suits', 'Military gear'],
              sfx: ['Alien atmosphere', 'Equipment beeps'],
              notes: 'The team explores the new planet and discovers signs of life.',
              budget: 'Very High',
              dialogues: [
                'SCIENCE OFFICER KAI: Captain, I\'m reading organic compounds here.',
                'CAPTAIN NOVA: Any signs of intelligent life?',
                'SCIENCE OFFICER KAI: Still analyzing, but the possibilities are extraordinary.',
                'CAPTAIN NOVA: Proceed with caution.'
              ],
              estimatedDuration: '6-7 minutes'
            }
          ],
          budget: {
            talent: 'RM 850000',
            location: 'RM 950000',
            propsSet: 'RM 780000',
            wardrobeMakeup: 'RM 420000',
            sfxVfx: 'RM 1200000',
            crew: 'RM 650000',
            miscellaneous: 'RM 350000'
          }
        } 
      }*/
    ];
    
    projects.value = demoProjects as Project[];
    
    // Only set initial selected project if none is already persisted
    if (demoProjects.length > 0 && !selectedProjectId.value) {
      selectedProjectId.value = demoProjects[0].id;
      selectedProjectTitle.value = demoProjects[0].title;
      currentProject.value = demoProjects[0] as Project;
      console.log('Setting default project since none was persisted:', demoProjects[0].title);
    } else if (selectedProjectId.value) {
      console.log('Keeping persisted project selection:', selectedProjectId.value);
    }
    
    console.log('Demo data loaded:', projects.value.length, 'projects')
    console.log('First project:', projects.value[0]?.title)
    console.log('Selected project ID:', selectedProjectId.value)
    
    // After loading projects, try to resolve any persisted project ID that wasn't found before
    if (selectedProjectId.value) {
      const project = projects.value.find(p => p.id === selectedProjectId.value);
      if (project && !selectedProjectTitle.value) {
        selectedProjectTitle.value = project.title;
        currentProject.value = project;
        localStorage.setItem('selectedProjectTitle', project.title);
        console.log('✅ Resolved persisted project ID after demo data load:', project.title);
      }
    }
  };

  // Enhanced authentication that loads demo data
  const setLogin = (status: boolean) => {
    isLoggedIn.value = status;
    localStorage.setItem('isLoggedIn', status.toString());
    
    // Load demo data when logging in
    if (status && projects.value.length === 0) {
      loadDemoData();
    }
  };

  // Actions
  const checkHealth = async (): Promise<HealthCheck | null> => {
    try {
      return await apiCall('/health');
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Health check failed';
      return null;
    }
  };

  const analyzeScript = async (file: File): Promise<AnalysisResult | null> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/analyze-script`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Analysis failed: ${response.statusText}`);
      }

      const result: AnalysisResult = await response.json();
      lastAnalysisResult.value = result;
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Analysis failed';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const saveAnalysis = async (analysisResult: AnalysisResult): Promise<SaveResponse | null> => {
    isLoading.value = true;
    error.value = null;

    try {
      const result: SaveResponse = await apiCall('/save-analysis', {
        method: 'POST',
        body: JSON.stringify(analysisResult.save_request),
      });
      
      // Refresh scripts list after saving
      await fetchScripts();
      
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Save failed';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchScripts = async (
    page = 0, 
    limit = 100, 
    orderBy = 'created_at',
    orderDirection = 'desc'
  ): Promise<void> => {
    isLoading.value = true;
    error.value = null;

    try {
      const params = new URLSearchParams({
        skip: (page * limit).toString(),
        limit: limit.toString(),
        order_by: orderBy,
        order_direction: orderDirection,
      });

      if (statusFilter.value) {
        params.append('status_filter', statusFilter.value);
      }

      if (searchTerm.value) {
        params.append('search', searchTerm.value);
      }

      const result: ScriptListResponse = await apiCall(`/analyzed-scripts?${params}`);
      
      scripts.value = result.data;
      pagination.value = result.pagination;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Fetch failed';
    } finally {
      isLoading.value = false;
    }
  };

  const fetchScript = async (scriptId: string): Promise<void> => {
    isLoading.value = true;
    error.value = null;

    try {
      const result = await apiCall(`/analyzed-scripts/${scriptId}`);
      
      currentScript.value = result.data;
      currentAnalysis.value = {
        script_data: result.data.script_data,
        cast_breakdown: result.data.cast_breakdown,
        cost_breakdown: result.data.cost_breakdown,
        location_breakdown: result.data.location_breakdown,
        props_breakdown: result.data.props_breakdown,
      };
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Fetch script failed';
    } finally {
      isLoading.value = false;
    }
  };

  const deleteScript = async (scriptId: string): Promise<boolean> => {
    isLoading.value = true;
    error.value = null;

    try {
      await apiCall(`/analyzed-scripts/${scriptId}`, {
        method: 'DELETE',
      });

      // Remove from local state
      scripts.value = scripts.value.filter(s => s.id !== scriptId);
      pagination.value.total = Math.max(0, pagination.value.total - 1);
      
      if (currentScript.value?.id === scriptId) {
        currentScript.value = null;
        currentAnalysis.value = null;
      }

      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Delete failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const searchScripts = async (searchQuery: string): Promise<void> => {
    searchTerm.value = searchQuery;
    await fetchScripts();
  };

  const filterByStatus = async (status: string): Promise<void> => {
    statusFilter.value = status;
    await fetchScripts();
  };

  const provideFeedback = async (
    scriptId: string, 
    feedbackText: string, 
    approved: boolean = true,
    requestReanalysis: boolean = false
  ): Promise<FeedbackResponse | null> => {
    isLoading.value = true;
    error.value = null;

    try {
      const result: FeedbackResponse = await apiCall(`/provide-feedback/${scriptId}`, {
        method: 'POST',
        body: JSON.stringify({
          feedback_text: feedbackText,
          approved,
          request_reanalysis: requestReanalysis,
        }),
      });

      // Refresh the script data
      await fetchScript(scriptId);
      
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Feedback failed';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const getScriptsAwaitingFeedback = async (page = 0, limit = 100): Promise<void> => {
    isLoading.value = true;
    error.value = null;

    try {
      const params = new URLSearchParams({
        skip: (page * limit).toString(),
        limit: limit.toString(),
      });

      const result: ScriptListResponse = await apiCall(`/scripts-awaiting-feedback?${params}`);
      
      scripts.value = result.data;
      pagination.value = result.pagination;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Fetch failed';
    } finally {
      isLoading.value = false;
    }
  };

  const createProjectWithScript = async (
    title: string,
    description: string,
    file: File
  ): Promise<any> => {
    isLoading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append('title', title);
      if (description) {
        formData.append('description', description);
      }
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/create-project-with-script`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Project creation failed');
      }

      const result = await response.json();
      
      // Add the new project to the projects list
      if (result.success && result.project) {
        const newProject = result.project;
        projects.value.unshift(newProject);
        
        // Set as selected project
        setSelectedProject(newProject.id);
        
        // If there's script analysis data, store it
        if (result.analysis_data) {
          currentAnalysis.value = result.analysis_data;
        }
      }
      
      return result;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Project creation failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // Project Management Actions
  const createProject = async (projectData: {
    title: string;
    description?: string;
    estimated_duration_days?: number;
  }): Promise<Project | null> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const project: Project = await apiCall('/projects', {
        method: 'POST',
        body: JSON.stringify(projectData),
      });
      
      projects.value.unshift(project);
      return project;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Project creation failed';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchProjects = async (): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // Always load demo data first to ensure we have the demo projects
      loadDemoData();
      
      // Then try to fetch from API and merge if needed
      const result = await apiCall('/projects/');
      if (result && result.data && result.data.length > 0) {
        // Combine demo projects with API projects, ensuring demo projects come first
        const demoProjects = projects.value; // Demo data was just loaded
        const apiProjects = result.data.filter((apiProject: any) => 
          !demoProjects.some(demoProject => demoProject.title === apiProject.title)
        );
        projects.value = [...demoProjects, ...apiProjects];
        console.log('Combined demo and API projects:', projects.value.length);
      } else {
        console.log('No additional projects from API, using demo data only');
      }
      
      // After loading all projects, try to resolve any persisted project ID
      if (selectedProjectId.value) {
        const project = projects.value.find(p => p.id === selectedProjectId.value);
        if (project && !selectedProjectTitle.value) {
          selectedProjectTitle.value = project.title;
          currentProject.value = project;
          localStorage.setItem('selectedProjectTitle', project.title);
          console.log('✅ Resolved persisted project ID after fetchProjects:', project.title);
        }
      }
    } catch (err) {
      // If API fails, we already have demo data loaded
      console.log('API not available, using demo data only');
      error.value = null; // Clear error since we have demo data
    } finally {
      isLoading.value = false;
    }
  };

  const updateProject = async (projectId: string, updates: Partial<Project>): Promise<boolean> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      console.log('🔄 Store: Updating project', { projectId, updates });
      
      const response = await apiCall(`/projects/${projectId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      });
      
      console.log('📡 Store: API response', response);
      
      // Handle the response structure from backend
      const updatedProject = response.project || response;
      
      const index = projects.value.findIndex(p => p.id === projectId);
      if (index !== -1) {
        projects.value[index] = updatedProject;
        console.log('✅ Store: Project updated in array at index', index);
      }
      
      if (currentProject.value?.id === projectId) {
        currentProject.value = updatedProject;
        console.log('✅ Store: Current project updated');
      }
      
      return true;
    } catch (err) {
      console.error('❌ Store: Project update failed', err);
      error.value = err instanceof Error ? err.message : 'Project update failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteProject = async (projectId: string): Promise<boolean> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      await apiCall(`/projects/${projectId}`, {
        method: 'DELETE',
      });
      
      projects.value = projects.value.filter(p => p.id !== projectId);
      
      if (currentProject.value?.id === projectId) {
        currentProject.value = null;
      }
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Project deletion failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const setCurrentProject = (project: Project | null) => {
    currentProject.value = project;
    if (project) {
      localStorage.setItem('current_project', JSON.stringify(project));
    } else {
      localStorage.removeItem('current_project');
    }
  };

  // Initialize current project from localStorage
  const initializeCurrentProject = () => {
    const projectData = localStorage.getItem('current_project');
    if (projectData) {
      try {
        currentProject.value = JSON.parse(projectData);
      } catch (e) {
        localStorage.removeItem('current_project');
      }
    }
  };

  // Call on store creation
  initializeCurrentProject();

  // Utility actions
  const clearError = () => {
    error.value = null;
  };

  const clearCurrentScript = () => {
    currentScript.value = null;
    currentAnalysis.value = null;
  };

  const clearSearch = () => {
    searchTerm.value = '';
    statusFilter.value = '';
  };

  const resetPagination = () => {
    pagination.value = {
      total: 0,
      skip: 0,
      limit: 100,
      returned: 0,
      has_more: false
    };
  };

  // Combined actions
  const analyzeAndSave = async (file: File): Promise<SaveResponse | null> => {
    const analysisResult = await analyzeScript(file);
    if (analysisResult && analysisResult.success) {
      const saveResult = await saveAnalysis(analysisResult);
      
      if (saveResult && saveResult.success) {
        // Create a project entry for the uploaded script with ACTIVE status
        const newProject: Project = {
          id: `api-${saveResult.database_id}`, // Prefix with 'api-' to distinguish from demo projects
          title: file.name.replace(/\.[^/.]+$/, ''), // Remove file extension
          description: `Script analysis project for ${file.name}`,
          status: 'REVIEW', // Set as REVIEW by default (maps to pending_review in backend)
          user_id: user.value?.id || 'current-user',
          budget_total: analysisResult.data?.cost_breakdown?.total_cost || 0,
          estimated_duration_days: 30, // Default estimation
          script_filename: file.name,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          scripts_count: 1,
          type: 'api-script', // Mark as API-generated script
          script_id: saveResult.database_id, // Link to the script in database
          analysis_data: analysisResult.data
        };
        
        // Add to projects list at the beginning
        projects.value.unshift(newProject);
        
        // Set as selected project
        setSelectedProject(newProject.id);
        
        console.log('✅ Created new project for uploaded script:', newProject.title);
      }
      
      return saveResult;
    }
    return null;
  };

  const refreshCurrentScript = async (): Promise<void> => {
    if (currentScript.value?.id) {
      await fetchScript(currentScript.value.id);
    }
  };

  const loadMore = async (): Promise<void> => {
    if (pagination.value.has_more) {
      const nextPage = Math.floor(pagination.value.skip / pagination.value.limit) + 1;
      await fetchScripts(nextPage);
    }
  };

  // Batch operations
  const deleteMultipleScripts = async (scriptIds: string[]): Promise<boolean[]> => {
    const results = await Promise.allSettled(
      scriptIds.map(id => deleteScript(id))
    );
    
    return results.map(result => 
      result.status === 'fulfilled' ? result.value : false
    );
  };

  // Statistics
  const getStatistics = computed(() => ({
    total: totalScripts.value,
    completed: completedScripts.value,
    errors: errorScripts.value,
    pending: pendingScripts.value,
    successRate: totalScripts.value > 0 
      ? Math.round((completedScripts.value / totalScripts.value) * 100) 
      : 0,
  }));

  // Initialize store
  const initialize = async (): Promise<void> => {
    await checkHealth();
    await fetchScripts();
  };

  // Missing methods for ProjectsView
  const setUser = (userData: any) => {
    user.value = userData;
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const removeProject = async (projectId: string): Promise<boolean> => {
    return await deleteProject(projectId);
  };

  const setSelectedProject = (projectIdOrTitle: string) => {
    console.log('🔧 setSelectedProject called with:', projectIdOrTitle);
    console.log('🔧 Current projects count:', projects.value.length);
    console.log('🔧 Available project IDs:', projects.value.map(p => p.id));
    
    // Try to find by ID first
    let project = projects.value.find(p => p.id === projectIdOrTitle);
    console.log('🔧 Found by ID:', project ? `${project.title} (${project.id})` : 'NOT FOUND');
    
    // If not found by ID, try by title
    if (!project) {
      project = projects.value.find(p => p.title === projectIdOrTitle);
      console.log('🔧 Found by title:', project ? `${project.title} (${project.id})` : 'NOT FOUND');
    }
    
    if (project) {
      selectedProjectId.value = project.id;
      selectedProjectTitle.value = project.title;
      currentProject.value = project;
      
      // Persist to localStorage for cross-page persistence
      localStorage.setItem('selectedProjectId', project.id);
      localStorage.setItem('selectedProjectTitle', project.title);
      
      console.log('💾 Saved selected project to localStorage:', project.id, project.title);
    } else {
      console.warn('⚠️ Project not found for selection:', projectIdOrTitle);
      console.warn('⚠️ This might be because projects haven\'t loaded yet');
      
      // If projects haven't loaded yet, still persist the ID to localStorage
      // so it can be picked up later when projects are loaded
      if (projectIdOrTitle && (projectIdOrTitle.startsWith('api-') || projectIdOrTitle.startsWith('demo-'))) {
        selectedProjectId.value = projectIdOrTitle;
        localStorage.setItem('selectedProjectId', projectIdOrTitle);
        console.log('💾 Persisted project ID for later resolution:', projectIdOrTitle);
      }
    }
  };

  const updateProjectStatus = async (projectId: string, status: string, statusColor?: string): Promise<boolean> => {
    try {
      console.log(`🔄 Updating project status for ${projectId} to ${status}`);
      
      // Check if this is an API script (needs backend update)
      if (projectId.startsWith('api-')) {
        const scriptId = projectId.replace('api-', '');
        console.log(`📡 Making API call to update script ${scriptId} status to ${status}`);
        
        // Make API call to update the script status
        const response = await apiCall(`/analyzed-scripts/${scriptId}`, {
          method: 'PUT',
          body: JSON.stringify({ status }),
        });
        
        if (response.success) {
          console.log(`✅ Backend updated successfully for script ${scriptId}`);
        } else {
          console.warn(`⚠️ Backend update may have failed for script ${scriptId}`);
        }
      }
      
      // Update frontend state regardless of backend call result
      // First try to find in projects array
      const projectIndex = projects.value.findIndex(p => p.id === projectId);
      
      if (projectIndex !== -1) {
        // Update project in projects array
        const oldStatus = projects.value[projectIndex].status;
        projects.value[projectIndex].status = status;
        
        // Also update current project if it matches
        if (currentProject.value?.id === projectId) {
          currentProject.value.status = status;
        }
        
        console.log(`✅ Frontend updated: Project ${projectId} status changed from ${oldStatus} to ${status}`);
        return true;
      }
      
      // If not found in projects, it might be an orphaned script - create a project for it
      if (projectId.startsWith('api-')) {
        const scriptId = projectId.replace('api-', '');
        const script = scripts.value.find(s => s.id === scriptId);
        
        if (script) {
          console.log(`📋 Creating project entry for script: ${scriptId}`);
          
          // Create a project entry for this script
          const newProject: Project = {
            id: projectId,
            title: script.filename || 'Untitled Script',
            description: `Script analysis project for ${script.filename}`,
            status: status, // Set to the new status
            user_id: user.value?.id || 'current-user',
            budget_total: script.estimated_budget || 0,
            estimated_duration_days: 30,
            script_filename: script.filename,
            created_at: script.created_at,
            updated_at: new Date().toISOString(),
            scripts_count: 1,
            type: 'api-script',
            script_id: scriptId,
            analysis_data: script
          };
          
          // Add to projects array
          projects.value.unshift(newProject);
          
          console.log(`✅ Created and updated project ${projectId} with status: ${status}`);
          return true;
        }
      }
      
      console.error(`❌ Project not found: ${projectId}`);
      error.value = 'Project not found';
      return false;
      
    } catch (err) {
      console.error('❌ Failed to update project status:', err);
      error.value = err instanceof Error ? err.message : 'Failed to update project status';
      return false;
    }
  };

  const getProjectAnalysis = async (projectId: string): Promise<any> => {
    isLoading.value = true;
    error.value = null;

    try {
      const result = await apiCall(`/projects/${projectId}/analysis`);
      return result.data;
    } catch (err) {
      // If API fails, return null or demo data
      console.log('Analysis API not available');
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // Data transformation utilities
  const transformAPIScene = (apiScene: any): any => {
    return {
      number: apiScene.scene_number || 0,
      heading: apiScene.scene_header || '',
      location: apiScene.location || '',
      time: apiScene.time_of_day || '',
      characters: apiScene.characters_present || [],
      props: apiScene.props_mentioned || [],
      notes: apiScene.action_lines ? apiScene.action_lines.join(' ') : '',
      budget: apiScene.estimated_budget ? `RM ${apiScene.estimated_budget}` : '',
      dialogues: apiScene.dialogue_lines || [],
      wardrobe: [],
      sfx: []
    };
  };

  const transformDemoScene = (demoScene: any): any => {
    return {
      number: demoScene.number || 0,
      heading: demoScene.heading || '',
      location: demoScene.location || '',
      time: demoScene.time || '',
      characters: demoScene.characters || [],
      props: demoScene.props || [],
      notes: demoScene.notes || '',
      budget: demoScene.budget || '',
      dialogues: demoScene.dialogues || [],
      wardrobe: demoScene.wardrobe || [],
      sfx: demoScene.sfx || []
    };
  };

  const standardizeSceneData = (scenes: any[], isAPIData = false): any[] => {
    if (!scenes || !Array.isArray(scenes)) return [];
    
    return scenes.map(scene => 
      isAPIData ? transformAPIScene(scene) : transformDemoScene(scene)
    );
  };

  const getScriptAnalysisData = async (scriptId: string): Promise<any> => {
    try {
      isLoading.value = true;
      const script = scripts.value.find(s => s.id === scriptId);
      
      if (!script) {
        throw new Error('Script not found');
      }

      // Fetch detailed script analysis if not already loaded
      if (!currentScript.value || currentScript.value.id !== scriptId) {
        await fetchScript(scriptId);
      }

      // Return standardized scene data
      const analysisData = currentAnalysis.value;
      console.log('🔍 getScriptAnalysisData - Analysis data:', analysisData);
      
      if (analysisData?.script_data?.scenes) {
        const result = {
          scenes: standardizeSceneData(analysisData.script_data.scenes, true),
          cast_breakdown: analysisData.cast_breakdown,
          cost_breakdown: analysisData.cost_breakdown,
          location_breakdown: analysisData.location_breakdown,
          props_breakdown: analysisData.props_breakdown,
          // Also include the full analysis data for budget processing
          comprehensive_analysis: analysisData
        };
        
        console.log('🔍 getScriptAnalysisData - Returning result:', result);
        return result;
      }

      return null;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load analysis data';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // Budget transformation utilities
  const parseBudgetAmount = (amount: string | number): number => {
    if (typeof amount === 'number') return amount;
    if (typeof amount === 'string') {
      // Remove 'RM', spaces, and commas, then parse
      const cleaned = amount.replace(/[RM\s,]/g, '');
      const parsed = parseFloat(cleaned);
      return isNaN(parsed) ? 0 : parsed;
    }
    return 0;
  };

  const formatBudgetAmount = (amount: number): string => {
    if (amount === 0) return 'RM 0';
    return `RM ${amount.toLocaleString()}`;
  };

  const transformDemoBudget = (budgetData: any): any => {
    const categories = {
      talent: parseBudgetAmount(budgetData.talent || 0),
      location: parseBudgetAmount(budgetData.location || 0),
      propsSet: parseBudgetAmount(budgetData.propsSet || 0),
      wardrobeMakeup: parseBudgetAmount(budgetData.wardrobeMakeup || 0),
      sfxVfx: parseBudgetAmount(budgetData.sfxVfx || 0),
      crew: parseBudgetAmount(budgetData.crew || 0),
      miscellaneous: parseBudgetAmount(budgetData.miscellaneous || 0)
    };

    const total = Object.values(categories).reduce((sum, amount) => sum + amount, 0);

    return {
      ...categories,
      total
    };
  };

  const transformAPIBudget = (apiData: any): any => {
    console.log('🔍 transformAPIBudget - Raw API data:', apiData);
    
    // Try to extract budget data from API response - check nested structure
    let costBreakdown = apiData.cost_breakdown || {};
    
    // If cost_breakdown is not found directly, try nested paths
    if (!costBreakdown || Object.keys(costBreakdown).length === 0) {
      // Try comprehensive_analysis.cost_breakdown
      if (apiData.comprehensive_analysis?.cost_breakdown) {
        costBreakdown = apiData.comprehensive_analysis.cost_breakdown;
        console.log('🔍 transformAPIBudget - Found cost breakdown in comprehensive_analysis');
      }
      // Try data.comprehensive_analysis.cost_breakdown
      else if (apiData.data?.comprehensive_analysis?.cost_breakdown) {
        costBreakdown = apiData.data.comprehensive_analysis.cost_breakdown;
        console.log('🔍 transformAPIBudget - Found cost breakdown in data.comprehensive_analysis');
      }
    }
    
    console.log('🔍 transformAPIBudget - Cost breakdown:', costBreakdown);
    console.log('🔍 transformAPIBudget - Cost breakdown keys:', Object.keys(costBreakdown));
    
    // Map API data to our standard format using the specified mappings:
    // Talent = total_cast_costs
    // Location = total_location_costs  
    // Crew = total_crew_costs
    // Props & Set = total_equipment_costs + total_props_costs
    // Wardrobe & Makeup = total_wardrobe_costs
    const standardBudget = {
      talent: parseBudgetAmount(costBreakdown.total_cast_costs || 0),
      location: parseBudgetAmount(costBreakdown.total_location_costs || 0),
      crew: parseBudgetAmount(costBreakdown.total_crew_costs || 0),
      propsSet: parseBudgetAmount((costBreakdown.total_equipment_costs || 0) + (costBreakdown.total_props_costs || 0)),
      wardrobeMakeup: parseBudgetAmount(costBreakdown.total_wardrobe_costs || 0),
      sfxVfx: parseBudgetAmount(costBreakdown.total_sfx_costs || costBreakdown.total_vfx_costs || 0),
      miscellaneous: parseBudgetAmount(costBreakdown.total_miscellaneous_costs || costBreakdown.total_other_costs || 0)
    };

    console.log('🔍 transformAPIBudget - Standard budget before total:', standardBudget);

    // Calculate total from individual categories
    const calculatedTotal = Object.values(standardBudget).reduce((sum, amount) => sum + amount, 0);
    
    const finalBudget = {
      ...standardBudget,
      total: calculatedTotal
    };

    console.log('🔍 transformAPIBudget - Final budget:', finalBudget);
    
    return finalBudget;
  };

  const calculateBudgetFromScenes = (scenes: any[]): any => {
    if (!scenes || scenes.length === 0) {
      return {
        talent: 0,
        location: 0,
        propsSet: 0,
        wardrobeMakeup: 0,
        sfxVfx: 0,
        crew: 0,
        miscellaneous: 0,
        total: 0
      };
    }

    // Sum up budget estimates from all scenes
    const totalSceneBudget = scenes.reduce((sum, scene) => {
      const sceneBudget = parseBudgetAmount(scene.budget || scene.estimated_budget || 0);
      return sum + sceneBudget;
    }, 0);

    // Estimate distribution based on typical film production ratios
    const estimatedDistribution = {
      talent: Math.round(totalSceneBudget * 0.35), // 35% for talent
      location: Math.round(totalSceneBudget * 0.15), // 15% for locations
      propsSet: Math.round(totalSceneBudget * 0.12), // 12% for props/set
      wardrobeMakeup: Math.round(totalSceneBudget * 0.08), // 8% for wardrobe/makeup
      sfxVfx: Math.round(totalSceneBudget * 0.20), // 20% for VFX/SFX
      crew: Math.round(totalSceneBudget * 0.08), // 8% for crew
      miscellaneous: Math.round(totalSceneBudget * 0.02) // 2% for miscellaneous
    };

    return {
      ...estimatedDistribution,
      total: totalSceneBudget
    };
  };

  const getBudgetBreakdown = async (projectId: string): Promise<any> => {
    try {
      isLoading.value = true;
      
      console.log('🔍 getBudgetBreakdown - Starting for projectId:', projectId);
      
      // Find the project in combined projects list (including API scripts)
      const project = projects.value.find(p => p.id === projectId);
      if (!project) {
        // If not found in projects, check if we can find it in scripts directly
        const scriptId = projectId.startsWith('api-') ? projectId.replace('api-', '') : projectId;
        const script = scripts.value.find(s => s.id === scriptId);
        
        if (script) {
          // Create a temporary project-like object
          const tempProject = {
            id: `api-${script.id}`,
            script_id: script.id,
            title: script.filename,
            type: 'api-script'
          };
          
          console.log('🔍 getBudgetBreakdown - Found script, using as project:', tempProject.title);
          
          // Get script analysis data
          const scriptData = await getScriptAnalysisData(script.id);
          if (scriptData) {
            return transformAPIBudget(scriptData);
          }
        }
        
        throw new Error('Project not found');
      }

      console.log('🔍 getBudgetBreakdown - Project found:', project.title, 'Type:', project.type);

      // Handle API scripts
      if (project.type === 'api-script' && project.script_id) {
        console.log('🔍 getBudgetBreakdown - Getting script analysis data for:', project.script_id);
        
        // First check if we already have the analysis data in current state
        if (currentScript.value?.id === project.script_id && currentAnalysis.value) {
          console.log('🔍 getBudgetBreakdown - Using cached analysis data');
          return transformAPIBudget(currentAnalysis.value);
        }
        
        // Otherwise fetch the script data
        const scriptData = await getScriptAnalysisData(project.script_id);
        console.log('🔍 getBudgetBreakdown - Script data received:', scriptData);
        
        if (scriptData) {
          // Try to get budget from cost breakdown
          if (scriptData.cost_breakdown) {
            console.log('🔍 getBudgetBreakdown - Using cost breakdown for budget');
            return transformAPIBudget(scriptData);
          }
          // Fallback to calculating from scenes
          else if (scriptData.scenes) {
            console.log('🔍 getBudgetBreakdown - Using scenes for budget calculation');
            return calculateBudgetFromScenes(scriptData.scenes);
          } else {
            console.log('⚠️ getBudgetBreakdown - No cost breakdown or scenes found in script data');
          }
        } else {
          console.log('⚠️ getBudgetBreakdown - Script data is null');
        }
      }

      // Handle regular projects
      if (project.scriptBreakdown?.budget) {
        console.log('🔍 getBudgetBreakdown - Using demo budget for regular project');
        return transformDemoBudget(project.scriptBreakdown.budget);
      }

      // Final fallback
      console.log('⚠️ getBudgetBreakdown - Using fallback budget (all zeros)');
      return {
        talent: 0,
        location: 0,
        propsSet: 0,
        wardrobeMakeup: 0,
        sfxVfx: 0,
        crew: 0,
        miscellaneous: 0,
        total: 0
      };

    } catch (err) {
      console.error('❌ getBudgetBreakdown error:', err);
      error.value = err instanceof Error ? err.message : 'Failed to get budget breakdown';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateBudgetCategory = async (projectId: string, category: string, amount: number): Promise<boolean> => {
    try {
      isLoading.value = true;
      
      // Find the project
      const project = projects.value.find(p => p.id === projectId);
      if (!project) {
        throw new Error('Project not found');
      }

      // For API scripts, we would need to update via API
      if (project.type === 'api-script' && project.script_id) {
        // TODO: Implement API budget update
        console.log('API budget update not yet implemented');
        return false;
      }

      // For demo projects, update locally
      if (project.scriptBreakdown?.budget) {
        project.scriptBreakdown.budget[category] = formatBudgetAmount(amount);
        return true;
      }

      return false;

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update budget';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  // Enhanced chatWithScript function
  const chatWithScript = async (scriptId: string, message: string): Promise<string | null> => {
    isLoading.value = true;
    error.value = null;

    try {
      console.log('📡 chatWithScript - Calling API for script:', scriptId);
      console.log('📡 chatWithScript - Message:', message);
      
      const result = await apiCall(`/chat/${scriptId}`, {
        method: 'POST',
        body: JSON.stringify({ message }),
      });
      
      console.log('📡 chatWithScript - API result:', result);
      
      if (result && result.success && result.response) {
        console.log('✅ chatWithScript - Success:', result.response.substring(0, 100) + '...');
        return result.response;
      } else {
        console.error('❌ chatWithScript - Invalid response format:', result);
        error.value = 'Invalid response from chat service';
        return null;
      }
    } catch (err) {
      console.error('❌ chatWithScript - Error:', err);
      error.value = err instanceof Error ? err.message : 'Chat failed';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // Initialize auth and project state from localStorage
  initializeAuth();
  initializeSelectedProject();

  return {
    // State
    user,
    accessToken,
    isLoggedIn,
    projects,
    currentProject,
    selectedProjectId,
    selectedProjectTitle,
    scripts,
    currentScript,
    currentAnalysis,
    isLoading,
    error,
    lastAnalysisResult,
    pagination,
    searchTerm,
    statusFilter,
    
    // Computed
    totalScripts,
    completedScripts,
    errorScripts,
    pendingScripts,
    hasScripts,
    isAnalyzing,
    getStatistics,
    
    // Basic Actions
    checkHealth,
    analyzeScript,
    saveAnalysis,
    fetchScripts,
    fetchScript,
    deleteScript,
    searchScripts,
    filterByStatus,
    provideFeedback,
    getScriptsAwaitingFeedback,
    
    // Utility Actions
    clearError,
    clearCurrentScript,
    clearSearch,
    resetPagination,
    refreshCurrentScript,
    loadMore,
    
    // Data Transformation
    transformAPIScene,
    transformDemoScene,
    standardizeSceneData,
    getScriptAnalysisData,
    
    // Budget Functions
    parseBudgetAmount,
    formatBudgetAmount,
    transformDemoBudget,
    transformAPIBudget,
    calculateBudgetFromScenes,
    getBudgetBreakdown,
    updateBudgetCategory,
    
    // Combined Actions
    analyzeAndSave,
    deleteMultipleScripts,
    initialize,
    
    // Project Actions
    createProjectWithScript,
    createProject,
    fetchProjects,
    updateProject,
    deleteProject,
    setCurrentProject,
    getProjectAnalysis,
    chatWithScript,

    
    // Authentication Actions
    login,
    register,
    logout,
    setLogin,
    setUser,
    removeProject,
    setSelectedProject,
    updateProjectStatus,
  };
});