# API Reference

## Core Classes

### `HART(d_model=16, nhead=4, num_layers=6)`
**Purpose**: Hybrid Autoregressive Transformer core.

```python
from src.hart_morphosis.core import HART

model = HART(d_model=16, num_layers=4)
input = torch.randn(1, 16, 16, 16)  # [batch, height, width, d_model]
output = model(input)  # [1, 16, 16, 3] RGB
```

### `MorphogenesisEngine(grid_size=(64,64), device='cpu')`
**Purpose**: Generates biological textures via reaction-diffusion.

```python
from src.hart_morphosis.core import MorphogenesisEngine

engine = MorphogenesisEngine(grid_size=(16, 16))
pattern = engine.generate_pattern(steps=50, seed=42)
# Returns: torch.Tensor [16, 16]
```

### `CosmologicalStructureModule(grid_size=(64,64), G=1.0, device='cpu')`
**Purpose**: Simulates gravitational clustering of semantic features.

```python
from src.hart_morphosis.core import CosmologicalStructureModule

module = CosmologicalStructureModule()
trajectory = module.simulate_clustering(n_clusters=8, steps=20, seed=42)
# Returns: List[torch.Tensor] — positions over time
```

### `FractalRenderer(base_resolution=(16,16))`
**Purpose**: Renders images at any zoom level.

```python
from src.hart_morphosis.core import FractalRenderer

renderer = FractalRenderer()
zoomed = renderer.render_zoom_level(base_grid, zoom_level=4)
renderer.save_image(zoomed, "output.png")
pil_img = renderer.tensor_to_pil(zoomed)
```

## CLI Usage

```bash
python -m src.hart_morphosis.cli.main \
  --prompt "a face made of trees under a galaxy" \
  --zoom 4 \
  --seed 42 \
  --output "result.png"
```

## Web UI

Launch with:

```bash
cd web_ui
streamlit run app.py
```

Access at `http://localhost:8501`
