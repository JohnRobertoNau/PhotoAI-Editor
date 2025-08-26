#!/usr/bin/env python3
"""
Test script to verify AI functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PIL import Image
from src.models.generative_fill import GenerativeFill

def test_ai_functionality():
    """Test if AI generative fill works"""
    print("🧪 Testing AI Generative Fill functionality...")
    print("=" * 50)
    
    # Create a test instance
    gen_fill = GenerativeFill()
    
    print(f"🔍 Advanced mode: {gen_fill.advanced_mode}")
    print(f"🔍 Pipeline loaded: {gen_fill.pipeline is not None}")
    print(f"🔍 Device: {gen_fill.device}")
    
    # Create a simple test image
    test_image = Image.new('RGB', (128, 128), (255, 0, 0))  # Red image
    test_mask = Image.new('RGB', (128, 128), (0, 0, 0))     # Black mask
    
    # Add a white square in the mask (area to fill)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(test_mask)
    draw.rectangle([40, 40, 80, 80], fill=(255, 255, 255))
    
    print("\n🖼️  Created test image: 128x128 red with white square mask")
    
    try:
        # Test the generative fill
        print("\n🚀 Testing generative fill...")
        result = gen_fill.fill(test_image, test_mask, "blue background")
        
        if result:
            print("✅ Generative fill completed successfully!")
            print(f"📏 Result size: {result.size}")
            print(f"🎨 Result mode: {result.mode}")
            
            # Save test result
            result.save("test_ai_result.png")
            print("💾 Result saved as 'test_ai_result.png'")
            
        else:
            print("❌ Generative fill returned None")
            
    except Exception as e:
        print(f"❌ Error during generative fill: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_ai_functionality()
