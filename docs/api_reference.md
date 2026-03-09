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

### `PromptEncoder()`
**Purpose**: Rule-based encoder that converts a text prompt to `GenerationParams`.
Maps natural-language keywords (organic, cosmic, water, face, abstract, detail,
palette colours) to morphogenesis, cosmological, and rendering parameters.
Fully deterministic — no neural network or external API required.

```python
from src.hart_morphosis.core import PromptEncoder

encoder = PromptEncoder()
params = encoder.encode("a detailed face made of trees under a galaxy")

print(params.morphogenesis.steps)       # 100  (detailed rule)
print(params.cosmological.n_clusters)   # 16   (galaxy rule)
print(params.d_model)                   # 16
print(params.seed_offset)               # 0  (no colour keyword)
```

`GenerationParams` fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `morphogenesis.grid_size` | `(int, int)` | `(32, 32)` | Reaction-diffusion grid |
| `morphogenesis.steps` | `int` | `50` | Diffusion iterations |
| `morphogenesis.diffusion_rate` | `float` | `0.2` | Laplacian weight |
| `cosmological.n_clusters` | `int` | `8` | Gravitational cluster count |
| `cosmological.G` | `float` | `1.0` | Gravitational constant |
| `rendering.zoom_level` | `int` | `2` | Default fractal zoom |
| `rendering.base_resolution` | `(int, int)` | `(32, 32)` | Base render resolution |
| `d_model` | `int` | `16` | HART channel width |
| `num_layers` | `int` | `2` | HART layer count |
| `seed_offset` | `int` | `0` | Added to numeric seed |

---

## REST API (FastAPI backend)

Start the server:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### `GET /health`

Liveness probe.

**Response** `200 OK`:
```json
{ "status": "ok", "version": "1.0.0" }
```

### `POST /generate`

Generate an image from a text prompt.

**Request body** (JSON):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | `string` | ✅ | Text description (1–500 chars) |
| `zoom` | `integer` | ✅ | Fractal zoom level (1–6) |
| `seed` | `integer \| null` | — | Optional RNG seed |

**Response** `200 OK`:

| Field | Type | Description |
|-------|------|-------------|
| `image_b64` | `string` | Base-64 encoded PNG |
| `width` | `int` | Image width in pixels |
| `height` | `int` | Image height in pixels |
| `seed` | `int` | Resolved seed used |
| `prompt` | `string` | Echo of input prompt |
| `latency_ms` | `float` | Server-side generation time |

**Error responses**: `422 Unprocessable Entity` for validation failures,
`429 Too Many Requests` when rate limit is exceeded.

**Environment variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_PER_MINUTE` | `30` | Max requests per client IP per minute |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated allowed CORS origins |

---

## CLI Usage

```bash
python -m src.hart_morphosis.cli.main \
  --prompt "a face made of trees under a galaxy" \
  --zoom 4 \
  --seed 42 \
  --output "result.png"
```

## Web UI (Streamlit)

Launch the legacy Streamlit prototype:

```bash
cd web_ui
streamlit run app.py
```

Access at `http://localhost:8501`

## Next.js UI

The enterprise UI lives in `ui/`. It communicates with the FastAPI backend.

```bash
# 1. Start the API backend
uvicorn api.main:app --port 8000 --reload

# 2. Start the Next.js dev server
cd ui
npm install
npm run dev
```

Access at `http://localhost:3000`

For production:

```bash
cd ui
npm run build
npm start
```

