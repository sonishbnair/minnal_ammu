## SDXL-Tubro model parameter - Reference

Here is the description of the SDXL-Tubro model parameter and how it will effect the image generation
Below are the default value
```python
image = self.pipeline(
    prompt=combined_prompt,
    num_inference_steps=20,  # SDXL-Turbo specific
    height=size,
    width=size,
    guidance_scale=0.0,  # SDXL-Turbo specific
    num_images_per_prompt=1
).images[0]
```

1. `num_inference_steps` (Range: 1-50)
```python
num_inference_steps=1  # Default for SDXL-Turbo
```
- What it does: Controls how many denoising steps the model takes
- Higher values (20-50): 
  - Better image quality and details
  - Slower generation time
  - More consistent with prompt
- Lower values (1-10):
  - Faster generation
  - Less detailed output
  - More variation between generations
- For SDXL-Turbo specifically:
  - 1-2 steps is recommended (model is optimized for speed)
  - Even at 1 step, quality is generally good

2. `guidance_scale` (Range: 0.0-20.0)
```python
guidance_scale=0.0  # Default for SDXL-Turbo
```
- What it does: Controls how closely the image follows the prompt
- Higher values (7.0-20.0):
  - Stronger adherence to prompt
  - More dramatic, stylized results
  - Can lead to artifacts if too high
- Lower values (0.0-5.0):
  - More creative, natural-looking results
  - Less strict prompt following
  - Better for artistic generations
- For SDXL-Turbo:
  - 0.0 is recommended (model is trained for zero-guidance)
  - Values up to 2.0 can work well for more controlled output

3. `height` and `width` (Range: 256-1024)
```python
height=size,
width=size,
```
- What it affects: Output image dimensions
- Common sizes:
  - 256x256: Fast, good for testing
  - 512x512: Good balance of quality and speed
  - 768x768: High quality, slower
  - 1024x1024: Maximum quality, slowest
- Should be multiples of 8
- Larger sizes need more VRAM

4. `num_images_per_prompt` (Range: 1-10)
```python
num_images_per_prompt=1
```
- What it does: Number of images generated per prompt
- Higher values:
  - More variations to choose from
  - Linearly increases generation time
  - Requires more memory

Here's how you might adjust these for different scenarios:

```python
# For highest quality (slower)
image = self.pipeline(
    prompt=combined_prompt,
    num_inference_steps=20,
    height=768,
    width=768,
    guidance_scale=1.0,
    num_images_per_prompt=3
)

# For fastest generation (lower quality)
image = self.pipeline(
    prompt=combined_prompt,
    num_inference_steps=1,
    height=256,
    width=256,
    guidance_scale=0.0,
    num_images_per_prompt=1
)

# Balanced approach
image = self.pipeline(
    prompt=combined_prompt,
    num_inference_steps=2,
    height=512,
    width=512,
    guidance_scale=0.5,
    num_images_per_prompt=1
)
```

Let me know if you'd like me to explain any of these parameters in more detail or help you find the right balance for your specific needs!