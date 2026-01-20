"""Core HART-Morphosis primitives - Morphogenesis and Cosmological modules."""

from __future__ import annotations

from typing import List, Tuple

import torch
from torch.nn import functional as F


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
            dist_sq = diff.pow(2).sum(-1).clamp_min(1e-2)
            force = -self.G * diff / dist_sq.unsqueeze(-1)
            net_force = force.sum(dim=1)
            positions = (positions + 0.05 * net_force).clamp(0.0, 1.0)
            trajectory.append(positions.clone())
        return trajectory
