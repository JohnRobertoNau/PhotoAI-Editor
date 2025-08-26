#!/usr/bin/env python3
"""
Bundle AI models for executable distribution
This script downloads and prepares the AI models for inclusion in the executable
"""

import os
import sys
from pathlib import Path
import shutil
import subprocess

def setup_model_cache():
    """Setup local model cache directory"""
    cache_dir = Path(__file__).parent / "models_cache"
    cache_dir.mkdir(exist_ok=True)
    
    # Set environment variables to use local cache
    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["TRANSFORMERS_CACHE"] = str(cache_dir / "transformers")
    os.environ["HF_DATASETS_CACHE"] = str(cache_dir / "datasets")
    
    return cache_dir

def download_stable_diffusion_model():
    """Download the Stable Diffusion inpainting model"""
    print("🔄 Downloading Stable Diffusion Inpainting model...")
    
    try:
        import torch
        from diffusers import StableDiffusionInpaintPipeline
        
        model_name = "runwayml/stable-diffusion-inpainting"
        pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        print(f"✅ Model '{model_name}' downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def copy_models_to_dist():
    """Copy the downloaded models to the distribution directory"""
    cache_dir = Path(__file__).parent / "models_cache"
    dist_dir = Path(__file__).parent / "dist" / "models"
    
    if cache_dir.exists():
        print(f"📦 Copying models from {cache_dir} to {dist_dir}")
        
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        shutil.copytree(cache_dir, dist_dir)
        print("✅ Models copied successfully!")
    else:
        print("❌ No models cache found to copy")

def main():
    print("🤖 AI Model Bundling Script")
    print("=" * 40)
    
    # Check if required libraries are available
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
    except ImportError:
        print("❌ PyTorch not found! Install it first.")
        sys.exit(1)
    
    try:
        import diffusers
        print(f"✅ Diffusers version: {diffusers.__version__}")
    except ImportError:
        print("❌ Diffusers not found! Install it first.")
        sys.exit(1)
    
    # Setup cache directory
    cache_dir = setup_model_cache()
    print(f"📁 Using cache directory: {cache_dir}")
    
    # Download models
    if download_stable_diffusion_model():
        print("\n🎉 All models downloaded successfully!")
        
        # Ask if user wants to copy to dist
        response = input("\n📦 Copy models to dist directory? (y/n): ")
        if response.lower() in ['y', 'yes']:
            copy_models_to_dist()
    else:
        print("\n❌ Model download failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
