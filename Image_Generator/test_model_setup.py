import os
import torch
import gc
from diffusers import AutoPipelineForText2Image
import time
from pathlib import Path

def cleanup_memory():
    """Clean up memory after operations"""
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

def test_generation(pipeline, image_size, prompt):
    """Test image generation with specific size"""
    start_time = time.time()
    
    try:
        image = pipeline(
            prompt=prompt,
            num_inference_steps=1,
            height=image_size,
            width=image_size,
            guidance_scale=0.0,
            num_images_per_prompt=1
        ).images[0]
        
        generation_time = time.time() - start_time
        
        # Save image
        output_dir = "test_outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"test_size_{image_size}_{int(time.time())}.png")
        image.save(output_path)
        
        return True, generation_time, output_path
        
    except Exception as e:
        return False, 0, str(e)

def run_size_test(model_path, sizes=[256, 384, 512, 768, 1024]):
    """Test different image sizes"""
    print("\n=== CPU Performance Test for Different Image Sizes ===")
    print(f"Model path: {model_path}")
    
    # Force CPU usage
    device = "cpu"
    print(f"\nUsing device: {device}")
    
    try:
        # Load model
        print("\nLoading model on CPU...")
        start_time = time.time()
        
        pipeline = AutoPipelineForText2Image.from_pretrained(
            model_path,
            torch_dtype=torch.float32,  # Use float32 for CPU
            local_files_only=True
        ).to(device)
        
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f} seconds")
        
        # Test prompt
        test_prompt = "A serene landscape with mountains and a lake at sunset, photorealistic"
        
        # Test each size
        results = []
        print("\nTesting different image sizes:")
        for size in sizes:
            print(f"\nTesting {size}x{size} resolution:")
            cleanup_memory()
            
            success, gen_time, output = test_generation(pipeline, size, test_prompt)
            
            if success:
                print(f"✓ Generation successful")
                print(f"• Generation time: {gen_time:.2f} seconds")
                print(f"• Output saved as: {output}")
                results.append((size, gen_time))
            else:
                print(f"✗ Generation failed")
                print(f"• Error: {output}")
        
        # Summary
        print("\n=== Performance Summary ===")
        print("Image Size | Generation Time")
        print("-----------+----------------")
        for size, time_taken in results:
            print(f"{size:>4}x{size:<4} | {time_taken:.2f} seconds")
        
        return True
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    # Model path - update this to your model location
    MODEL_PATH = "/Users/sonishbalan/AI_Models/sdxl-turbo11"
    
    # Test with different image sizes
    # You can modify this list to test different sizes
    test_sizes = [256, 384, 512]  # Starting with smaller sizes
    
    success = run_size_test(MODEL_PATH, test_sizes)
    
    if not success:
        print("\nTroubleshooting Tips:")
        print("1. Verify model path is correct")
        print("2. Ensure enough system memory is available")
        print("3. Close other memory-intensive applications")
        print("4. Try with smaller image sizes")
        print("5. Check system resources in Activity Monitor")