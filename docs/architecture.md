# Architecture Overview

HART-Morphosis is built as a **modular, layered system** that simulates natural processes instead of memorizing data.

## 🔄 Pipeline

```
[Text Prompt]
        ↓
[Seed Generator] → Creates 16×16 latent grid from prompt embedding
        ↓
[Morphogenesis Engine] → Grows textures via reaction-diffusion (Turing patterns)
        ↓
[Cosmological Module] → Clusters features via gravitational attraction (N-body)
        ↓
[HART Layer] → Refines structure using morpho-cosmo attention
        ↓
[Fractal Renderer] → Renders infinite resolution on-demand
        ↓
[Output Image] → Saved or streamed
```

## 🧩 Components

### 1. **HART (Hybrid Autoregressive Transformer)**
- Operates on 2D grid (not tokens)
- Two attention heads:
  - **Morpho-Attention**: Measures local morphogen concentration gradients
  - **Cosmo-Attention**: Computes gravitational attraction between semantic clusters
- Lightweight: Only 4–6 layers, d_model=16

### 2. **Morphogenesis Engine**
- Simulates **Gray-Scott reaction-diffusion**
- Two morphogens: Activator (A), Inhibitor (B)
- Generates:
  - Spots, stripes, labyrinthine patterns
  - Veins, tree bark, skin textures

### 3. **Cosmological Structure Module**
- Simulates **gravitational clustering** of feature centers
- Each feature (eye, mountain, galaxy) has “mass” = semantic importance
- Uses simplified N-body physics:
  ```
  F = G * (m1 * m2) / r²
  ```
- Creates cosmic web structure: filaments, voids, halos

### 4. **Fractal Renderer**
- Stores only: seed + rules (≤5KB)
- Renders at any resolution by **recursively applying rules**
- Zoom level `n` → 2ⁿ× resolution
- No interpolation artifacts — only *emergent detail*

## 📦 Output
- **File**: PNG, 8-bit RGB
- **Memory**: Constant (5KB) regardless of output size
- **Speed**: 1–3s on CPU (iPhone 14, Raspberry Pi 5)
