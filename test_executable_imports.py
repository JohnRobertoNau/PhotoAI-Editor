#!/usr/bin/env python3
"""
Quick test inside executable environment
"""

def test_imports_in_executable():
    """Test what's missing in executable"""
    print("🔍 Testing imports in executable environment...")
    
    try:
        import diffusers
        print(f"✅ diffusers: {diffusers.__version__}")
    except Exception as e:
        print(f"❌ diffusers: {e}")
    
    try:
        import transformers
        print(f"✅ transformers: {transformers.__version__}")
    except Exception as e:
        print(f"❌ transformers: {e}")
        
    try:
        from diffusers import StableDiffusionInpaintPipeline
        print("✅ StableDiffusionInpaintPipeline imported")
    except Exception as e:
        print(f"❌ StableDiffusionInpaintPipeline: {e}")

if __name__ == "__main__":
    test_imports_in_executable()
