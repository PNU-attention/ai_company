"""Memory management using ChromaDB for vector storage."""

import json
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """A single memory entry."""
    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    content: str = Field(..., description="Memory content")
    memory_type: str = Field(default="general", description="Type: task_result, conversation, knowledge, decision")
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="system", description="Source agent or system")
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryManager:
    """
    Manager for long-term memory using ChromaDB.

    Provides:
    - Semantic search over past interactions
    - Task result storage and retrieval
    - Knowledge base management
    - Decision history
    """

    def __init__(self, persist_directory: Optional[str] = None):
        self._initialized = False
        self._persist_directory = persist_directory
        self._collection = None
        self._client = None

    def _ensure_initialized(self) -> None:
        """Lazy initialization of ChromaDB."""
        if self._initialized:
            return

        try:
            import chromadb
            from chromadb.config import Settings

            if self._persist_directory:
                self._client = chromadb.PersistentClient(
                    path=self._persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )
            else:
                self._client = chromadb.Client(
                    settings=Settings(anonymized_telemetry=False)
                )

            self._collection = self._client.get_or_create_collection(
                name="company_memory",
                metadata={"hnsw:space": "cosine"}
            )
            self._initialized = True
        except ImportError:
            # ChromaDB not installed, use in-memory fallback
            self._memories: list[MemoryEntry] = []
            self._initialized = True

    def add_memory(
        self,
        content: str,
        memory_type: str = "general",
        metadata: dict[str, Any] = None,
        source: str = "system",
        project_id: str = None,
        task_id: str = None,
    ) -> MemoryEntry:
        """Add a new memory entry."""
        self._ensure_initialized()

        entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            metadata=metadata or {},
            source=source,
            project_id=project_id,
            task_id=task_id,
        )

        if self._collection:
            self._collection.add(
                ids=[entry.entry_id],
                documents=[content],
                metadatas=[{
                    "memory_type": memory_type,
                    "source": source,
                    "project_id": project_id or "",
                    "task_id": task_id or "",
                    "created_at": entry.created_at.isoformat(),
                    **{k: str(v) for k, v in (metadata or {}).items()}
                }]
            )
        else:
            self._memories.append(entry)

        return entry

    def search(
        self,
        query: str,
        n_results: int = 5,
        memory_type: str = None,
        project_id: str = None,
    ) -> list[MemoryEntry]:
        """Search memories semantically."""
        self._ensure_initialized()

        if self._collection:
            where = {}
            if memory_type:
                where["memory_type"] = memory_type
            if project_id:
                where["project_id"] = project_id

            results = self._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where if where else None
            )

            entries = []
            for i, doc in enumerate(results.get("documents", [[]])[0]):
                metadata = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
                entries.append(MemoryEntry(
                    entry_id=results.get("ids", [[]])[0][i],
                    content=doc,
                    memory_type=metadata.get("memory_type", "general"),
                    source=metadata.get("source", "system"),
                    project_id=metadata.get("project_id") or None,
                    task_id=metadata.get("task_id") or None,
                ))
            return entries
        else:
            # Fallback: simple keyword matching
            results = []
            query_lower = query.lower()
            for entry in self._memories:
                if query_lower in entry.content.lower():
                    if memory_type and entry.memory_type != memory_type:
                        continue
                    if project_id and entry.project_id != project_id:
                        continue
                    results.append(entry)
                    if len(results) >= n_results:
                        break
            return results

    def get_by_task(self, task_id: str) -> list[MemoryEntry]:
        """Get all memories for a specific task."""
        self._ensure_initialized()

        if self._collection:
            results = self._collection.get(
                where={"task_id": task_id}
            )
            entries = []
            for i, doc in enumerate(results.get("documents", [])):
                metadata = results.get("metadatas", [])[i] if results.get("metadatas") else {}
                entries.append(MemoryEntry(
                    entry_id=results.get("ids", [])[i],
                    content=doc,
                    memory_type=metadata.get("memory_type", "general"),
                    source=metadata.get("source", "system"),
                    project_id=metadata.get("project_id") or None,
                    task_id=task_id,
                ))
            return entries
        else:
            return [e for e in self._memories if e.task_id == task_id]

    def get_by_project(self, project_id: str) -> list[MemoryEntry]:
        """Get all memories for a specific project."""
        self._ensure_initialized()

        if self._collection:
            results = self._collection.get(
                where={"project_id": project_id}
            )
            entries = []
            for i, doc in enumerate(results.get("documents", [])):
                metadata = results.get("metadatas", [])[i] if results.get("metadatas") else {}
                entries.append(MemoryEntry(
                    entry_id=results.get("ids", [])[i],
                    content=doc,
                    memory_type=metadata.get("memory_type", "general"),
                    source=metadata.get("source", "system"),
                    project_id=project_id,
                    task_id=metadata.get("task_id") or None,
                ))
            return entries
        else:
            return [e for e in self._memories if e.project_id == project_id]

    def store_task_result(
        self,
        task_id: str,
        project_id: str,
        task_name: str,
        result: dict[str, Any],
        agent_id: str,
    ) -> MemoryEntry:
        """Store a task execution result."""
        content = f"Task '{task_name}' completed by {agent_id}. Result: {json.dumps(result, ensure_ascii=False)}"

        return self.add_memory(
            content=content,
            memory_type="task_result",
            metadata={"task_name": task_name, "result": result},
            source=agent_id,
            project_id=project_id,
            task_id=task_id,
        )

    def store_decision(
        self,
        decision: str,
        context: str,
        agent_id: str,
        project_id: str = None,
        task_id: str = None,
    ) -> MemoryEntry:
        """Store an important decision."""
        content = f"Decision by {agent_id}: {decision}. Context: {context}"

        return self.add_memory(
            content=content,
            memory_type="decision",
            metadata={"decision": decision, "context": context},
            source=agent_id,
            project_id=project_id,
            task_id=task_id,
        )

    def clear(self) -> None:
        """Clear all memories (for testing)."""
        self._ensure_initialized()

        if self._collection and self._client:
            self._client.delete_collection("company_memory")
            self._collection = self._client.get_or_create_collection(
                name="company_memory",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self._memories = []
