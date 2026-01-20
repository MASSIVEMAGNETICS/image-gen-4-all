"""Lightweight HART implementation optimized for CPU and small d_model.

This module provides a minimal, CPU-friendly HART (Hybrid Autoregressive Transformer)
implementation using convolutional encoder-decoder architecture instead of heavy
transformer layers.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class HART(nn.Module):
    """Lightweight HART implementation using convolutional layers.
    
    A CPU-friendly alternative to the full transformer-based HART, using
    a simple convolutional encoder-decoder with residual connections.
    Deterministic under torch.manual_seed().
    
    Args:
        d_model: Number of channels in the input/output tensors (default: 16)
        num_layers: Number of convolutional layers in the architecture (default: 2)
    """

    def __init__(self, d_model: int = 16, num_layers: int = 2) -> None:
        super().__init__()
        self.d_model = d_model
        self.num_layers = num_layers
        
        # Build a simple convolutional encoder-decoder
        self.layers = nn.ModuleList()
        for i in range(num_layers):
            # Each layer consists of conv + residual connection
            self.layers.append(
                nn.Sequential(
                    nn.Conv2d(d_model, d_model, kernel_size=3, padding=1, bias=True),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(d_model, d_model, kernel_size=3, padding=1, bias=True),
                )
            )
        
        # Final projection to 3 channels (RGB)
        self.proj = nn.Conv2d(d_model, 3, kernel_size=1, bias=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Process input tensor through the network.
        
        Args:
            x: Input tensor of shape [batch, height, width, channels]
            
        Returns:
            Output tensor of shape [batch, height, width, 3] with values in [0, 1]
            
        Raises:
            ValueError: If input shape is incorrect or channels don't match d_model
        """
        if x.dim() != 4:
            raise ValueError("Expected input with shape [batch, height, width, channels].")
        
        batch, height, width, channels = x.shape
        if channels != self.d_model:
            raise ValueError(f"Expected input channels to match d_model={self.d_model}.")
        
        # Convert from [batch, height, width, channels] to [batch, channels, height, width]
        x = x.permute(0, 3, 1, 2)
        
        # Apply convolutional layers with residual connections
        for layer in self.layers:
            identity = x
            x = layer(x)
            x = x + identity  # Residual connection
            x = F.relu(x)
        
        # Project to RGB
        x = self.proj(x)
        
        # Convert back to [batch, height, width, channels] and apply sigmoid
        x = x.permute(0, 2, 3, 1)
        return torch.sigmoid(x)
