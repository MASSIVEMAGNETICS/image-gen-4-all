"""Streamlit web UI for HART-Morphosis."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from PIL import Image
import streamlit as st
import torch

from src.hart_morphosis.core import HART, FractalRenderer, MorphogenesisEngine


def prompt_to_seed(prompt: str) -> int:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


@st.cache_data(show_spinner=False)
def generate_image(prompt: str, zoom: int, seed: int | None) -> Image.Image:
    resolved_seed = seed if seed is not None else prompt_to_seed(prompt)
    torch.manual_seed(resolved_seed)

    morpho = MorphogenesisEngine(grid_size=(16, 16))
    pattern = morpho.generate_pattern(steps=50, seed=resolved_seed)
    base_state = pattern.unsqueeze(-1).repeat(1, 1, 16).unsqueeze(0)

    model = HART(d_model=16, num_layers=4)
    with torch.no_grad():
        refined = model(base_state).squeeze(0)

    renderer = FractalRenderer(base_resolution=(16, 16))
    zoomed = renderer.render_zoom_level(refined, zoom_level=zoom)
    return renderer.tensor_to_pil(zoomed)


def app() -> None:
    st.title("HART-Morphosis Live Demo")
    st.caption("Nature doesn't store images — it grows them.")

    prompt = st.text_input("Prompt", value="a face made of trees under a galaxy")
    zoom = st.slider("Zoom level", min_value=1, max_value=6, value=2)
    seed_input = st.text_input("Seed (optional)", value="")

    seed = None
    seed_error = False
    if seed_input.strip():
        try:
            seed = int(seed_input.strip())
        except ValueError:
            seed_error = True
            st.error("Seed must be an integer.")

    if st.button("Generate"):
        if seed_error:
            return
        image = generate_image(prompt, zoom, seed)
        st.image(image, caption=f"Zoom level {zoom}")


if __name__ == "__main__":
    app()
