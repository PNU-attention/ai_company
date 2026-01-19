"""SQLite-based checkpointing for LangGraph state persistence."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence, Tuple

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)

from src.config import get_settings


class SQLiteCheckpointer(BaseCheckpointSaver):
    """
    SQLite-based checkpoint saver for LangGraph.

    Provides persistent storage for graph state, enabling:
    - State recovery after interrupts
    - Session resumption
    - Audit trail of state changes
    """

    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        if db_path:
            self.db_path = db_path
        else:
            settings = get_settings()
            # Extract path from SQLite URL
            db_url = settings.database_url
            if db_url.startswith("sqlite:///"):
                self.db_path = db_url.replace("sqlite:///", "")
            else:
                self.db_path = str(Path(__file__).parent.parent.parent / "data" / "checkpoints.db")

        self._ensure_tables()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_tables(self) -> None:
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    parent_id TEXT,
                    checkpoint_data TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (thread_id, checkpoint_id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
                ON checkpoints (thread_id, created_at DESC)
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS writes (
                    thread_id TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    write_type TEXT NOT NULL,
                    write_data TEXT NOT NULL,
                    idx INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (thread_id, checkpoint_id, task_id, idx)
                )
            """)

            conn.commit()

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple by config."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id")

        with self._get_connection() as conn:
            if checkpoint_id:
                cursor = conn.execute(
                    """
                    SELECT checkpoint_id, parent_id, checkpoint_data, metadata
                    FROM checkpoints
                    WHERE thread_id = ? AND checkpoint_id = ?
                    """,
                    (thread_id, checkpoint_id)
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT checkpoint_id, parent_id, checkpoint_data, metadata
                    FROM checkpoints
                    WHERE thread_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (thread_id,)
                )

            row = cursor.fetchone()

            if not row:
                return None

            checkpoint_data = json.loads(row["checkpoint_data"])
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}

            checkpoint = Checkpoint(
                v=1,
                id=row["checkpoint_id"],
                ts=datetime.utcnow().isoformat(),
                channel_values=checkpoint_data.get("channel_values", {}),
                channel_versions=checkpoint_data.get("channel_versions", {}),
                versions_seen=checkpoint_data.get("versions_seen", {}),
                pending_sends=checkpoint_data.get("pending_sends", []),
            )

            return CheckpointTuple(
                config=config,
                checkpoint=checkpoint,
                metadata=CheckpointMetadata(**metadata) if metadata else CheckpointMetadata(),
                parent_config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": row["parent_id"]
                    }
                } if row["parent_id"] else None,
                pending_writes=[],
            )

    def list(
        self,
        config: Optional[dict],
        *,
        filter: Optional[dict] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints."""
        if not config:
            return

        thread_id = config["configurable"]["thread_id"]

        query = """
            SELECT checkpoint_id, parent_id, checkpoint_data, metadata, created_at
            FROM checkpoints
            WHERE thread_id = ?
        """
        params = [thread_id]

        if before:
            before_id = before.get("configurable", {}).get("checkpoint_id")
            if before_id:
                query += " AND checkpoint_id < ?"
                params.append(before_id)

        query += " ORDER BY created_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)

            for row in cursor:
                checkpoint_data = json.loads(row["checkpoint_data"])
                metadata = json.loads(row["metadata"]) if row["metadata"] else {}

                checkpoint = Checkpoint(
                    v=1,
                    id=row["checkpoint_id"],
                    ts=row["created_at"],
                    channel_values=checkpoint_data.get("channel_values", {}),
                    channel_versions=checkpoint_data.get("channel_versions", {}),
                    versions_seen=checkpoint_data.get("versions_seen", {}),
                    pending_sends=checkpoint_data.get("pending_sends", []),
                )

                yield CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": row["checkpoint_id"]
                        }
                    },
                    checkpoint=checkpoint,
                    metadata=CheckpointMetadata(**metadata) if metadata else CheckpointMetadata(),
                    parent_config={
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": row["parent_id"]
                        }
                    } if row["parent_id"] else None,
                    pending_writes=[],
                )

    def put(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        """Save a checkpoint."""
        thread_id = config["configurable"]["thread_id"]
        parent_id = config["configurable"].get("checkpoint_id")

        checkpoint_data = {
            "channel_values": self._serialize_channel_values(checkpoint.get("channel_values", {})),
            "channel_versions": checkpoint.get("channel_versions", {}),
            "versions_seen": checkpoint.get("versions_seen", {}),
            "pending_sends": checkpoint.get("pending_sends", []),
        }

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints
                (thread_id, checkpoint_id, parent_id, checkpoint_data, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    thread_id,
                    checkpoint["id"],
                    parent_id,
                    json.dumps(checkpoint_data, default=str),
                    json.dumps(metadata.__dict__ if hasattr(metadata, '__dict__') else {}, default=str),
                )
            )
            conn.commit()

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint["id"]
            }
        }

    def put_writes(
        self,
        config: dict,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Save pending writes."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id", "")

        with self._get_connection() as conn:
            for idx, (channel, value) in enumerate(writes):
                conn.execute(
                    """
                    INSERT OR REPLACE INTO writes
                    (thread_id, checkpoint_id, task_id, channel, write_type, write_data, idx)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        thread_id,
                        checkpoint_id,
                        task_id,
                        channel,
                        type(value).__name__,
                        json.dumps(value, default=str),
                        idx,
                    )
                )
            conn.commit()

    def _serialize_channel_values(self, values: dict) -> dict:
        """Serialize channel values for storage."""
        serialized = {}
        for key, value in values.items():
            if hasattr(value, "model_dump"):
                serialized[key] = value.model_dump()
            elif hasattr(value, "__dict__"):
                serialized[key] = value.__dict__
            else:
                serialized[key] = value
        return serialized

    def delete_thread(self, thread_id: str) -> None:
        """Delete all checkpoints for a thread."""
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = ?",
                (thread_id,)
            )
            conn.execute(
                "DELETE FROM writes WHERE thread_id = ?",
                (thread_id,)
            )
            conn.commit()

    def clear_all(self) -> None:
        """Clear all checkpoints (for testing)."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM checkpoints")
            conn.execute("DELETE FROM writes")
            conn.commit()


def create_checkpointer(db_path: Optional[str] = None) -> SQLiteCheckpointer:
    """Factory function to create a checkpointer."""
    return SQLiteCheckpointer(db_path=db_path)
