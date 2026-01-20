"""FractalRenderer for upsampling and converting tensors to PIL images.

This module provides utilities for rendering zoom levels by upsampling tensors
and converting them to PIL Image objects.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
from PIL import Image
import torch
from torch.nn import functional as F


class FractalRenderer:
    """Renders zoom levels by upsampling the base grid using interpolation.
    
    Provides utilities to:
    - Upsample tensors to higher resolutions
    - Convert tensors to PIL Images
    - Save images to disk
    
    Args:
        base_resolution: Base resolution as (height, width) tuple (default: (16, 16))
    """

    def __init__(self, base_resolution: Iterable[int] = (16, 16)) -> None:
        self.base_resolution = tuple(base_resolution)

    def render_zoom_level(self, base_grid: torch.Tensor, zoom_level: int = 1) -> torch.Tensor:
        """Upsample base_grid to zoom level using bilinear interpolation.
        
        Args:
            base_grid: Input tensor of shape [height, width], [channels, height, width],
                      or [height, width, channels]
            zoom_level: Zoom level (1 = 2x resolution, 2 = 4x, etc.). Must be >= 1.
            
        Returns:
            Upsampled tensor of shape [channels, H, W] where H, W are
            base_resolution * (2 ** zoom_level)
            
        Raises:
            ValueError: If zoom_level < 1
        """
        if zoom_level < 1:
            raise ValueError("zoom_level must be an integer >= 1")
        
        # Convert to float32
        grid = base_grid.to(torch.float32)
        
        # Normalize shape to [batch, channels, height, width] for interpolate
        if grid.dim() == 2:
            # [height, width] -> [1, 1, height, width]
            grid = grid.unsqueeze(0).unsqueeze(0)
            num_channels = 1
        elif grid.dim() == 3:
            # Check if [C, H, W] or [H, W, C]
            # Heuristic: if first dim is small (1-4), assume [C, H, W]
            if grid.shape[0] <= 4:
                # [channels, height, width] -> [1, channels, height, width]
                grid = grid.unsqueeze(0)
                num_channels = grid.shape[1]
            else:
                # [height, width, channels] -> [1, channels, height, width]
                grid = grid.permute(2, 0, 1).unsqueeze(0)
                num_channels = grid.shape[1]
        else:
            raise ValueError(f"Expected 2D or 3D tensor, got shape {grid.shape}")
        
        # Calculate target size
        target_height = self.base_resolution[0] * (2 ** zoom_level)
        target_width = self.base_resolution[1] * (2 ** zoom_level)
        
        # Upsample using bilinear interpolation
        zoomed = F.interpolate(
            grid,
            size=(target_height, target_width),
            mode="bilinear",
            align_corners=False
        )
        
        # Remove batch dimension and return [channels, height, width]
        zoomed = zoomed.squeeze(0)
        
        return zoomed

    def tensor_to_pil(self, tensor: torch.Tensor) -> Image.Image:
        """Convert a float tensor to a PIL Image.
        
        Args:
            tensor: Input tensor with values in [0, 1]. Can be:
                   - [height, width] for grayscale
                   - [channels, height, width] for multi-channel
                   - [height, width, channels] for multi-channel
            
        Returns:
            PIL Image in mode 'L' (grayscale) or 'RGB'
        """
        # Move to CPU and detach
        array = tensor.detach().cpu()
        
        # Normalize to [height, width, channels]
        if array.dim() == 2:
            # [height, width] -> [height, width, 1]
            array = array.unsqueeze(-1)
        elif array.dim() == 3:
            # Check if [C, H, W] or [H, W, C]
            if array.shape[0] <= 4 and array.shape[0] < min(array.shape[1], array.shape[2]):
                # [channels, height, width] -> [height, width, channels]
                array = array.permute(1, 2, 0)
        
        # Handle single channel -> grayscale or RGB
        if array.shape[-1] == 1:
            # Convert to [height, width] for grayscale
            array = array.squeeze(-1)
            array = array.clamp(0, 1).numpy()
            array = (array * 255).round().astype(np.uint8)
            return Image.fromarray(array, mode='L')
        else:
            # For RGB, take first 3 channels if more exist
            if array.shape[-1] > 3:
                array = array[..., :3]
            elif array.shape[-1] == 2:
                # Pad to 3 channels
                array = torch.cat([array, torch.zeros_like(array[..., :1])], dim=-1)
            
            array = array.clamp(0, 1).numpy()
            array = (array * 255).round().astype(np.uint8)
            return Image.fromarray(array, mode='RGB')

    def save_image(self, tensor_or_pil, path: str) -> None:
        """Save a tensor or PIL Image to disk.
        
        Args:
            tensor_or_pil: Either a torch.Tensor or PIL.Image.Image
            path: Output file path
        """
        if isinstance(tensor_or_pil, Image.Image):
            tensor_or_pil.save(path)
        else:
            self.tensor_to_pil(tensor_or_pil).save(path)
