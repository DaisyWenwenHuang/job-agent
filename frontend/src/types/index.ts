export interface Job {
  id: string
  source: 'linkedin' | 'indeed'
  external_id: string | null
  url: string
  title: string
  company: string
  location: string | null
  remote_type: string | null
  employment_type: string | null
  seniority: string | null
  description: string | null
  salary_range: string | null
  posted_date: string | null
  scraped_at: string
  claude_score: number | null
  claude_reasoning: string | null  // JSON array string
  claude_summary: string | null
  claude_seniority: string | null
  claude_red_flags: string | null  // JSON array string
  claude_role_type: string | null
  status: 'pending_review' | 'approved' | 'rejected' | 'applied' | 'skipped'
  reviewed_at: string | null
  applied_at: string | null
  apply_error: string | null
}

export interface Application {
  id: string
  job_id: string
  applied_at: string
  platform: string
  method: string | null
  status: 'submitted' | 'failed' | 'requires_manual'
  error_detail: string | null
  confirmation_text: string | null
}

export interface RunHistory {
  id: string
  started_at: string
  finished_at: string | null
  trigger: 'scheduled' | 'manual'
  status: 'running' | 'completed' | 'failed'
  jobs_scraped: number
  jobs_new: number
  jobs_scored: number
  jobs_applied: number
  error_message: string | null
  log_output: string | null
}

export interface JobConfig {
  target_roles: string[]
  location: {
    city: string
    state: string
    max_miles_onsite: number
    allowed_remote_types: string[]
  }
  employment_types: string[]
  seniority_levels: string[]
  min_claude_score: number
  apply_automatically: boolean
  daily_apply_limit: number
  platforms: {
    linkedin: { enabled: boolean; max_results_per_run: number }
    indeed: { enabled: boolean; max_results_per_run: number }
  }
  scheduler: { run_time: string; timezone: string }
}
