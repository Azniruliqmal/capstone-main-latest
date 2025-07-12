export interface Scene {
  number: number
  heading: string
  location: string
  time: string
  characters: string[]
  props: string[]
  wardrobe: string[]
  sfx: string[]
  notes: string
  budget: string
}

export interface Project {
  id: string
  title: string
  description?: string
  status: string
  user_id?: string
  budget_total?: number
  estimated_duration_days?: number
  script_filename?: string
  created_at: string
  updated_at: string
  scripts_count: number
  // UI-specific properties
  genre?: string
  statusColor?: string
  budget?: string
  dueDate?: string
  team?: string
  analysis_data?: any
  scriptBreakdown?: {
    scenes: Scene[]
    // ...other breakdown fields
  }
}