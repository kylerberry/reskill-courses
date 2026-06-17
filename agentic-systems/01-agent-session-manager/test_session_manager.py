"""
Scaffolded tests for Agent Session Manager.

Fill in the assertions during the red-tests step.
Each test should fail until you implement the corresponding logic.
"""

import pytest
from session_manager import (
    SessionManager,
    SessionStatus,
    Checkpoint,
    ToolCall,
    ResumeResult,
)


@pytest.fixture
def manager():
    mgr = SessionManager(checkpoint_strategy="fine")
    yield mgr
    mgr.close()


class TestSessionLifecycle:
    def test_create_session_returns_id(self, manager):
        pytest.skip("TODO(human): Assert that create_session returns a non-empty string")

    def test_session_starts_in_initializing_state(self, manager):
        pytest.skip("TODO(human): Assert that a newly created session has status INITIALIZING")

    def test_update_status_transitions_state(self, manager):
        pytest.skip("TODO(human): Assert that update_status changes the session status")


class TestCheckpointing:
    def test_checkpoint_is_stored(self, manager):
        pytest.skip("TODO(human): Assert that after checkpoint() the session stores the checkpoint")

    def test_latest_checkpoint_id_updated(self, manager):
        pytest.skip("TODO(human): Assert that latest_checkpoint_id points to the most recent checkpoint")

    def test_multiple_checkpoints_preserved(self, manager):
        pytest.skip("TODO(human): Assert that multiple checkpoints are all kept in session.checkpoints")


class TestResumeSession:
    def test_resume_returns_latest_checkpoint(self, manager):
        pytest.skip("TODO(human): Assert that resume_session returns the most recent checkpoint data")

    def test_resume_finds_pending_tool_calls(self, manager):
        pytest.skip("TODO(human): Assert that incomplete tool calls are listed as pending")

    def test_resume_skips_completed_tool_calls(self, manager):
        pytest.skip("TODO(human): Assert that completed tool calls are NOT in pending_tool_calls")

    def test_resume_includes_pending_sub_agents(self, manager):
        pytest.skip("TODO(human): Assert that non-terminal sub-agents are included in pending_sub_agents")

    def test_resume_excludes_completed_sub_agents(self, manager):
        pytest.skip("TODO(human): Assert that completed sub-agents are NOT in pending_sub_agents")

    def test_resume_raises_on_missing_session(self, manager):
        pytest.skip("TODO(human): Assert that resuming a non-existent session raises an error")


class TestHierarchicalSessions:
    def test_child_session_has_parent_id(self, manager):
        pytest.skip("TODO(human): Assert that a child session stores its parent's session_id")

    def test_sub_agent_lifecycle_events(self, manager):
        pytest.skip("TODO(human): Assert that sub-agent events are emitted and retrievable")


class TestObservability:
    def test_events_are_emitted(self, manager):
        pytest.skip("TODO(human): Assert that lifecycle events are stored and retrievable")

    def test_event_limit_works(self, manager):
        pytest.skip("TODO(human): Assert that get_events(limit=N) returns at most N events")
