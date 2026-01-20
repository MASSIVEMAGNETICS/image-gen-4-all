"""Integration tests for HART-Morphosis pipeline.

Tests the end-to-end pipeline from pattern generation through HART processing
to fractal rendering, ensuring CLI and web UI can run successfully.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from PIL import Image
import pytest
import torch

from src.hart_morphosis.core import HART, FractalRenderer, MorphogenesisEngine


class TestPipeline:
    """Integration tests for the full HART-Morphosis pipeline."""

    def test_end_to_end_pipeline(self):
        """Test the complete pipeline from pattern generation to image rendering.
        
        This test validates:
        1. MorphogenesisEngine generates patterns correctly
        2. HART processes base_state tensors
        3. FractalRenderer upsamples and converts to PIL Images
        4. The pipeline is deterministic with a seed
        """
        # Create MorphogenesisEngine with small grid for fast testing
        morpho = MorphogenesisEngine(grid_size=(8, 8))
        
        # Generate pattern with seed for determinism
        pattern = morpho.generate_pattern(steps=1, seed=0)
        
        # Verify pattern shape
        assert pattern.shape == (8, 8), f"Expected pattern shape (8, 8), got {pattern.shape}"
        assert pattern.dtype == torch.float32
        assert pattern.min() >= 0.0 and pattern.max() <= 1.0
        
        # Create base_state the same way CLI/web_ui do
        # pattern.unsqueeze(-1).repeat(1,1,16).unsqueeze(0)
        # Shape: [8, 8] -> [8, 8, 16] -> [1, 8, 8, 16]
        base_state = pattern.unsqueeze(-1).repeat(1, 1, 16).unsqueeze(0)
        
        assert base_state.shape == (1, 8, 8, 16), f"Expected base_state shape (1, 8, 8, 16), got {base_state.shape}"
        
        # Instantiate HART with d_model=16, num_layers=2
        model = HART(d_model=16, num_layers=2)
        
        # Run forward pass
        with torch.no_grad():
            refined = model(base_state)
        
        # Verify output shape
        assert refined.shape == (1, 8, 8, 3), f"Expected refined shape (1, 8, 8, 3), got {refined.shape}"
        assert refined.min() >= 0.0 and refined.max() <= 1.0, "HART output should be in [0, 1]"
        
        # Remove batch dimension for renderer
        refined = refined.squeeze(0)
        
        # Instantiate FractalRenderer
        renderer = FractalRenderer(base_resolution=(8, 8))
        
        # Render at zoom level 1 (2x upsampling)
        zoomed = renderer.render_zoom_level(refined, zoom_level=1)
        
        # Verify zoomed tensor is correct shape
        assert isinstance(zoomed, torch.Tensor)
        expected_size = (8 * 2, 8 * 2)  # 2^1 = 2x scaling
        assert zoomed.shape[1:] == expected_size, f"Expected zoomed size {expected_size}, got {zoomed.shape[1:]}"
        
        # Convert to PIL Image
        pil_image = renderer.tensor_to_pil(zoomed)
        
        # Verify PIL Image
        assert isinstance(pil_image, Image.Image), f"Expected PIL.Image.Image, got {type(pil_image)}"
        assert pil_image.size == (16, 16), f"Expected image size (16, 16), got {pil_image.size}"
        
    def test_deterministic_behavior(self):
        """Test that the pipeline is deterministic when using the same seed."""
        seed = 42
        
        # Run pipeline twice with same seed
        results = []
        for _ in range(2):
            torch.manual_seed(seed)
            
            morpho = MorphogenesisEngine(grid_size=(8, 8))
            pattern = morpho.generate_pattern(steps=1, seed=seed)
            base_state = pattern.unsqueeze(-1).repeat(1, 1, 16).unsqueeze(0)
            
            model = HART(d_model=16, num_layers=2)
            with torch.no_grad():
                refined = model(base_state)
            
            results.append(refined)
        
        # Verify results are identical
        assert torch.allclose(results[0], results[1], atol=1e-6), "Pipeline should be deterministic with same seed"
    
    def test_save_image(self):
        """Test that images can be saved to disk."""
        # Create a simple pattern
        morpho = MorphogenesisEngine(grid_size=(8, 8))
        pattern = morpho.generate_pattern(steps=1, seed=0)
        
        # Create renderer
        renderer = FractalRenderer(base_resolution=(8, 8))
        
        # Save to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.png"
            renderer.save_image(pattern, str(output_path))
            
            # Verify file exists
            assert output_path.exists(), "Output file should be created"
            
            # Verify it's a valid image
            img = Image.open(output_path)
            assert isinstance(img, Image.Image)

    def test_different_zoom_levels(self):
        """Test rendering at different zoom levels."""
        morpho = MorphogenesisEngine(grid_size=(8, 8))
        pattern = morpho.generate_pattern(steps=1, seed=0)
        
        renderer = FractalRenderer(base_resolution=(8, 8))
        
        # Test zoom levels 1, 2, 3
        for zoom_level in [1, 2, 3]:
            zoomed = renderer.render_zoom_level(pattern, zoom_level=zoom_level)
            expected_size = 8 * (2 ** zoom_level)
            
            assert zoomed.shape[-2] == expected_size, f"Zoom {zoom_level}: expected height {expected_size}"
            assert zoomed.shape[-1] == expected_size, f"Zoom {zoom_level}: expected width {expected_size}"
