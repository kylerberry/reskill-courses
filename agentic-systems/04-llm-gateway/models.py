"""
Data models for the Multi-Tenant LLM Gateway.

These dataclasses define the domain vocabulary. They are used by both the
starter (gateway.py) and the test suite. Do not modify them.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class Provider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"


class CapabilityFlag(Enum):
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    JSON_MODE = "json_mode"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"  # >100k tokens


@dataclass
class ModelSpec:
    provider: Provider
    model_id: str
    cost_per_input_token: float   # USD per token
    cost_per_output_token: float
    max_context_tokens: int
    avg_latency_ms: int
    capabilities: set[CapabilityFlag] = field(default_factory=set)


@dataclass
class TenantConfig:
    tenant_id: str
    team_name: str
    monthly_budget_usd: float
    preferred_providers: list[Provider]         # ordered preference
    required_capabilities: set[CapabilityFlag]  # must-have for failover eligibility
    latency_sla_ms: int                         # max acceptable p95 latency
    allow_semantic_cache: bool = True
    cache_similarity_threshold: float = 0.92    # cosine similarity cutoff


@dataclass
class BudgetState:
    tenant_id: str
    month_key: str                  # "2026-05"
    spent_usd: float = 0.0
    last_updated: float = field(default_factory=time.time)

    def remaining(self, cap: float) -> float:
        return max(0.0, cap - self.spent_usd)

    def utilization_pct(self, cap: float) -> float:
        return (self.spent_usd / cap) * 100 if cap > 0 else 0


@dataclass
class LLMRequest:
    tenant_id: str
    messages: list[dict]
    required_capabilities: set[CapabilityFlag] = field(default_factory=set)
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
