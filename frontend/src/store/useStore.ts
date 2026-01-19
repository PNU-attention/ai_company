import { create } from 'zustand'
import type { CompanyState, Agent, Project, Task, Interrupt, ChatMessage, GraphNode, GraphEdge } from '../types'

interface Store {
  // Session
  sessionId: string | null
  isLoading: boolean
  error: string | null

  // Company State
  companyState: CompanyState | null
  agents: Agent[]
  projects: Project[]
  tasks: Task[]
  interrupts: Interrupt[]

  // Graph
  graphNodes: GraphNode[]
  graphEdges: GraphEdge[]

  // Chat
  chatMessages: ChatMessage[]
  selectedAgent: string | null

  // WebSocket
  ws: WebSocket | null

  // Actions
  createSession: () => Promise<void>
  setupCompany: (request: {
    goal: string
    kpis: string[]
    constraints: string[]
    context?: string
    budget?: string
    timeline?: string
  }) => Promise<void>
  respondToInterrupt: (interruptId: string, response: {
    approved?: boolean
    inputs?: Record<string, unknown>
    message?: string
  }) => Promise<void>
  fetchState: () => Promise<void>
  fetchAgents: () => Promise<void>
  fetchProjects: () => Promise<void>
  fetchTasks: () => Promise<void>
  fetchInterrupts: () => Promise<void>
  fetchGraph: () => Promise<void>
  connectWebSocket: () => void
  disconnectWebSocket: () => void
  sendChatMessage: (content: string, targetAgent?: string) => void
  setSelectedAgent: (agentId: string | null) => void
  addChatMessage: (message: ChatMessage) => void
  setError: (error: string | null) => void
}

const API_BASE = ''

export const useStore = create<Store>((set, get) => ({
  // Initial State
  sessionId: null,
  isLoading: false,
  error: null,
  companyState: null,
  agents: [],
  projects: [],
  tasks: [],
  interrupts: [],
  graphNodes: [],
  graphEdges: [],
  chatMessages: [],
  selectedAgent: null,
  ws: null,

  // Actions
  createSession: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch(`${API_BASE}/api/sessions`, {
        method: 'POST',
      })
      const data = await response.json()
      if (data.success) {
        set({ sessionId: data.data.session_id })
        get().connectWebSocket()
      } else {
        set({ error: data.error })
      }
    } catch (err) {
      set({ error: 'Failed to create session' })
    } finally {
      set({ isLoading: false })
    }
  },

  setupCompany: async (request) => {
    const { sessionId } = get()
    if (!sessionId) return

    set({ isLoading: true, error: null })
    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      })
      const data = await response.json()
      if (data.success) {
        set({ companyState: data.data })
        // Fetch all related data
        await Promise.all([
          get().fetchAgents(),
          get().fetchProjects(),
          get().fetchTasks(),
          get().fetchInterrupts(),
          get().fetchGraph(),
        ])
      } else {
        set({ error: data.error })
      }
    } catch (err) {
      set({ error: 'Failed to setup company' })
    } finally {
      set({ isLoading: false })
    }
  },

  respondToInterrupt: async (interruptId, response) => {
    const { sessionId } = get()
    if (!sessionId) return

    set({ isLoading: true, error: null })
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interrupt_id: interruptId,
          ...response,
        }),
      })
      const data = await res.json()
      if (data.success) {
        set({ companyState: data.data })
        await Promise.all([
          get().fetchAgents(),
          get().fetchProjects(),
          get().fetchTasks(),
          get().fetchInterrupts(),
          get().fetchGraph(),
        ])
      } else {
        set({ error: data.error })
      }
    } catch (err) {
      set({ error: 'Failed to respond to interrupt' })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchState: async () => {
    const { sessionId } = get()
    if (!sessionId) return

    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}`)
      const data = await response.json()
      if (data.success && data.data.state) {
        set({ companyState: data.data.state })
      }
    } catch (err) {
      console.error('Failed to fetch state:', err)
    }
  },

  fetchAgents: async () => {
    const { sessionId } = get()
    if (!sessionId) return

    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/agents`)
      const data = await response.json()
      if (data.success) {
        set({ agents: data.data.agents })
      }
    } catch (err) {
      console.error('Failed to fetch agents:', err)
    }
  },

  fetchProjects: async () => {
    const { sessionId } = get()
    if (!sessionId) return

    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/projects`)
      const data = await response.json()
      if (data.success) {
        set({ projects: data.data.projects })
      }
    } catch (err) {
      console.error('Failed to fetch projects:', err)
    }
  },

  fetchTasks: async () => {
    const { sessionId } = get()
    if (!sessionId) return

    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/tasks`)
      const data = await response.json()
      if (data.success) {
        set({ tasks: data.data.tasks })
      }
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
    }
  },

  fetchInterrupts: async () => {
    const { sessionId } = get()
    if (!sessionId) return

    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/interrupts`)
      const data = await response.json()
      if (data.success) {
        set({ interrupts: data.data.interrupts })
      }
    } catch (err) {
      console.error('Failed to fetch interrupts:', err)
    }
  },

  fetchGraph: async () => {
    const { sessionId } = get()
    if (!sessionId) return

    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/graph`)
      const data = await response.json()
      if (data.success) {
        set({ graphNodes: data.data.nodes, graphEdges: data.data.edges })
      }
    } catch (err) {
      console.error('Failed to fetch graph:', err)
    }
  },

  connectWebSocket: () => {
    const { sessionId } = get()
    if (!sessionId) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.type === 'state_update') {
        set({ companyState: message.data })
        get().fetchGraph()
      } else if (message.type === 'chat_response') {
        get().addChatMessage({
          id: Date.now().toString(),
          role: 'agent',
          content: message.data.content,
          agentId: message.data.from,
          agentName: message.data.from,
          timestamp: message.data.timestamp,
        })
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      set({ ws: null })
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    set({ ws })
  },

  disconnectWebSocket: () => {
    const { ws } = get()
    if (ws) {
      ws.close()
      set({ ws: null })
    }
  },

  sendChatMessage: (content, targetAgent) => {
    const { ws } = get()
    if (!ws) return

    // Add user message to chat
    get().addChatMessage({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    })

    // Send via WebSocket
    ws.send(JSON.stringify({
      type: 'chat',
      content,
      target_agent: targetAgent,
    }))
  },

  setSelectedAgent: (agentId) => {
    set({ selectedAgent: agentId })
  },

  addChatMessage: (message) => {
    set((state) => ({
      chatMessages: [...state.chatMessages, message],
    }))
  },

  setError: (error) => {
    set({ error })
  },
}))
