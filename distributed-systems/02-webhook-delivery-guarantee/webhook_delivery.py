"""
Webhook Delivery Guarantee Layer

Components:
- BackoffStrategy: exponential backoff with full jitter
- CircuitBreaker: per-endpoint open/closed/half-open state machine
- DeliveryStateMachine: retry lifecycle (pending -> in-flight -> delivered / dead-letter)
- DeadLetterStore: final resting place for exhausted deliveries
- WebhookDispatcher: fan-out coordinator with circuit-aware delivery
"""

from __future__ import annotations

import asyncio
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Protocol


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class DeliveryStatus(Enum):
    PENDING = "pending"
    IN_FLIGHT = "in_flight"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class WebhookEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    payload: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class DeliveryAttempt:
    attempt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str = ""
    subscriber_id: str = ""
    attempt_number: int = 0
    status: DeliveryStatus = DeliveryStatus.PENDING
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    http_status_code: Optional[int] = None
    error_message: Optional[str] = None
    next_retry_at: Optional[datetime] = None


@dataclass
class SubscriberState:
    subscriber_id: str = ""
    endpoint_url: str = ""
    max_retries: int = 5
    retry_budget_seconds: int = 86400
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    circuit_opened_at: Optional[datetime] = None
    circuit_half_open_at: Optional[datetime] = None
    total_deliveries: int = 0
    total_failures: int = 0


# ---------------------------------------------------------------------------
# Backoff Strategy
# ---------------------------------------------------------------------------

class BackoffStrategy(Protocol):
    def delay_seconds(self, attempt: int) -> float:
        ...


class ExponentialBackoffWithJitter:
    """
    Full jitter: delay = random(0, min(cap, base * 2^attempt))
    Prevents thundering herd when many subscribers retry simultaneously.
    """

    def __init__(self, base: float = 1.0, cap: float = 3600.0):
        self.base = base
        self.cap = cap

    def delay_seconds(self, attempt: int) -> float:
        """
        TODO(human): Implement retry timing with capped exponential backoff and jitter to avoid synchronized retries.

        Formula: random(0, min(cap, base * 2^attempt))
        Return a float representing seconds to wait before next attempt.
        Make sure attempt=0 still produces a non-zero delay for initial failure.
        """
        pass


class FixedDelay:
    """Simple fixed delay -- useful for testing."""

    def __init__(self, seconds: float = 5.0):
        self.seconds = seconds

    def delay_seconds(self, attempt: int) -> float:
        return self.seconds


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------

class CircuitBreaker:
    """
    Per-endpoint circuit breaker.

    State machine:
        CLOSED -> OPEN   : after `failure_threshold` consecutive failures
        OPEN -> HALF_OPEN: after `cooldown_seconds` have elapsed
        HALF_OPEN -> CLOSED: on first successful probe delivery
        HALF_OPEN -> OPEN  : on probe failure
    """

    def __init__(self, failure_threshold: int = 5, cooldown_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

    def allow_request(self, state: SubscriberState) -> bool:
        """
        TODO(human): Implement circuit breaker state transitions across allow, success, and failure paths.

        Check circuit_state on the SubscriberState object:
        - CLOSED -> always allow
        - OPEN -> check if cooldown has elapsed; if so transition to HALF_OPEN and allow one probe
        - HALF_OPEN -> allow exactly one probe

        Remember to update circuit_half_open_at when transitioning OPEN -> HALF_OPEN.
        """
        pass

    def record_success(self, state: SubscriberState) -> None:
        """
        Learning objective: record success and close or stabilize the circuit when appropriate.

        Reset consecutive_failures, return circuit to CLOSED.
        """
        pass

    def record_failure(self, state: SubscriberState) -> None:
        """
        Learning objective: record failures and open the circuit when threshold is exceeded.

        Increment consecutive_failures.
        If it meets or exceeds failure_threshold: transition to OPEN, set circuit_opened_at.
        If already HALF_OPEN and probe failed: revert to OPEN, reset circuit_opened_at.
        """
        pass


# ---------------------------------------------------------------------------
# Delivery State Machine
# ---------------------------------------------------------------------------

class DeliveryStateMachine:
    """
    Manages state transitions for a DeliveryAttempt.

    Valid transitions:
        PENDING     -> IN_FLIGHT   (dispatch called)
        IN_FLIGHT   -> DELIVERED   (2xx response received)
        IN_FLIGHT   -> FAILED      (non-2xx or timeout)
        FAILED      -> PENDING     (retry scheduled, budget remaining)
        FAILED      -> DEAD_LETTER (budget exhausted)
    """

    def __init__(
        self,
        backoff: Optional[BackoffStrategy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        self.backoff = backoff or ExponentialBackoffWithJitter()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()

    def start_dispatch(self, attempt: DeliveryAttempt) -> None:
        """Transition PENDING -> IN_FLIGHT."""
        if attempt.status != DeliveryStatus.PENDING:
            raise ValueError(f"Cannot dispatch from status {attempt.status}")
        attempt.status = DeliveryStatus.IN_FLIGHT
        attempt.started_at = datetime.now(timezone.utc)

    def record_success(
        self, attempt: DeliveryAttempt, subscriber: SubscriberState, http_status: int
    ) -> None:
        """Transition IN_FLIGHT -> DELIVERED."""
        if attempt.status != DeliveryStatus.IN_FLIGHT:
            raise ValueError(f"Cannot succeed from status {attempt.status}")
        attempt.status = DeliveryStatus.DELIVERED
        attempt.completed_at = datetime.now(timezone.utc)
        attempt.http_status_code = http_status
        subscriber.total_deliveries += 1
        self.circuit_breaker.record_success(subscriber)

    def record_failure(
        self,
        attempt: DeliveryAttempt,
        subscriber: SubscriberState,
        http_status: Optional[int],
        error: str,
    ) -> DeliveryAttempt:
        """
        TODO(human): Implement per-delivery failure handling: retry budget, next-at scheduling, and dead-letter transition.

        Transition IN_FLIGHT -> FAILED, then decide: schedule retry or dead-letter.

        Steps:
          1. Mark current attempt FAILED (set status, completed_at, http_status_code, error_message)
          2. Increment subscriber.total_failures
          3. Call circuit_breaker.record_failure(subscriber)
          4. If attempt.attempt_number < subscriber.max_retries:
               Create and return a new DeliveryAttempt (PENDING, attempt_number+1)
               Calculate next_retry_at using self.backoff.delay_seconds(attempt.attempt_number)
          5. Else: transition current attempt to DEAD_LETTER and return it
        """
        pass


# ---------------------------------------------------------------------------
# Dead Letter Store
# ---------------------------------------------------------------------------

@dataclass
class DeadLetterEntry:
    event: WebhookEvent
    subscriber_id: str
    final_attempt: DeliveryAttempt
    attempt_history: List[DeliveryAttempt]
    dead_lettered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    failure_reason: str = ""


class DeadLetterStore:
    """In-memory dead-letter store. Production: replace with durable queue."""

    def __init__(self):
        self._entries: List[DeadLetterEntry] = []

    def write(self, entry: DeadLetterEntry) -> None:
        self._entries.append(entry)

    def list_for_subscriber(self, subscriber_id: str) -> List[DeadLetterEntry]:
        return [e for e in self._entries if e.subscriber_id == subscriber_id]

    def count(self) -> int:
        return len(self._entries)

    def replay(self, entry: DeadLetterEntry) -> DeliveryAttempt:
        """
        Learning objective: replay dead-letter entries as fresh delivery attempts while preserving auditability.

        Create a fresh PENDING attempt from a dead-letter entry for manual replay.
        Return a new DeliveryAttempt in PENDING status for the same event/subscriber,
        with attempt_number reset to 0 and scheduled_at = now.
        """
        pass


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

class WebhookDispatcher:
    """
    Coordinates fan-out delivery of a single event to multiple subscribers.
    Each subscriber gets an independent DeliveryAttempt with its own retry lifecycle.
    """

    def __init__(
        self,
        state_machine: Optional[DeliveryStateMachine] = None,
        dead_letter_store: Optional[DeadLetterStore] = None,
        concurrency_limit: int = 100,
    ):
        self.state_machine = state_machine or DeliveryStateMachine()
        self.dead_letter_store = dead_letter_store or DeadLetterStore()
        self.concurrency_limit = concurrency_limit
        self._semaphore = asyncio.Semaphore(concurrency_limit)

    async def fan_out(
        self, event: WebhookEvent, subscribers: List[SubscriberState]
    ) -> Dict[str, DeliveryAttempt]:
        """Dispatch event to all subscribers concurrently."""
        tasks = [self._deliver_one(event, sub) for sub in subscribers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            sub.subscriber_id: result
            for sub, result in zip(subscribers, results)
            if not isinstance(result, Exception)
        }

    async def _deliver_one(
        self, event: WebhookEvent, subscriber: SubscriberState
    ) -> DeliveryAttempt:
        """
        TODO(human): Implement one-subscriber delivery orchestration with circuit checks, idempotency, success/failure recording, and dead-letter storage.

        Steps:
          1. Create a DeliveryAttempt in PENDING status
          2. Check circuit breaker -- if OPEN, mark as FAILED and return
          3. Call state_machine.start_dispatch(attempt)
          4. Call the endpoint (via _call_endpoint)
          5. On success: record_success
          6. On failure: record_failure; if dead-lettered, write to DeadLetterStore
          7. Return the attempt
        """
        pass

    async def _call_endpoint(
        self, url: str, event: WebhookEvent
    ) -> tuple[Optional[int], Optional[str]]:
        """Simulate HTTP POST to subscriber endpoint."""
        await asyncio.sleep(0.01)
        return 200, None
