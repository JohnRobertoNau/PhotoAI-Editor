#!/usr/bin/env python3
"""
Test script pentru verificarea instalării AI Photo Editor
"""

import sys
import importlib.util

def test_import(module_name, package=None):
    """Testează importul unui modul."""
    try:
        if package:
            __import__(package)
            print(f"✅ {module_name}: OK")
            return True
        else:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✅ {module_name}: OK")
                return True
            else:
                print(f"❌ {module_name}: Nu este găsit")
                return False
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False

def main():
    print("🧪 Test AI Photo Editor - Verificare dependențe\n")
    
    # Testează Python version
    python_version = sys.version_info
    print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("⚠️ Recomandăm Python 3.8+")
    else:
        print("✅ Versiune Python OK")
    
    print("\n📦 Dependențe de bază:")
    basic_deps = [
        ("Pillow", "PIL"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("CustomTkinter", "customtkinter"),
        ("scikit-learn", "sklearn"),
        ("requests", "requests"),
    ]
    
    basic_ok = 0
    for name, module in basic_deps:
        if test_import(name, module):
            basic_ok += 1
    
    print(f"\n📊 Dependențe de bază: {basic_ok}/{len(basic_deps)}")
    
    # Testează dependențele AI avansate
    print("\n🤖 Dependențe AI avansate (opționale):")
    ai_deps = [
        ("PyTorch", "torch"),
        ("TorchVision", "torchvision"),
        ("Transformers", "transformers"),
        ("Diffusers", "diffusers"),
        ("rembg", "rembg"),
    ]
    
    ai_ok = 0
    for name, module in ai_deps:
        if test_import(name, module):
            ai_ok += 1
    
    print(f"\n📊 Dependențe AI: {ai_ok}/{len(ai_deps)}")
    
    # Test GUI
    print("\n🖼️ Test GUI:")
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()  # Ascunde fereastra
        root.destroy()
        print("✅ Tkinter GUI: OK")
        gui_ok = True
    except Exception as e:
        print(f"❌ Tkinter GUI: {e}")
        gui_ok = False
    
    # Test importuri proprii
    print("\n📁 Test module aplicație:")
    try:
        sys.path.insert(0, 'src')
        from models.upscaler import ImageUpscaler
        from models.background_remover import BackgroundRemover
        from models.generative_fill import GenerativeFill
        from models.image_recognition import ImageRecognition
        from utils.image_processor import ImageProcessor
        print("✅ Module aplicație: OK")
        app_modules_ok = True
    except Exception as e:
        print(f"❌ Module aplicație: {e}")
        app_modules_ok = False
    
    # Sumar final
    print("\n" + "="*50)
    print("📋 SUMAR:")
    print(f"Dependențe de bază: {basic_ok}/{len(basic_deps)} {'✅' if basic_ok >= 4 else '⚠️'}")
    print(f"Dependențe AI: {ai_ok}/{len(ai_deps)} {'✅' if ai_ok >= 2 else '⚠️'}")
    print(f"GUI: {'✅' if gui_ok else '❌'}")
    print(f"Module aplicație: {'✅' if app_modules_ok else '❌'}")
    
    if basic_ok >= 4 and gui_ok and app_modules_ok:
        print("\n🎉 Gata! Poți rula aplicația cu: python main.py")
        if ai_ok < 2:
            print("💡 Pentru funcții AI avansate, instalează: pip install transformers diffusers rembg")
    else:
        print("\n⚠️ Instalarea nu este completă.")
        print("Rulează: bash setup.sh (în WSL) sau pip install -r requirements.txt")
    
    return 0

if __name__ == "__main__":
    main()
