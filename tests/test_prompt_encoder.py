"""Tests for the PromptEncoder and its integration with the generation pipeline."""

from __future__ import annotations

import pytest

from src.hart_morphosis.core import PromptEncoder, GenerationParams


class TestPromptEncoder:
    """Unit tests for the PromptEncoder keyword-matching logic."""

    def setup_method(self):
        self.encoder = PromptEncoder()

    # ------------------------------------------------------------------
    # Default (no keyword matches)
    # ------------------------------------------------------------------

    def test_default_params_returned_for_empty_keywords(self):
        params = self.encoder.encode("xyz 123")
        defaults = GenerationParams()
        assert params.morphogenesis.steps == defaults.morphogenesis.steps
        assert params.morphogenesis.grid_size == defaults.morphogenesis.grid_size
        assert params.cosmological.n_clusters == defaults.cosmological.n_clusters
        assert params.seed_offset == 0

    # ------------------------------------------------------------------
    # Individual keyword categories
    # ------------------------------------------------------------------

    def test_organic_keywords_increase_steps(self):
        params = self.encoder.encode("a forest of trees")
        assert params.morphogenesis.steps > GenerationParams().morphogenesis.steps

    def test_cosmic_keywords_increase_clusters(self):
        params = self.encoder.encode("a galaxy of stars")
        assert params.cosmological.n_clusters > GenerationParams().cosmological.n_clusters

    def test_water_keywords_increase_diffusion(self):
        params = self.encoder.encode("ocean waves")
        assert params.morphogenesis.diffusion_rate > GenerationParams().morphogenesis.diffusion_rate

    def test_face_keywords_increase_grid_size(self):
        params = self.encoder.encode("portrait of a human face")
        assert params.morphogenesis.grid_size[0] > GenerationParams().morphogenesis.grid_size[0]

    def test_abstract_keywords_increase_d_model(self):
        params = self.encoder.encode("abstract fractal mandala")
        assert params.d_model > GenerationParams().d_model

    def test_detailed_keywords_increase_steps(self):
        params = self.encoder.encode("a detailed landscape")
        assert params.morphogenesis.steps >= 100

    def test_minimal_keywords_decrease_steps(self):
        params = self.encoder.encode("minimal clean design")
        assert params.morphogenesis.steps < GenerationParams().morphogenesis.steps

    # ------------------------------------------------------------------
    # Palette / colour seed offsets
    # ------------------------------------------------------------------

    def test_palette_keyword_adds_seed_offset(self):
        params = self.encoder.encode("a warm sunset")
        assert params.seed_offset > 0

    def test_multiple_palette_keywords_accumulate(self):
        params_single = self.encoder.encode("a warm landscape")
        params_double = self.encoder.encode("a warm blue ocean")
        assert params_double.seed_offset > params_single.seed_offset

    # ------------------------------------------------------------------
    # Grid/resolution sync
    # ------------------------------------------------------------------

    def test_grid_size_and_base_resolution_stay_in_sync(self):
        params = self.encoder.encode("portrait of a human face")
        assert params.morphogenesis.grid_size == params.rendering.base_resolution

    # ------------------------------------------------------------------
    # Case insensitivity
    # ------------------------------------------------------------------

    def test_keyword_matching_is_case_insensitive(self):
        lower = self.encoder.encode("a galaxy")
        upper = self.encoder.encode("A GALAXY")
        assert lower.cosmological.n_clusters == upper.cosmological.n_clusters

    # ------------------------------------------------------------------
    # Determinism
    # ------------------------------------------------------------------

    def test_same_prompt_always_returns_same_params(self):
        p1 = self.encoder.encode("a face made of trees under a galaxy")
        p2 = self.encoder.encode("a face made of trees under a galaxy")
        assert p1.morphogenesis.steps == p2.morphogenesis.steps
        assert p1.cosmological.n_clusters == p2.cosmological.n_clusters
        assert p1.seed_offset == p2.seed_offset
