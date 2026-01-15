# Examples

## Example 1: Simple Face in Forest

```python
from src.hart_morphosis.core import HART, MorphogenesisEngine, CosmologicalStructureModule, FractalRenderer

# Initialize
hart = HART(d_model=16, num_layers=4)
morpho = MorphogenesisEngine(grid_size=(16,16))
cosmo = CosmologicalStructureModule(grid_size=(16,16))
renderer = FractalRenderer()

# Generate
morpho_pattern = morpho.generate_pattern(steps=50, seed=42)
trajectory = cosmo.simulate_clustering(n_clusters=8, steps=20, seed=42)

# Combine into HART input
base_state = morpho_pattern.unsqueeze(0).unsqueeze(-1).repeat(1, 1, 16)
base_state = base_state.unsqueeze(0)

# Refine with HART
with torch.no_grad():
    refined = hart(base_state).squeeze(0)

# Render at 128x128
final = renderer.render_zoom_level(refined.squeeze().cpu(), zoom_level=4)
renderer.save_image(final, "face_in_forest.png")
```

## Example 2: Cosmic Portrait (Web UI)

In the **web UI**, enter:
> **Prompt**: `"a woman's face, hair made of galaxy filaments, eyes as nebulae"`

→ Generates a portrait where:
- Skin = Turing pattern texture
- Hair = L-system branching (simulated via morpho gradients)
- Eyes = gravitational clusters (high-mass features)
- Background = cosmological voids and filaments

## Example 3: Fractal Zoom

```python
for z in [1, 2, 4, 8]:
    img = renderer.render_zoom_level(refined, z)
    renderer.save_image(img, f"zoom_{z}.png")
```

Each image has **2× more pixels**, but **no blur** — new detail emerges organically.

## Example 4: Custom Rules

Edit `src/hart_morphosis/models/rulesets/default.json` to change:
- Diffusion rates
- Reaction constants
- Gravitational strength
- Cluster mass scaling

No retraining needed.
