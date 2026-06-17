"""
Global Leaderboard Service

Models the core behavior of a Redis Sorted Set (ZSET):
  - ZADD  -> update_score / batch_update
  - ZRANK -> get_rank  (1-indexed, descending by score, tie-break: lower player_id wins)
  - ZSCORE -> get_score
  - ZREVRANGE -> get_top_n

Uses a TopNCache to keep hot read paths fast.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Top-N Cache
# ---------------------------------------------------------------------------

class TopNCache:
    """
    In-memory cache for the top-N leaderboard entries.

    Tracks a score threshold (the minimum score in the cached top-N) so callers
    can decide whether a new score is high enough to warrant cache invalidation
    without reading the full sorted set.
    """

    def __init__(self, n: int):
        self.n = n
        self.threshold: int | None = None
        self._data: list[dict] | None = None

    def get(self) -> list[dict] | None:
        """Return cached entries, or None on cache miss."""
        return self._data

    def set(self, entries: list[dict]) -> None:
        """
        TODO(human): Implement top-N cache storage, threshold calculation, and invalidation decisions.

        Store entries in self._data and derive self.threshold from the minimum
        score in entries. If entries is empty, threshold should be 0 (any score
        would beat an empty leaderboard).
        """
        pass

    def should_invalidate(self, score: int) -> bool:
        """
        Learning objective: decide whether a write can affect the cached leaderboard window.

        Return True if the cache is empty OR if score strictly beats self.threshold.
        An equal score does NOT invalidate -- ties don't displace existing top-N entries.
        """
        pass


# ---------------------------------------------------------------------------
# Leaderboard Service
# ---------------------------------------------------------------------------

class LeaderboardService:
    def __init__(self, top_n: int = 100):
        self.top_n = top_n
        self._cache = TopNCache(n=top_n)
        # Internal storage: player_id -> score
        self._scores: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def update_score(self, player_id: str, score: int) -> None:
        """Upsert a single player's score and invalidate cache if needed."""
        self._scores[player_id] = score
        if self._cache.should_invalidate(score):
            self._invalidate_cache()

    def batch_update(self, entries: list[tuple[str, int]]) -> None:
        """
        TODO(human): Implement batch score updates with at-most-once cache invalidation.

        Iterate entries, update self._scores for each player, then invalidate
        the cache once if ANY of the new scores beats the current threshold.
        Don't invalidate once per entry -- check after the full batch and
        invalidate at most once.
        """
        pass

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def get_rank(self, player_id: str) -> int | None:
        """
        TODO(human): Implement deterministic global ranking with descending score and stable tie-breaks.

        Rank 1 = highest score. Ties broken by player_id ascending (lower wins).
        Return None if player_id is not in self._scores.
        Otherwise, build the sorted order and return the player's position.
        Hint: sort by (-score, player_id) so that higher scores come first
        and ties are broken lexicographically by player_id.
        """
        pass

    def get_score(self, player_id: str) -> int | None:
        """Return the player's current score, or None if not found."""
        return self._scores.get(player_id)

    def get_top_n(self, n: int | None = None) -> list[dict]:
        """
        TODO(human): Implement top-N reads that use and refresh the cache consistently.

        Uses n if provided, otherwise falls back to self.top_n.
        Checks the cache first; on miss, computes from self._scores and
        populates the cache.

        Check self._cache.get() first. If it returns data, return it.
        On cache miss, sort self._scores by (-score, player_id), slice to n
        entries, build the list of dicts, call self._cache.set() with the
        result, then return it.
        """
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _invalidate_cache(self) -> None:
        """Clear and recompute the top-N cache."""
        top = sorted(self._scores.items(), key=lambda kv: (-kv[1], kv[0]))
        entries = [{"player_id": pid, "score": s} for pid, s in top[: self.top_n]]
        self._cache.set(entries)
