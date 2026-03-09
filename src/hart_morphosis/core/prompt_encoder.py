"""Prompt encoder that maps text keywords to HART-Morphosis generation parameters.

This module provides a lightweight, rule-based prompt encoding system that
translates natural-language prompts into morphogenesis and rendering parameters.
No neural network or external API is required.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Parameter dataclasses
# ---------------------------------------------------------------------------


@dataclass
class MorphogenesisParams:
    """Parameters for the MorphogenesisEngine."""

    grid_size: Tuple[int, int] = (32, 32)
    steps: int = 50
    # Diffusion rate influences pattern coarseness (0.0 = random, 1.0 = fully diffused)
    diffusion_rate: float = 0.2


@dataclass
class CosmologicalParams:
    """Parameters for the CosmologicalStructureModule."""

    n_clusters: int = 8
    steps: int = 20
    G: float = 1.0


@dataclass
class RenderingParams:
    """Parameters for the FractalRenderer."""

    zoom_level: int = 2
    base_resolution: Tuple[int, int] = (32, 32)


@dataclass
class GenerationParams:
    """Full set of generation parameters derived from a prompt."""

    morphogenesis: MorphogenesisParams = field(default_factory=MorphogenesisParams)
    cosmological: CosmologicalParams = field(default_factory=CosmologicalParams)
    rendering: RenderingParams = field(default_factory=RenderingParams)
    seed_offset: int = 0
    d_model: int = 16
    num_layers: int = 2


# ---------------------------------------------------------------------------
# Keyword → parameter mappings
# ---------------------------------------------------------------------------

# Maps keyword patterns to (attribute_path, value) adjustments.
# Attribute paths use dot notation relative to GenerationParams.
_KEYWORD_RULES: List[Tuple[str, str, object]] = [
    # Organic / natural textures → denser morphogenesis
    (r"\b(tree|forest|leaf|leaves|plant|flower|vine|bark)\b", "morphogenesis.steps", 80),
    (r"\b(tree|forest|leaf|leaves|plant|flower|vine|bark)\b", "morphogenesis.diffusion_rate", 0.15),
    # Cosmic / galactic → more clusters
    (r"\b(galaxy|galaxies|cosmic|cosmos|nebula|star|stars|universe|space)\b", "cosmological.n_clusters", 16),
    (r"\b(galaxy|galaxies|cosmic|cosmos|nebula|star|stars|universe|space)\b", "cosmological.G", 2.0),
    # Water / fluid → higher diffusion
    (r"\b(water|ocean|sea|river|lake|wave|waves|fluid|liquid)\b", "morphogenesis.diffusion_rate", 0.35),
    (r"\b(water|ocean|sea|river|lake|wave|waves|fluid|liquid)\b", "morphogenesis.steps", 60),
    # Portrait / face → finer grid
    (r"\b(face|portrait|person|human|eye|eyes|skin)\b", "morphogenesis.grid_size", (48, 48)),
    (r"\b(face|portrait|person|human|eye|eyes|skin)\b", "rendering.base_resolution", (48, 48)),
    (r"\b(face|portrait|person|human|eye|eyes|skin)\b", "num_layers", 3),
    # Abstract / psychedelic → more layers
    (r"\b(abstract|psychedelic|fractal|geometric|pattern|mandala)\b", "num_layers", 4),
    (r"\b(abstract|psychedelic|fractal|geometric|pattern|mandala)\b", "d_model", 32),
    # High detail / detailed
    (r"\b(detailed|intricate|complex|elaborate|fine)\b", "morphogenesis.steps", 100),
    (r"\b(detailed|intricate|complex|elaborate|fine)\b", "morphogenesis.grid_size", (48, 48)),
    # Zoom / wide / large
    (r"\b(zoom|zoomed|close.?up|macro)\b", "rendering.zoom_level", 4),
    (r"\b(wide|panoramic|landscape|vast)\b", "rendering.zoom_level", 2),
    # Minimal / simple
    (r"\b(minimal|simple|clean|sparse)\b", "morphogenesis.steps", 20),
    (r"\b(minimal|simple|clean|sparse)\b", "cosmological.n_clusters", 4),
]

# Palette keywords inject a seed offset so different colour families emerge
_PALETTE_SEEDS: Dict[str, int] = {
    "warm": 1,
    "cold": 2,
    "blue": 3,
    "red": 4,
    "green": 5,
    "gold": 6,
    "purple": 7,
    "dark": 8,
    "bright": 9,
    "monochrome": 10,
    "rainbow": 11,
}


# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------


class PromptEncoder:
    """Rule-based encoder that converts a text prompt to GenerationParams.

    The encoder applies keyword rules in the order they are defined, so later
    rules for the same attribute override earlier ones.  This keeps the
    implementation predictable and fully deterministic.

    Example::

        encoder = PromptEncoder()
        params = encoder.encode("a detailed face made of trees under a galaxy")
        print(params.morphogenesis.steps)   # 100 (detailed rule wins)
        print(params.cosmological.n_clusters)  # 16 (galaxy rule)
    """

    def encode(self, prompt: str) -> GenerationParams:
        """Encode a natural-language prompt into GenerationParams.

        Args:
            prompt: Natural-language description of the desired image.

        Returns:
            GenerationParams populated from keyword matching.
        """
        params = GenerationParams()
        lowered = prompt.lower()

        for pattern, attr_path, value in _KEYWORD_RULES:
            if re.search(pattern, lowered):
                self._set_nested(params, attr_path, value)

        # Palette / colour seed offset
        for keyword, offset in _PALETTE_SEEDS.items():
            if keyword in lowered:
                params.seed_offset += offset

        # Keep grid_size and base_resolution in sync if only one was modified
        if params.morphogenesis.grid_size != params.rendering.base_resolution:
            # Use the larger of the two
            h = max(params.morphogenesis.grid_size[0], params.rendering.base_resolution[0])
            w = max(params.morphogenesis.grid_size[1], params.rendering.base_resolution[1])
            params.morphogenesis.grid_size = (h, w)
            params.rendering.base_resolution = (h, w)

        return params

    @staticmethod
    def _set_nested(obj: object, attr_path: str, value: object) -> None:
        """Set a nested attribute specified by a dot-separated path."""
        parts = attr_path.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)
