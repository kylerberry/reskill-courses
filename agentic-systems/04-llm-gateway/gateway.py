"""
Multi-Tenant LLM Gateway

Handles: routing, semantic caching, budget enforcement, provider failover.

Architecture:
- ProviderRouter: selects candidate models given tenant config + request capabilities
- SemanticCache: embedding-based cache with capability fingerprinting
- BudgetEnforcer: per-tenant monthly spend tracking
- LLMGateway: orchestrates the full flow
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class Provider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"


class CapabilityFlag(Enum):
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    JSON_MODE = "json_mode"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"


@dataclass
class ModelSpec:
    provider: Provider
    model_id: str
    cost_per_input_token: float
    cost_per_output_token: float
    max_context_tokens: int
    avg_latency_ms: int
    capabilities: Set[CapabilityFlag] = field(default_factory=set)


@dataclass
class TenantConfig:
    tenant_id: str
    team_name: str
    monthly_budget_usd: float
    preferred_providers: List[Provider]
    required_capabilities: Set[CapabilityFlag]
    latency_sla_ms: int
    allow_semantic_cache: bool = True
    cache_similarity_threshold: float = 0.92


@dataclass
class BudgetState:
    tenant_id: str
    month_key: str
    spent_usd: float = 0.0
    last_updated: float = field(default_factory=time.time)

    def remaining(self, cap: float) -> float:
        return max(0.0, cap - self.spent_usd)

    def utilization_pct(self, cap: float) -> float:
        return (self.spent_usd / cap) * 100 if cap > 0 else 0


@dataclass
class LLMRequest:
    tenant_id: str
    messages: List[Dict[str, str]]
    required_capabilities: Set[CapabilityFlag] = field(default_factory=set)
    max_tokens: int = 1024
    request_id: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class LLMResponse:
    request_id: str
    content: str
    provider: Provider
    model_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    cache_hit: bool = False
    cache_similarity: float = 0.0


# ---------------------------------------------------------------------------
# Provider Catalog
# ---------------------------------------------------------------------------

PROVIDER_CATALOG: List[ModelSpec] = [
    ModelSpec(
        provider=Provider.ANTHROPIC,
        model_id="claude-sonnet-4-6",
        cost_per_input_token=0.000003,
        cost_per_output_token=0.000015,
        max_context_tokens=200_000,
        avg_latency_ms=800,
        capabilities={
            CapabilityFlag.FUNCTION_CALLING,
            CapabilityFlag.VISION,
            CapabilityFlag.JSON_MODE,
            CapabilityFlag.STREAMING,
            CapabilityFlag.LONG_CONTEXT,
        },
    ),
    ModelSpec(
        provider=Provider.OPENAI,
        model_id="gpt-4o",
        cost_per_input_token=0.0000025,
        cost_per_output_token=0.000010,
        max_context_tokens=128_000,
        avg_latency_ms=600,
        capabilities={
            CapabilityFlag.FUNCTION_CALLING,
            CapabilityFlag.VISION,
            CapabilityFlag.JSON_MODE,
            CapabilityFlag.STREAMING,
        },
    ),
    ModelSpec(
        provider=Provider.AZURE_OPENAI,
        model_id="gpt-4o",
        cost_per_input_token=0.0000025,
        cost_per_output_token=0.000010,
        max_context_tokens=128_000,
        avg_latency_ms=500,
        capabilities={
            CapabilityFlag.FUNCTION_CALLING,
            CapabilityFlag.JSON_MODE,
            CapabilityFlag.STREAMING,
        },
    ),
]


# ---------------------------------------------------------------------------
# Semantic Cache
# ---------------------------------------------------------------------------

class SemanticCache:
    """
    Embedding-based cache. Stores (embedding, response) pairs.
    Real impl would use pgvector or Qdrant; this uses in-memory cosine sim.
    """

    def __init__(self):
        # store: (embedding, capability_fingerprint, response)
        self._store: List[tuple[List[float], str, LLMResponse]] = []

    def _capability_fingerprint(self, capabilities: Set[CapabilityFlag]) -> str:
        # TODO(human): compute a stable string fingerprint from a set of CapabilityFlags
        # Must be order-independent (same set -> same fingerprint regardless of iteration order)
        # Hint: frozenset is hashable; consider sorting + joining flag names
        pass

    def _embed(self, text: str) -> List[float]:
        """Stub: replace with real embedding API call."""
        return [0.0] * 1536

    def _cosine_sim(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = sum(x ** 2 for x in a) ** 0.5
        mag_b = sum(x ** 2 for x in b) ** 0.5
        return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0

    def lookup(
        self, request: LLMRequest, threshold: float
    ) -> Optional[tuple[LLMResponse, float]]:
        """Return (cached_response, similarity) if above threshold and fingerprint matches."""
        query_text = " ".join(m["content"] for m in request.messages)
        query_emb = self._embed(query_text)
        query_fp = self._capability_fingerprint(request.required_capabilities)

        best_sim, best_resp = 0.0, None
        for stored_emb, stored_fp, stored_resp in self._store:
            if stored_fp != query_fp:
                continue
            sim = self._cosine_sim(query_emb, stored_emb)
            if sim > best_sim:
                best_sim, best_resp = sim, stored_resp

        if best_sim >= threshold and best_resp:
            return best_resp, best_sim
        return None

    def store(self, request: LLMRequest, response: LLMResponse) -> None:
        query_text = " ".join(m["content"] for m in request.messages)
        fp = self._capability_fingerprint(request.required_capabilities)
        self._store.append((self._embed(query_text), fp, response))


# ---------------------------------------------------------------------------
# Budget Enforcer
# ---------------------------------------------------------------------------

class BudgetEnforcer:
    """
    Eventual-consistency budget check. State stored in-process (Redis in prod).
    Accepts small overspend window as trade-off for speed.
    """

    def __init__(self, configs: Dict[str, TenantConfig]):
        self._configs = configs
        self._state: Dict[str, BudgetState] = {}

    def _month_key(self) -> str:
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m")

    def _get_state(self, tenant_id: str) -> BudgetState:
        key = f"{tenant_id}:{self._month_key()}"
        if key not in self._state:
            self._state[key] = BudgetState(tenant_id, self._month_key())
        return self._state[key]

    def check_and_reserve(self, tenant_id: str, estimated_cost: float) -> bool:
        """Returns True if spend is within budget (optimistic)."""
        config = self._configs[tenant_id]
        state = self._get_state(tenant_id)
        return state.remaining(config.monthly_budget_usd) >= estimated_cost

    def record_spend(self, tenant_id: str, actual_cost: float) -> None:
        state = self._get_state(tenant_id)
        state.spent_usd += actual_cost
        state.last_updated = time.time()

    def utilization(self, tenant_id: str) -> float:
        config = self._configs[tenant_id]
        state = self._get_state(tenant_id)
        return state.utilization_pct(config.monthly_budget_usd)


# ---------------------------------------------------------------------------
# Provider Router
# ---------------------------------------------------------------------------

class ProviderRouter:
    """
    Selects best ModelSpec for a request given tenant preferences + capabilities.
    """

    def __init__(self, catalog: List[ModelSpec]):
        self._catalog = catalog

    def select_candidates(
        self,
        tenant: TenantConfig,
        request: LLMRequest,
    ) -> List[ModelSpec]:
        """
        TODO(human): Implement candidate selection logic.

        Given tenant config and request, return an ORDERED list of ModelSpec
        candidates -- from most preferred to least preferred fallback.

        Rules to enforce:
        1. Model must have ALL required capabilities (union of tenant + request)
        2. Respect tenant's preferred_providers ordering (preferred first)
        3. Filter out models whose avg_latency_ms exceeds tenant.latency_sla_ms
        4. Return empty list if no candidates qualify

        Returns:
            List[ModelSpec] ordered by preference (best first), or [] if none qualify
        """
        pass


# ---------------------------------------------------------------------------
# LLM Gateway
# ---------------------------------------------------------------------------

class LLMGateway:
    """
    Orchestrates: cache lookup -> budget check -> routing -> provider call -> spend tracking.
    """

    def __init__(self, tenant_configs: List[TenantConfig]):
        self._configs = {t.tenant_id: t for t in tenant_configs}
        self._cache = SemanticCache()
        self._budget = BudgetEnforcer(self._configs)
        self._router = ProviderRouter(PROVIDER_CATALOG)

    def _estimate_cost(self, spec: ModelSpec, request: LLMRequest) -> float:
        input_tokens = sum(len(m["content"].split()) for m in request.messages) * 1.3
        return (
            input_tokens * spec.cost_per_input_token
            + request.max_tokens * spec.cost_per_output_token
        )

    def _call_provider(self, spec: ModelSpec, request: LLMRequest) -> LLMResponse:
        """Stub: real impl calls provider SDK."""
        latency = spec.avg_latency_ms + 50
        input_tokens = sum(len(m["content"].split()) for m in request.messages)
        output_tokens = min(request.max_tokens, 256)
        cost = (
            input_tokens * spec.cost_per_input_token
            + output_tokens * spec.cost_per_output_token
        )
        return LLMResponse(
            request_id=request.request_id or str(uuid.uuid4()),
            content=f"[stub response from {spec.provider.value}/{spec.model_id}]",
            provider=spec.provider,
            model_id=spec.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency,
        )

    def handle(self, request: LLMRequest) -> LLMResponse:
        """
        TODO(human): Implement the full gateway request handler.

        Flow:
        1. Semantic cache lookup (if tenant allows it)
        2. Route to candidates via ProviderRouter
        3. Budget check + failover loop across candidates
        4. Track spend and cache the response

        Key decisions:
        - What should happen when no candidates match the tenant's constraints?
        - What should happen when the budget is exceeded?
        - How should provider failures be handled -- try next candidate or abort?
        """
        pass
