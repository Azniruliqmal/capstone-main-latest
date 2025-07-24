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
  dialogues?: Array<{character: string, text: string}>
}

// Unified Scene interface for consistent data handling
export interface UnifiedScene {
  number: number
  heading: string  
  location: string
  time: string
  characters: string[]
  props: string[]
  notes: string
  budget?: string
  dialogues?: Array<{character: string, text: string}>
  wardrobe?: string[]
  sfx?: string[]
}

// API Scene structure (from backend analysis)
export interface APIScene {
  scene_number: number
  scene_header: string
  location: string
  time_of_day: string
  characters_present: string[]
  props_mentioned: string[]
  action_lines: string[]
  dialogue_lines?: Array<{character: string, text: string}>
  estimated_budget?: number
}

// Budget breakdown interface
export interface BudgetBreakdown {
  talent: number
  location: number
  propsSet: number
  wardrobeMakeup: number
  sfxVfx: number
  crew: number
  miscellaneous: number
  total: number
}

// Budget category interface
export interface BudgetCategory {
  name: string
  amount: number
  percentage: number
  color: string
}

// API budget structure
export interface APIBudgetData {
  cost_breakdown?: {
    categories?: Record<string, any>
    totals?: Record<string, any>
    scene_budgets?: Record<string, number>
  }
  estimated_budget?: number
  budget_total?: number
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