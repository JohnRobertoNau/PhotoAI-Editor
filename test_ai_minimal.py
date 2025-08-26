#!/usr/bin/env python3
"""
Minimal test for transformers in executable
"""

def test_transformers_import():
    """Test if transformers can be imported properly"""
    print("🧪 Testing transformers import...")
    
    try:
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
        
        # Test specific components
        from transformers import CLIPTokenizer, CLIPTextModel
        print("✅ CLIP components imported successfully")
        
        from transformers import pipeline
        print("✅ Pipeline imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def test_diffusers_import():
    """Test if diffusers can be imported properly"""
    print("\n🧪 Testing diffusers import...")
    
    try:
        import diffusers
        print(f"✅ Diffusers version: {diffusers.__version__}")
        
        from diffusers import StableDiffusionInpaintPipeline
        print("✅ StableDiffusionInpaintPipeline imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def test_model_loading():
    """Test actual model loading (minimal)"""
    print("\n🧪 Testing model loading...")
    
    try:
        import torch
        from diffusers import StableDiffusionInpaintPipeline
        
        print("🔄 Attempting to load pipeline...")
        
        # Try loading with local_files_only first
        try:
            pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                "runwayml/stable-diffusion-inpainting",
                torch_dtype=torch.float32,
                safety_checker=None,
                requires_safety_checker=False,
                local_files_only=True
            )
            print("✅ Model loaded from local cache!")
            return True
            
        except Exception as e1:
            print(f"⚠️ Local loading failed: {e1}")
            
            # Try downloading
            print("🔄 Attempting to download...")
            pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                "runwayml/stable-diffusion-inpainting",
                torch_dtype=torch.float32,
                safety_checker=None,
                requires_safety_checker=False,
                local_files_only=False
            )
            print("✅ Model downloaded and loaded!")
            return True
            
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 AI Components Test")
    print("=" * 40)
    
    transformers_ok = test_transformers_import()
    diffusers_ok = test_diffusers_import()
    
    if transformers_ok and diffusers_ok:
        model_ok = test_model_loading()
        
        if model_ok:
            print("\n🎉 All tests passed! AI should work in executable.")
        else:
            print("\n⚠️ Model loading failed - will use fallback mode.")
    else:
        print("\n❌ Import tests failed - need to fix hidden imports.")
    
    print("\n" + "=" * 40)
