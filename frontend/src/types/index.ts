// API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

// CEO Request
export interface CEORequest {
  goal: string
  kpis: string[]
  constraints: string[]
  context?: string
  budget?: string
  timeline?: string
}

// Agent Types
export interface Agent {
  id: string
  role: 'hr' | 'rm' | 'expert'
  role_name: string
  description: string
  status: 'active' | 'busy' | 'inactive'
  specialties: string[]
  tools: string[]
  assigned_tasks: string[]
}

// Project Types
export interface Project {
  id: string
  name: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'cancelled'
  priority: string
  deliverables: string[]
  task_ids: string[]
}

// Task Types
export interface Task {
  id: string
  project_id: string
  name: string
  description: string
  type: 'ACTION' | 'DOCUMENT' | 'RESEARCH' | 'APPROVAL'
  status: 'PENDING' | 'INPUT_REQUIRED' | 'VALIDATING' | 'TOOL_CHECK' | 'AWAITING_TOOL' | 'APPROVAL_WAIT' | 'EXECUTING' | 'COMPLETED' | 'FAILED'
  priority: string
  assigned_to?: string
  dependencies: string[]
  required_inputs: RequiredInput[]
  tools: ToolRequirement[]
  approval_points: ApprovalPoint[]
}

export interface RequiredInput {
  key: string
  label: string
  type: string
  required: boolean
  source: string
  description?: string
  example?: string
}

export interface ToolRequirement {
  tool_id: string
  name: string
  type: string
  required: boolean
  status: string
}

export interface ApprovalPoint {
  point: string
  description: string
  approval_type: string
}

// Interrupt Types
export interface Interrupt {
  id: string
  type: 'info_request' | 'approval_request' | 'tool_connection' | 'error_report' | 'progress_report'
  from_agent: string
  message: string
  required_inputs: Array<{
    key: string
    label: string
    type: string
    description?: string
    example?: string
  }>
  options: string[]
  context: Record<string, unknown>
  task_id?: string
  project_id?: string
  created_at: string
}

// State Types
export interface CompanyState {
  current_phase: string
  should_continue: boolean
  error?: string
  ceo_request?: CEORequest
  agents_count: number
  projects_count: number
  tasks_count: number
  pending_tasks_count: number
  pending_interrupts_count: number
  agents: Record<string, {
    id: string
    role_name: string
    status: string
    specialties: string[]
  }>
  projects: Record<string, {
    id: string
    name: string
    status: string
  }>
  tasks: Record<string, {
    id: string
    name: string
    status: string
    assigned_to?: string
  }>
  pending_interrupts: Array<{
    id: string
    type: string
    message: string
    from_agent: string
  }>
}

// Graph Visualization Types
export interface GraphNode {
  id: string
  type: string
  data: {
    label: string
    [key: string]: unknown
  }
  position: { x: number; y: number }
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  animated?: boolean
  type?: string
}

// Chat Types
export interface ChatMessage {
  id: string
  role: 'user' | 'agent' | 'system'
  content: string
  agentId?: string
  agentName?: string
  timestamp: string
}
