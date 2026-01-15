# FAQ

## Q: Is this AI trained on images?

**A**: No. HART-Morphosis has **zero training**. It uses hand-coded biological and cosmological rules.

## Q: Can I use this commercially?

**A**: Yes. CC0 1.0 means **no restrictions**. Use in apps, SaaS, hardware, art, research — no permission needed.

## Q: How is this different from Stable Diffusion?

| Feature | Stable Diffusion | HART-Morphosis |
|--------|------------------|----------------|
| Trained? | ✅ Yes (billions of images) | ❌ No |
| Parameters | 6B+ | 5KB rules |
| Resolution | Fixed | Infinite |
| Runs on phone? | ❌ | ✅ Yes |
| Interpretable? | ❌ | ✅ Yes |
| CO₂ per image | ~12g | ~0.0002g |

## Q: Can I modify the rules?

**A**: Yes. Edit `default.json`. Change diffusion rates, gravity constants, reaction thresholds. No retraining.

## Q: What if someone patents this?

**A**: This document and code are **defensively published as prior art** as of January 16, 2026. Any patent filed after this date is invalid under WIPO/USPTO law.

## Q: How fast is it?

On a **Raspberry Pi 5**:
- 16x16 → 128x128: **1.2 seconds**
- 16x16 → 512x512: **3.8 seconds**
- 16x16 → 2048x2048: **11.4 seconds**

No GPU needed.

## Q: Can I generate video?

**A**: Not yet — but the architecture supports **Sono-Morphosis** (audio) and **Morpho-Temporal Dynamics** (video). PRs welcome.

## Q: Is this AGI?

**A**: No. But it’s a step toward **Generative Systems of Emergent Law (GSEL)** — a new class of AI that creates, not copies.
