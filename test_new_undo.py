#!/usr/bin/env python3
"""
Test independent pentru sistemul simplificat de undo/redo
"""

import pickle
import gzip
import time
from enum import Enum
from PIL import Image, ImageDraw
import numpy as np

class OperationType(Enum):
    NORMAL = "normal"
    AI = "ai"
    DRAWING = "drawing"

class UndoState:
    def __init__(self, image: Image.Image, operation_name: str, operation_type: OperationType):
        self.operation_name = operation_name
        self.operation_type = operation_type
        self.timestamp = time.time()
        
        # Compresie adaptivă bazată pe tipul operației
        if operation_type == OperationType.AI:
            # Pentru AI: compresie mai bună dar mai lentă
            self.compressed_image = self._compress_image_high(image)
        else:
            # Pentru normal/drawing: compresie rapidă
            self.compressed_image = self._compress_image_fast(image)
    
    def _compress_image_high(self, image: Image.Image) -> bytes:
        """Compresie de înaltă calitate pentru operații AI"""
        img_array = np.array(image)
        return gzip.compress(pickle.dumps(img_array), compresslevel=9)
    
    def _compress_image_fast(self, image: Image.Image) -> bytes:
        """Compresie rapidă pentru operații normale"""
        img_array = np.array(image)
        return gzip.compress(pickle.dumps(img_array), compresslevel=3)
    
    def get_image(self) -> Image.Image:
        """Decomprimă și returnează imaginea"""
        img_array = pickle.loads(gzip.decompress(self.compressed_image))
        return Image.fromarray(img_array)
    
    def get_memory_size(self) -> int:
        """Returnează mărimea în memorie"""
        return len(self.compressed_image)

def classify_operation(operation_name: str) -> OperationType:
    """Clasifică operația bazat pe nume"""
    ai_operations = [
        'generative fill', 'background removal', 'remove background',
        'image recognition', 'generate', 'inpaint'
    ]
    
    drawing_operations = [
        'brush', 'pen', 'draw', 'paint', 'line', 'rectangle', 
        'circle', 'text', 'shape'
    ]
    
    # Operații normale (filtre, ajustări, transformări) - inclusiv upscale non-AI
    normal_operations = [
        'filter', 'blur', 'sharpen', 'brightness', 'contrast', 
        'saturation', 'hue', 'gamma', 'levels', 'curves',
        'grayscale', 'sepia', 'invert', 'edge', 'emboss',
        'rotate', 'flip', 'crop', 'resize', 'scale', 'upscale'
    ]
    
    operation_lower = operation_name.lower()
    
    # Verifică mai întâi operațiile normale (pentru a avea prioritate)
    for normal_op in normal_operations:
        if normal_op in operation_lower:
            return OperationType.NORMAL
    
    # Apoi verifică operațiile AI
    for ai_op in ai_operations:
        if ai_op in operation_lower:
            return OperationType.AI
    
    # În final verifică operațiile de desenare
    for draw_op in drawing_operations:
        if draw_op in operation_lower:
            return OperationType.DRAWING
    
    # Default: operație normală
    return OperationType.NORMAL

def create_test_image(width=300, height=200, color=(255, 255, 255)):
    """Creează o imagine de test"""
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle([50, 50, 150, 150], fill=(255, 0, 0))
    draw.ellipse([200, 50, 250, 100], fill=(0, 255, 0))
    return image

def test_new_undo_system():
    """Testează noul sistem simplificat"""
    print("🧪 TESTARE SISTEM SIMPLIFICAT UNDO/REDO")
    print("=" * 50)
    
    try:
        # 1. Test UndoState - Compresie
        print("\n1️⃣ Test Compresie Adaptivă")
        test_image = create_test_image()
        
        # Test operație AI (compresie înaltă)
        ai_state = UndoState(test_image, "AI Background Removal", OperationType.AI)
        ai_size = ai_state.get_memory_size()
        
        # Test operație normală (compresie rapidă)
        normal_state = UndoState(test_image, "Blur Filter", OperationType.NORMAL)
        normal_size = normal_state.get_memory_size()
        
        print(f"   Memorie AI state: {ai_size / 1024:.1f} KB")
        print(f"   Memorie Normal state: {normal_size / 1024:.1f} KB")
        if normal_size > 0:
            print(f"   AI vs Normal: {((ai_size - normal_size) / normal_size * 100):+.1f}%")
        
        # 2. Test Restaurare Imagine
        print("\n2️⃣ Test Restaurare Imagine")
        
        # Test restore AI
        restored_ai = ai_state.get_image()
        original_array = np.array(test_image)
        restored_array = np.array(restored_ai)
        
        if np.array_equal(original_array, restored_array):
            print("   ✅ AI state restaurare: PERFECTĂ")
            ai_ok = True
        else:
            print("   ❌ AI state restaurare: EȘUATĂ")
            ai_ok = False
        
        # Test restore normal
        restored_normal = normal_state.get_image()
        restored_normal_array = np.array(restored_normal)
        
        if np.array_equal(original_array, restored_normal_array):
            print("   ✅ Normal state restaurare: PERFECTĂ")
            normal_ok = True
        else:
            print("   ❌ Normal state restaurare: EȘUATĂ")
            normal_ok = False
        
        # 3. Test Clasificare Operații
        print("\n3️⃣ Test Clasificare Operații")
        test_operations = [
            ("Blur Filter", OperationType.NORMAL),
            ("Generative Fill", OperationType.AI),
            ("Background Removal", OperationType.AI),
            ("Brush Tool", OperationType.DRAWING),
            ("Brightness Adjustment", OperationType.NORMAL),
            ("AI Upscale", OperationType.NORMAL),  # Trebuie să fie normal
        ]
        
        classification_ok = True
        for op_name, expected_type in test_operations:
            actual_type = classify_operation(op_name)
            status = "✅" if actual_type == expected_type else "❌"
            print(f"   {status} '{op_name}' → {actual_type.value} (așteptat: {expected_type.value})")
            if actual_type != expected_type:
                classification_ok = False
        
        # 4. Test Ciclu Undo/Redo Simulat
        print("\n4️⃣ Test Ciclu Complet")
        
        # Simulează un stack de undo
        undo_stack = []
        current_image = create_test_image()
        
        print("   📸 Imagine inițială creată")
        
        # Operație 1: Normal
        undo_stack.append(UndoState(current_image, "Blur", OperationType.NORMAL))
        # Simulează blur
        from PIL import ImageFilter
        current_image = current_image.filter(ImageFilter.BLUR)
        print("   🔹 Operație 1: Blur aplicat")
        
        # Operație 2: AI  
        undo_stack.append(UndoState(current_image, "Background Removal", OperationType.AI))
        # Simulează AI operation
        img_array = np.array(current_image)
        img_array = 255 - img_array  # Inversare pentru simulare
        current_image = Image.fromarray(img_array)
        print("   🤖 Operație 2: AI Background Removal aplicat")
        
        # Test undo de 2 ori
        cycle_ok = True
        if undo_stack:
            last_state = undo_stack.pop()
            current_image = last_state.get_image()
            print(f"   ⬅️ Undo 1: {last_state.operation_name} - SUCCESS")
        else:
            cycle_ok = False
        
        if undo_stack:
            last_state = undo_stack.pop()
            current_image = last_state.get_image()
            print(f"   ⬅️ Undo 2: {last_state.operation_name} - SUCCESS")
        else:
            cycle_ok = False
        
        # Rezultat final
        print("\n" + "=" * 50)
        all_tests_ok = ai_ok and normal_ok and classification_ok and cycle_ok
        
        if all_tests_ok:
            print("🎉 TOATE TESTELE AU TRECUT!")
            print("✅ Sistemul simplificat funcționează PERFECT")
            print("\n💡 Avantajele noului sistem:")
            print("   • Compresie adaptivă pentru AI vs Normal")
            print("   • Restaurare perfectă a imaginilor")
            print("   • Clasificare corectă a operațiilor")
            print("   • Logică simplă și robustă")
        else:
            print("⚠️ UNELE TESTE AU EȘUAT")
            if not ai_ok or not normal_ok:
                print("🔧 Problemă cu restaurarea imaginilor")
            if not classification_ok:
                print("🔧 Problemă cu clasificarea operațiilor")
            if not cycle_ok:
                print("🔧 Problemă cu ciclul undo/redo")
        
        return all_tests_ok
        
    except Exception as e:
        print(f"❌ EROARE în test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_new_undo_system()
    sys.exit(0 if success else 1)
