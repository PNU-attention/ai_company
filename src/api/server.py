"""FastAPI server for AI Company."""

import asyncio
import json
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.context.state import CEORequest, CompanyState, HumanResponse
from src.context.checkpointer import create_checkpointer
from src.graph.company_graph import create_company_graph
from src.tools.registry import ToolRegistry
from src.tools.mcp_adapter import create_mcp_adapter


# Request/Response Models
class CompanySetupRequest(BaseModel):
    """Request to setup a new company."""
    goal: str = Field(..., description="Company goal")
    kpis: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    context: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None


class InterruptResponseRequest(BaseModel):
    """Request to respond to an interrupt."""
    interrupt_id: str
    approved: Optional[bool] = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message from CEO."""
    content: str
    target_agent: Optional[str] = None  # hr-agent, rm-agent, or specific expert


class ApiResponse(BaseModel):
    """Standard API response."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


# WebSocket Connection Manager
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


# Global instances
manager = ConnectionManager()
active_sessions: dict[str, CompanyState] = {}
session_graphs: dict[str, Any] = {}


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="AI Company API",
        description="API for AI Company - Agentic AI orchestration",
        version="0.1.0"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


# ==================== REST Endpoints ====================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "AI Company API"}


@app.post("/api/sessions", response_model=ApiResponse)
async def create_session():
    """Create a new session."""
    session_id = str(uuid4())
    checkpointer = create_checkpointer()
    graph = create_company_graph(checkpointer=checkpointer)

    session_graphs[session_id] = graph
    active_sessions[session_id] = None

    return ApiResponse(
        success=True,
        data={"session_id": session_id}
    )


@app.get("/api/sessions/{session_id}", response_model=ApiResponse)
async def get_session(session_id: str):
    """Get session state."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]
    state = graph.get_state(session_id)

    if not state:
        return ApiResponse(
            success=True,
            data={"session_id": session_id, "state": None, "status": "initialized"}
        )

    return ApiResponse(
        success=True,
        data={
            "session_id": session_id,
            "state": _serialize_state(state),
            "status": state.current_phase
        }
    )


@app.post("/api/sessions/{session_id}/setup", response_model=ApiResponse)
async def setup_company(session_id: str, request: CompanySetupRequest):
    """Setup company with CEO's goal."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]

    ceo_request = CEORequest(
        goal=request.goal,
        kpis=request.kpis,
        constraints=request.constraints,
        context=request.context,
        budget=request.budget,
        timeline=request.timeline
    )

    try:
        # Run the graph
        final_state = await graph.run(ceo_request, thread_id=session_id)
        active_sessions[session_id] = final_state

        # Notify via WebSocket
        await manager.send_message(session_id, {
            "type": "state_update",
            "data": _serialize_state(final_state)
        })

        return ApiResponse(
            success=True,
            data=_serialize_state(final_state)
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/sessions/{session_id}/respond", response_model=ApiResponse)
async def respond_to_interrupt(session_id: str, request: InterruptResponseRequest):
    """Respond to a pending interrupt."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]

    response = HumanResponse(
        interrupt_id=request.interrupt_id,
        approved=request.approved,
        inputs=request.inputs,
        message=request.message
    )

    try:
        final_state = await graph.resume(response, thread_id=session_id)
        active_sessions[session_id] = final_state

        await manager.send_message(session_id, {
            "type": "state_update",
            "data": _serialize_state(final_state)
        })

        return ApiResponse(
            success=True,
            data=_serialize_state(final_state)
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/sessions/{session_id}/agents", response_model=ApiResponse)
async def get_agents(session_id: str):
    """Get all agents in the session."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]
    state = graph.get_state(session_id)

    if not state:
        return ApiResponse(success=True, data={"agents": []})

    agents = [
        {
            "id": agent.agent_id,
            "role": agent.role.value,
            "role_name": agent.role_name,
            "description": agent.description,
            "status": agent.status.value,
            "specialties": agent.specialties,
            "tools": agent.tools,
            "assigned_tasks": agent.assigned_tasks
        }
        for agent in state.agents.values()
    ]

    return ApiResponse(success=True, data={"agents": agents})


@app.get("/api/sessions/{session_id}/projects", response_model=ApiResponse)
async def get_projects(session_id: str):
    """Get all projects in the session."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]
    state = graph.get_state(session_id)

    if not state:
        return ApiResponse(success=True, data={"projects": []})

    projects = [
        {
            "id": project.project_id,
            "name": project.name,
            "description": project.description,
            "status": project.status.value,
            "priority": project.priority,
            "deliverables": project.deliverables,
            "task_ids": project.task_ids
        }
        for project in state.projects.values()
    ]

    return ApiResponse(success=True, data={"projects": projects})


@app.get("/api/sessions/{session_id}/tasks", response_model=ApiResponse)
async def get_tasks(session_id: str):
    """Get all tasks in the session."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]
    state = graph.get_state(session_id)

    if not state:
        return ApiResponse(success=True, data={"tasks": []})

    tasks = [
        {
            "id": task.task_id,
            "project_id": task.project_id,
            "name": task.name,
            "description": task.description,
            "type": task.type.value,
            "status": task.status.value,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "dependencies": task.dependencies,
            "required_inputs": [inp.model_dump() for inp in task.required_inputs],
            "tools": [t.model_dump() for t in task.tools],
            "approval_points": [ap.model_dump() for ap in task.approval_points]
        }
        for task in state.tasks.values()
    ]

    return ApiResponse(success=True, data={"tasks": tasks})


@app.get("/api/sessions/{session_id}/interrupts", response_model=ApiResponse)
async def get_interrupts(session_id: str):
    """Get pending interrupts."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]
    state = graph.get_state(session_id)

    if not state:
        return ApiResponse(success=True, data={"interrupts": []})

    interrupts = [
        {
            "id": str(interrupt.created_at),
            "type": interrupt.interrupt_type.value,
            "from_agent": interrupt.from_agent,
            "message": interrupt.message,
            "required_inputs": interrupt.required_inputs,
            "options": interrupt.options,
            "context": interrupt.context,
            "task_id": interrupt.task_id,
            "project_id": interrupt.project_id,
            "created_at": interrupt.created_at.isoformat()
        }
        for interrupt in state.pending_interrupts
    ]

    return ApiResponse(success=True, data={"interrupts": interrupts})


@app.get("/api/sessions/{session_id}/graph", response_model=ApiResponse)
async def get_graph_visualization(session_id: str):
    """Get graph data for visualization."""
    if session_id not in session_graphs:
        raise HTTPException(status_code=404, detail="Session not found")

    graph = session_graphs[session_id]
    state = graph.get_state(session_id)

    if not state:
        return ApiResponse(success=True, data={"nodes": [], "edges": []})

    nodes = []
    edges = []

    # Add CEO node
    nodes.append({
        "id": "ceo",
        "type": "ceo",
        "data": {
            "label": "CEO",
            "goal": state.ceo_request.goal if state.ceo_request else "",
            "status": "active"
        },
        "position": {"x": 100, "y": 300}
    })

    # Add HR node
    nodes.append({
        "id": "hr-agent",
        "type": "agent",
        "data": {
            "label": "HR Agent",
            "role": "HR Manager",
            "status": "active",
            "agentType": "hr"
        },
        "position": {"x": 350, "y": 150}
    })
    edges.append({"id": "e-ceo-hr", "source": "ceo", "target": "hr-agent", "animated": True})

    # Add RM node
    nodes.append({
        "id": "rm-agent",
        "type": "agent",
        "data": {
            "label": "RM Agent",
            "role": "Resource Manager",
            "status": "active",
            "agentType": "rm"
        },
        "position": {"x": 350, "y": 450}
    })
    edges.append({"id": "e-ceo-rm", "source": "ceo", "target": "rm-agent", "animated": True})
    edges.append({"id": "e-hr-rm", "source": "hr-agent", "target": "rm-agent", "type": "dashed"})

    # Add expert agents
    x_offset = 600
    y_offset = 100
    expert_count = 0

    for agent_id, agent in state.agents.items():
        if agent_id in ["hr-agent", "rm-agent"]:
            continue

        nodes.append({
            "id": agent_id,
            "type": "agent",
            "data": {
                "label": agent.role_name,
                "role": agent.description[:50] + "..." if len(agent.description) > 50 else agent.description,
                "status": agent.status.value,
                "agentType": "expert",
                "specialties": agent.specialties,
                "tools": agent.tools
            },
            "position": {"x": x_offset, "y": y_offset + (expert_count * 150)}
        })
        edges.append({
            "id": f"e-rm-{agent_id}",
            "source": "rm-agent",
            "target": agent_id,
            "animated": agent.status.value == "active"
        })
        expert_count += 1

    # Add task nodes
    x_task = 900
    y_task = 100
    task_count = 0

    for task_id, task in state.tasks.items():
        status_color = {
            "PENDING": "#6b7280",
            "EXECUTING": "#f59e0b",
            "COMPLETED": "#10b981",
            "FAILED": "#ef4444",
            "INPUT_REQUIRED": "#3b82f6",
            "APPROVAL_WAIT": "#8b5cf6"
        }.get(task.status.value, "#6b7280")

        nodes.append({
            "id": task_id,
            "type": "task",
            "data": {
                "label": task.name,
                "description": task.description[:30] + "..." if len(task.description) > 30 else task.description,
                "status": task.status.value,
                "statusColor": status_color,
                "taskType": task.type.value,
                "assignedTo": task.assigned_to
            },
            "position": {"x": x_task, "y": y_task + (task_count * 120)}
        })

        # Connect task to assigned agent
        if task.assigned_to:
            edges.append({
                "id": f"e-{task.assigned_to}-{task_id}",
                "source": task.assigned_to,
                "target": task_id,
                "animated": task.status.value == "EXECUTING"
            })

        task_count += 1

    return ApiResponse(
        success=True,
        data={"nodes": nodes, "edges": edges}
    )


@app.get("/api/tools", response_model=ApiResponse)
async def get_available_tools():
    """Get all available tools."""
    registry = ToolRegistry.get_instance()
    tools = [
        {
            "id": tool.tool_id,
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "type": tool.type,
            "status": tool.status.value,
            "capabilities": tool.capabilities
        }
        for tool in registry.list_all()
    ]

    return ApiResponse(success=True, data={"tools": tools})


# ==================== WebSocket Endpoint ====================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, session_id)

    try:
        # Send initial state
        if session_id in session_graphs:
            graph = session_graphs[session_id]
            state = graph.get_state(session_id)
            if state:
                await websocket.send_json({
                    "type": "initial_state",
                    "data": _serialize_state(state)
                })

        while True:
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            elif data.get("type") == "chat":
                # Handle chat messages
                response = await _handle_chat_message(
                    session_id,
                    data.get("content", ""),
                    data.get("target_agent")
                )
                await websocket.send_json({
                    "type": "chat_response",
                    "data": response
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)


# ==================== Helper Functions ====================

def _serialize_state(state: CompanyState) -> dict:
    """Serialize CompanyState for JSON response."""
    return {
        "current_phase": state.current_phase,
        "should_continue": state.should_continue,
        "error": state.error,
        "ceo_request": state.ceo_request.model_dump() if state.ceo_request else None,
        "agents_count": len(state.agents),
        "projects_count": len(state.projects),
        "tasks_count": len(state.tasks),
        "pending_tasks_count": len(state.pending_tasks),
        "pending_interrupts_count": len(state.pending_interrupts),
        "agents": {
            aid: {
                "id": a.agent_id,
                "role_name": a.role_name,
                "status": a.status.value,
                "specialties": a.specialties
            }
            for aid, a in state.agents.items()
        },
        "projects": {
            pid: {
                "id": p.project_id,
                "name": p.name,
                "status": p.status.value
            }
            for pid, p in state.projects.items()
        },
        "tasks": {
            tid: {
                "id": t.task_id,
                "name": t.name,
                "status": t.status.value,
                "assigned_to": t.assigned_to
            }
            for tid, t in state.tasks.items()
        },
        "pending_interrupts": [
            {
                "id": str(i.created_at),
                "type": i.interrupt_type.value,
                "message": i.message,
                "from_agent": i.from_agent
            }
            for i in state.pending_interrupts
        ]
    }


async def _handle_chat_message(
    session_id: str,
    content: str,
    target_agent: Optional[str]
) -> dict:
    """Handle chat message from CEO."""
    # This would integrate with the agent system
    # For now, return a placeholder response
    return {
        "from": target_agent or "system",
        "content": f"메시지를 받았습니다: {content}",
        "timestamp": datetime.utcnow().isoformat()
    }


# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
