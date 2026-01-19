"""Tests for memory management."""

import pytest


class TestMemoryManager:
    """Tests for MemoryManager."""

    def test_add_memory(self, memory_manager):
        """Test adding a memory entry."""
        entry = memory_manager.add_memory(
            content="테스트 메모리 항목입니다.",
            memory_type="general",
            source="test"
        )

        assert entry.content == "테스트 메모리 항목입니다."
        assert entry.memory_type == "general"
        assert entry.entry_id is not None

    def test_search_memory(self, memory_manager):
        """Test searching memories."""
        # Add some memories
        memory_manager.add_memory(
            content="쿠팡 셀러 계정을 생성했습니다.",
            memory_type="task_result",
            source="expert-123"
        )
        memory_manager.add_memory(
            content="마케팅 전략을 수립했습니다.",
            memory_type="task_result",
            source="expert-456"
        )

        # Search
        results = memory_manager.search("쿠팡")
        assert len(results) >= 1
        assert "쿠팡" in results[0].content

    def test_get_by_task(self, memory_manager):
        """Test getting memories by task ID."""
        task_id = "task-test-123"

        memory_manager.add_memory(
            content="Task 결과 1",
            task_id=task_id,
            source="test"
        )
        memory_manager.add_memory(
            content="Task 결과 2",
            task_id=task_id,
            source="test"
        )
        memory_manager.add_memory(
            content="다른 Task 결과",
            task_id="other-task",
            source="test"
        )

        results = memory_manager.get_by_task(task_id)
        assert len(results) == 2

    def test_store_task_result(self, memory_manager):
        """Test storing task result."""
        entry = memory_manager.store_task_result(
            task_id="task-123",
            project_id="proj-123",
            task_name="셀러 계정 생성",
            result={"account_id": "seller123", "status": "created"},
            agent_id="expert-456"
        )

        assert "셀러 계정 생성" in entry.content
        assert entry.memory_type == "task_result"
        assert entry.task_id == "task-123"

    def test_store_decision(self, memory_manager):
        """Test storing a decision."""
        entry = memory_manager.store_decision(
            decision="쿠팡 Wing 요금제 선택",
            context="월 매출 예상에 따라 Wing 요금제가 적합함",
            agent_id="rm-agent",
            project_id="proj-123"
        )

        assert entry.memory_type == "decision"
        assert "Wing 요금제" in entry.content


class TestCheckpointer:
    """Tests for SQLite Checkpointer."""

    def test_create_checkpointer(self, temp_db):
        """Test creating checkpointer."""
        from src.context.checkpointer import create_checkpointer

        checkpointer = create_checkpointer(db_path=temp_db)
        assert checkpointer is not None

    def test_put_and_get_checkpoint(self, temp_db):
        """Test saving and retrieving checkpoint."""
        from src.context.checkpointer import create_checkpointer
        from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata

        checkpointer = create_checkpointer(db_path=temp_db)

        config = {"configurable": {"thread_id": "test-thread"}}

        checkpoint = Checkpoint(
            v=1,
            id="checkpoint-123",
            ts="2024-01-01T00:00:00",
            channel_values={"test": "value"},
            channel_versions={},
            versions_seen={},
            pending_sends=[]
        )

        metadata = CheckpointMetadata()

        # Save checkpoint
        new_config = checkpointer.put(config, checkpoint, metadata, {})

        assert new_config["configurable"]["checkpoint_id"] == "checkpoint-123"

        # Retrieve checkpoint
        result = checkpointer.get_tuple(new_config)

        assert result is not None
        assert result.checkpoint["id"] == "checkpoint-123"

    def test_list_checkpoints(self, temp_db):
        """Test listing checkpoints."""
        from src.context.checkpointer import create_checkpointer
        from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata

        checkpointer = create_checkpointer(db_path=temp_db)

        config = {"configurable": {"thread_id": "list-test"}}

        # Add multiple checkpoints
        for i in range(3):
            checkpoint = Checkpoint(
                v=1,
                id=f"checkpoint-{i}",
                ts=f"2024-01-0{i+1}T00:00:00",
                channel_values={"step": i},
                channel_versions={},
                versions_seen={},
                pending_sends=[]
            )
            checkpointer.put(
                {"configurable": {"thread_id": "list-test", "checkpoint_id": f"checkpoint-{i-1}" if i > 0 else None}},
                checkpoint,
                CheckpointMetadata(),
                {}
            )

        # List checkpoints
        checkpoints = list(checkpointer.list(config))
        assert len(checkpoints) == 3

    def test_delete_thread(self, temp_db):
        """Test deleting thread checkpoints."""
        from src.context.checkpointer import create_checkpointer
        from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata

        checkpointer = create_checkpointer(db_path=temp_db)

        # Add checkpoint
        config = {"configurable": {"thread_id": "delete-test"}}
        checkpoint = Checkpoint(
            v=1,
            id="delete-checkpoint",
            ts="2024-01-01T00:00:00",
            channel_values={},
            channel_versions={},
            versions_seen={},
            pending_sends=[]
        )
        checkpointer.put(config, checkpoint, CheckpointMetadata(), {})

        # Delete
        checkpointer.delete_thread("delete-test")

        # Verify deleted
        result = checkpointer.get_tuple(config)
        assert result is None
