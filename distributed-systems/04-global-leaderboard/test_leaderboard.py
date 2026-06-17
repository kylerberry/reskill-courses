"""
Scaffolded tests for Global Leaderboard Service.

Fill in the assertions during the red-tests step.
"""

import pytest
from leaderboard import LeaderboardService, TopNCache


@pytest.fixture
def leaderboard():
    return LeaderboardService(top_n=100)


@pytest.fixture
def small_leaderboard():
    return LeaderboardService(top_n=5)


@pytest.fixture
def cache():
    return TopNCache(n=5)


# ---------------------------------------------------------------------------
# Score update tests
# ---------------------------------------------------------------------------

class TestScoreUpdates:
    def test_update_score_stores_player(self, leaderboard):
        pytest.skip("TODO(human): Assert that update_score makes the player rankable")

    def test_update_score_replaces_previous_score(self, leaderboard):
        pytest.skip("TODO(human): Assert that updating the same player replaces their score")

    def test_update_score_batch_accepts_multiple_players(self, leaderboard):
        pytest.skip("TODO(human): Assert that batch_update stores all players")

    def test_update_score_with_tie_both_players_stored(self, leaderboard):
        pytest.skip("TODO(human): Assert that tied scores are both stored with deterministic ordering")


# ---------------------------------------------------------------------------
# Rank query tests
# ---------------------------------------------------------------------------

class TestRankQueries:
    def test_get_rank_returns_1_for_highest_score(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that highest score gets rank 1")

    def test_get_rank_returns_correct_position(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that get_rank returns correct 1-indexed position")

    def test_get_rank_returns_none_for_unknown_player(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that unknown player returns None")

    def test_get_rank_tied_scores_deterministic(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that ties are broken by player_id ascending")


# ---------------------------------------------------------------------------
# Top-N list tests
# ---------------------------------------------------------------------------

class TestTopNList:
    def test_get_top_n_returns_correct_count(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that get_top_n returns exactly n entries")

    def test_get_top_n_ordered_descending(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that top-n is ordered by score descending")

    def test_get_top_n_with_fewer_players_than_n(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that get_top_n returns all players when fewer than n exist")

    def test_get_top_n_returns_player_id_and_score(self, small_leaderboard):
        pytest.skip("TODO(human): Assert that each entry has player_id and score keys")


# ---------------------------------------------------------------------------
# Cache tests
# ---------------------------------------------------------------------------

class TestTopNCache:
    def test_cache_miss_on_empty_cache(self, cache):
        pytest.skip("TODO(human): Assert that get() returns None on empty cache")

    def test_cache_hit_after_set(self, cache):
        pytest.skip("TODO(human): Assert that get() returns data after set()")

    def test_cache_invalidated_when_score_beats_threshold(self, cache):
        pytest.skip("TODO(human): Assert that should_invalidate returns True for score > threshold")

    def test_cache_not_invalidated_when_score_below_threshold(self, cache):
        pytest.skip("TODO(human): Assert that should_invalidate returns False for score < threshold")

    def test_cache_threshold_updates_after_set(self, cache):
        pytest.skip("TODO(human): Assert that threshold equals minimum score after set()")
