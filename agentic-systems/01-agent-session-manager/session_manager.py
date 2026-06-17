"""
Agent Session Manager

Production-grade session management and state persistence for multi-agent
AI systems with long-running tasks.

Design a system that:
1. Enables resumable sessions — recover from failures without losing progress
2. Tracks hierarchical agent relationships — parent/child with cascading resumption
3. Implements flexible checkpointing — fine vs coarse-grained strategies
4. Provides real-time observability — event stream for monitoring progress
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class SessionStatus(str, Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ToolCall:
    """A single tool invocation within an agent session."""
    tool_name: str
    args: Dict[str, Any]
    result: Any = None
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    completed: bool = False
    cacheable: bool = False


@dataclass
class Artifact:
    """An output produced during agent execution."""
    artifact_id: str
    artifact_type: str
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# TODO(human): Design the checkpoint state model
#
# A checkpoint captures everything needed to resume an agent's work.
# Consider what you need to persist:
# - Tool calls made so far?
# - Artifacts generated (files, analysis results)?
# - Agent memory/context?
# - Sub-agent references?
# - Progress indicators?
#
# Trade-offs:
# - Granular checkpoints = easier resume, more storage
# - Coarse checkpoints = less overhead, more re-work on resume
@dataclass
class Checkpoint:
    checkpoint_id: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    artifacts: Dict[str, Artifact] = field(default_factory=dict)
    context: str = ""
    sub_agents: Dict[str, str] = field(default_factory=dict)
    progress: float = 0.0
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


# TODO(human): Design the session state model
#
# Session state is the complete, resumable representation of a running agent.
# Think about:
# - What's the relationship between Session and Checkpoint?
# - Should sessions store ALL checkpoints or just the latest?
# - How do you handle sub-agent sessions?
@dataclass
class Session:
    metadata: SessionMetadata
    checkpoint_strategy: str = "fine"  # "fine" | "coarse"
    latest_checkpoint_id: str = ""
    checkpoints: Dict[str, Checkpoint] = field(default_factory=dict)


@dataclass
class SessionMetadata:
    session_id: str
    agent_id: str
    status: SessionStatus = SessionStatus.INITIALIZING
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    parent_session_id: Optional[str] = None


@dataclass
class ResumeResult:
    """Everything an agent runtime needs to restart execution."""
    checkpoint: Checkpoint
    pending_tool_calls: List[ToolCall] = field(default_factory=list)
    pending_sub_agents: List[dict] = field(default_factory=list)


@dataclass
class SessionEvent:
    type: str
    session_id: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    payload: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Storage Abstraction
# ---------------------------------------------------------------------------

class SessionStore(Protocol):
    """Storage layer abstraction — swap SQLite for PostgreSQL/DynamoDB/Redis."""

    def create_session(self, session: Session) -> None: ...
    def get_session(self, session_id: str) -> Optional[Session]: ...
    def update_session(self, session: Session) -> None: ...
    def get_all_sessions(self) -> List[Session]: ...
    def add_checkpoint(self, session_id: str, checkpoint: Checkpoint) -> None: ...
    def emit_event(self, event: SessionEvent) -> None: ...
    def get_events(self, session_id: str, limit: Optional[int] = None) -> List[SessionEvent]: ...
    def close(self) -> None: ...


class SQLiteSessionStore:
    """SQLite-backed session store for local development."""

    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                status TEXT NOT NULL,
                parent_session_id TEXT,
                checkpoint_strategy TEXT NOT NULL,
                latest_checkpoint_id TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                checkpoints_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                payload_json TEXT NOT NULL DEFAULT '{}'
            );
        """)
        self.conn.commit()

    def create_session(self, session: Session) -> None:
        m = session.metadata
        self.conn.execute(
            """
            INSERT INTO sessions
            (session_id, agent_id, status, parent_session_id, checkpoint_strategy,
             latest_checkpoint_id, created_at, updated_at, checkpoints_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                m.session_id, m.agent_id, m.status.value, m.parent_session_id,
                session.checkpoint_strategy, session.latest_checkpoint_id,
                m.created_at, m.updated_at, json.dumps({})
            ),
        )
        self.conn.commit()

    def get_session(self, session_id: str) -> Optional[Session]:
        row = self.conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not row:
            return None
        # Deserialize checkpoints from JSON
        checkpoints = {}
        for cp_id, cp_data in json.loads(row["checkpoints_json"]).items():
            checkpoints[cp_id] = Checkpoint(
                checkpoint_id=cp_data["checkpoint_id"],
                tool_calls=[ToolCall(**tc) for tc in cp_data.get("tool_calls", [])],
                artifacts={k: Artifact(**v) for k, v in cp_data.get("artifacts", {}).items()},
                context=cp_data.get("context", ""),
                sub_agents=cp_data.get("sub_agents", {}),
                progress=cp_data.get("progress", 0.0),
                timestamp=cp_data.get("timestamp", 0.0),
            )
        latest = row["latest_checkpoint_id"] or ""
        metadata = SessionMetadata(
            session_id=row["session_id"],
            agent_id=row["agent_id"],
            status=SessionStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            parent_session_id=row["parent_session_id"],
        )
        return Session(
            metadata=metadata,
            checkpoint_strategy=row["checkpoint_strategy"],
            latest_checkpoint_id=latest,
            checkpoints=checkpoints,
        )

    def update_session(self, session: Session) -> None:
        m = session.metadata
        checkpoints_json = {}
        for cp_id, cp in session.checkpoints.items():
            checkpoints_json[cp_id] = {
                "checkpoint_id": cp.checkpoint_id,
                "tool_calls": [tc.__dict__ for tc in cp.tool_calls],
                "artifacts": {k: v.__dict__ for k, v in cp.artifacts.items()},
                "context": cp.context,
                "sub_agents": cp.sub_agents,
                "progress": cp.progress,
                "timestamp": cp.timestamp,
            }
        self.conn.execute(
            """
            UPDATE sessions SET
                status = ?, parent_session_id = ?, checkpoint_strategy = ?,
                latest_checkpoint_id = ?, updated_at = ?, checkpoints_json = ?
            WHERE session_id = ?
            """,
            (
                m.status.value, m.parent_session_id, session.checkpoint_strategy,
                session.latest_checkpoint_id, m.updated_at,
                json.dumps(checkpoints_json), m.session_id,
            ),
        )
        self.conn.commit()

    def get_all_sessions(self) -> List[Session]:
        rows = self.conn.execute("SELECT session_id FROM sessions").fetchall()
        return [self.get_session(r["session_id"]) for r in rows if r]

    def add_checkpoint(self, session_id: str, checkpoint: Checkpoint) -> None:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session.checkpoints[checkpoint.checkpoint_id] = checkpoint
        session.latest_checkpoint_id = checkpoint.checkpoint_id
        self.update_session(session)

    def emit_event(self, event: SessionEvent) -> None:
        self.conn.execute(
            "INSERT INTO events (session_id, type, timestamp, payload_json) VALUES (?, ?, ?, ?)",
            (event.session_id, event.type, event.timestamp, json.dumps(event.payload)),
        )
        self.conn.commit()

    def get_events(self, session_id: str, limit: Optional[int] = None) -> List[SessionEvent]:
        sql = "SELECT * FROM events WHERE session_id = ? ORDER BY timestamp DESC"
        params: tuple = (session_id,)
        if limit:
            sql += " LIMIT ?"
            params = (session_id, limit)
        rows = self.conn.execute(sql, params).fetchall()
        return [
            SessionEvent(
                type=r["type"],
                session_id=r["session_id"],
                timestamp=r["timestamp"],
                payload=json.loads(r["payload_json"]),
            )
            for r in rows
        ]

    def close(self) -> None:
        self.conn.close()


# ---------------------------------------------------------------------------
# Session Manager
# ---------------------------------------------------------------------------

class SessionManager:
    """
    High-level API for managing agent sessions.

    Responsibilities:
    - Create / resume / cancel sessions
    - Checkpoint creation and pruning
    - Event emission for observability
    - Sub-agent session tracking
    """

    def __init__(
        self,
        store: Optional[SessionStore] = None,
        checkpoint_strategy: str = "fine",
        on_event: Optional[Callable[[SessionEvent], None]] = None,
    ):
        self.store = store or SQLiteSessionStore(":memory:")
        self.checkpoint_strategy = checkpoint_strategy
        self.on_event = on_event or (lambda e: None)

    def create_session(self, agent_id: str, parent_session_id: Optional[str] = None) -> str:
        session_id = str(uuid.uuid4())
        now = datetime.now().timestamp()
        metadata = SessionMetadata(
            session_id=session_id,
            agent_id=agent_id,
            status=SessionStatus.INITIALIZING,
            created_at=now,
            updated_at=now,
            parent_session_id=parent_session_id,
        )
        session = Session(
            metadata=metadata,
            checkpoint_strategy=self.checkpoint_strategy,
            latest_checkpoint_id="",
            checkpoints={},
        )
        self.store.create_session(session)
        self._emit(SessionEvent(
            type="session.started",
            session_id=session_id,
            payload={"agent_id": agent_id, "parent_session_id": parent_session_id},
        ))
        return session_id

    def update_status(self, session_id: str, status: SessionStatus) -> None:
        session = self.store.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session.metadata.status = status
        session.metadata.updated_at = datetime.now().timestamp()
        self.store.update_session(session)

        event_type = {
            SessionStatus.COMPLETED: "session.completed",
            SessionStatus.FAILED: "session.failed",
            SessionStatus.CANCELLED: "session.cancelled",
        }.get(status)
        if event_type:
            self._emit(SessionEvent(type=event_type, session_id=session_id))

    def checkpoint(self, session_id: str, checkpoint: Checkpoint) -> str:
        if not checkpoint.checkpoint_id:
            checkpoint.checkpoint_id = str(uuid.uuid4())
        self.store.add_checkpoint(session_id, checkpoint)
        self._emit(SessionEvent(
            type="session.checkpoint",
            session_id=session_id,
            payload={"checkpoint_id": checkpoint.checkpoint_id, "progress": checkpoint.progress},
        ))
        return checkpoint.checkpoint_id

    # TODO(human): Implement session resumption logic
    #
    # This is the critical piece — how do you restart a failed agent?
    #
    # Consider:
    # 1. How do you reconstruct agent state from the latest checkpoint?
    # 2. Should you replay tool calls? Skip completed ones? Re-run everything?
    # 3. How do you handle sub-agents? Resume them too? Skip completed ones?
    # 4. What should the return type be? The checkpoint? Instructions for the agent?
    #
    # Guidance:
    # - The caller (agent runtime) needs enough info to restart execution
    # - Think about what an agent needs to "pick up where it left off"
    # - Consider returning: { checkpoint, pending_tool_calls, pending_sub_agents }
    def resume_session(self, session_id: str) -> ResumeResult:
        """
        Resume a failed or paused session from its latest checkpoint.

        Returns everything the agent runtime needs to restart execution.
        """
        session = self.store.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        latest = session.checkpoints.get(session.latest_checkpoint_id)
        if not latest:
            raise ValueError(f"No checkpoint found for session {session_id}")

        # TODO(human): Compute pending work from the latest checkpoint
        # pending_tool_calls = ...
        # pending_sub_agents = ...
        pass

    def cancel_session(self, session_id: str) -> None:
        self.update_status(session_id, SessionStatus.CANCELLED)

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.store.get_session(session_id)

    def get_events(self, session_id: str, limit: Optional[int] = None) -> List[SessionEvent]:
        return self.store.get_events(session_id, limit)

    def close(self) -> None:
        self.store.close()

    def _emit(self, event: SessionEvent) -> None:
        self.store.emit_event(event)
        self.on_event(event)
