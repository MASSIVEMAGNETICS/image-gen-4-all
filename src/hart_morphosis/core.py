"""Core HART-Morphosis primitives."""

from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
from PIL import Image
import torch
from torch import nn
from torch.nn import functional as F


class HART(nn.Module):
    """Hybrid Autoregressive Transformer (minimal reference implementation)."""

    def __init__(self, d_model: int = 16, nhead: int = 4, num_layers: int = 6) -> None:
        super().__init__()
        if d_model % nhead != 0:
            raise ValueError("d_model must be divisible by nhead.")
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.proj = nn.Linear(d_model, 3)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 4:
            raise ValueError("Expected input with shape [batch, height, width, channels].")
        batch, height, width, channels = x.shape
        x = self.encoder(x.reshape(batch, height * width, channels))
        x = x.reshape(batch, height, width, channels)
        return torch.sigmoid(self.proj(x))


class MorphogenesisEngine:
    """Generates reaction-diffusion inspired patterns."""

    def __init__(self, grid_size: Tuple[int, int] = (64, 64), device: str = "cpu") -> None:
        self.grid_size = tuple(grid_size)
        self.device = torch.device(device)
        self._kernel = torch.tensor(
            [
                [0.05, 0.2, 0.05],
                [0.2, -1.0, 0.2],
                [0.05, 0.2, 0.05],
            ],
            dtype=torch.float32,
            device=self.device,
        ).view(1, 1, 3, 3)

    def generate_pattern(self, steps: int = 50, seed: int | None = None) -> torch.Tensor:
        if seed is not None:
            torch.manual_seed(seed)
        pattern = torch.rand(self.grid_size, device=self.device)
        for _ in range(steps):
            laplacian = F.conv2d(pattern[None, None, ...], self._kernel, padding=1)
            pattern = (pattern + 0.2 * laplacian.squeeze(0).squeeze(0)).clamp(0, 1)
        return pattern


class CosmologicalStructureModule:
    """Simulates simplified gravitational clustering of features."""

    def __init__(self, grid_size: Tuple[int, int] = (64, 64), G: float = 1.0, device: str = "cpu") -> None:
        self.grid_size = tuple(grid_size)
        self.G = G
        self.device = torch.device(device)

    def simulate_clustering(
        self, n_clusters: int = 8, steps: int = 20, seed: int | None = None
    ) -> List[torch.Tensor]:
        if seed is not None:
            torch.manual_seed(seed)
        positions = torch.rand(n_clusters, 2, device=self.device)
        trajectory = [positions.clone()]
        for _ in range(steps):
            diff = positions[:, None, :] - positions[None, :, :]
            dist_sq = diff.pow(2).sum(-1).clamp_min(1e-3)
            force = -self.G * diff / dist_sq.unsqueeze(-1)
            net_force = force.sum(dim=1)
            positions = (positions + 0.05 * net_force).clamp(0.0, 1.0)
            trajectory.append(positions.clone())
        return trajectory


class FractalRenderer:
    """Renders zoom levels by recursively scaling the base grid."""

    def __init__(self, base_resolution: Iterable[int] = (16, 16)) -> None:
        self.base_resolution = tuple(base_resolution)

    def render_zoom_level(self, base_grid: torch.Tensor, zoom_level: int = 1) -> torch.Tensor:
        if zoom_level < 1:
            raise ValueError("zoom_level must be >= 1")
        scale = 2**zoom_level
        grid = base_grid
        if grid.dim() == 2:
            grid = grid.unsqueeze(-1)
        grid = grid.to(torch.float32)
        zoomed = grid.repeat_interleave(scale, dim=0).repeat_interleave(scale, dim=1)
        return zoomed

    def tensor_to_pil(self, tensor: torch.Tensor) -> Image.Image:
        array = tensor.detach().cpu()
        if array.dim() == 2:
            array = array.unsqueeze(-1)
        if array.shape[-1] == 1:
            array = array.repeat(1, 1, 3)
        array = array.clamp(0, 1).numpy()
        array = (array * 255).round().astype(np.uint8)
        return Image.fromarray(array)

    def save_image(self, tensor: torch.Tensor, path: str) -> None:
        self.tensor_to_pil(tensor).save(path)
