"""Command-line interface for HART-Morphosis."""

from __future__ import annotations

import argparse
import hashlib

import torch

from src.hart_morphosis.core import HART, FractalRenderer, MorphogenesisEngine


def prompt_to_seed(prompt: str) -> int:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def build_image(prompt: str, zoom: int, seed: int | None, output: str) -> None:
    resolved_seed = seed if seed is not None else prompt_to_seed(prompt)
    torch.manual_seed(resolved_seed)

    morpho = MorphogenesisEngine(grid_size=(16, 16))
    pattern = morpho.generate_pattern(steps=50, seed=resolved_seed)

    base_state = pattern.unsqueeze(-1).repeat(1, 1, 16)
    base_state = base_state.unsqueeze(0)

    model = HART(d_model=16, num_layers=4)
    with torch.no_grad():
        refined = model(base_state).squeeze(0)

    renderer = FractalRenderer(base_resolution=(16, 16))
    zoomed = renderer.render_zoom_level(refined, zoom_level=zoom)
    renderer.save_image(zoomed, output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate images with HART-Morphosis")
    parser.add_argument("--prompt", required=True, help="Text prompt to seed generation")
    parser.add_argument("--zoom", type=int, default=1, help="Zoom level for fractal rendering")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for reproducibility")
    parser.add_argument("--output", default="output.png", help="Output image path")
    args = parser.parse_args()

    build_image(args.prompt, args.zoom, args.seed, args.output)


if __name__ == "__main__":
    main()
