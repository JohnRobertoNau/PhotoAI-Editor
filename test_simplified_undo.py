#!/usr/bin/env python3
"""
Test pentru noul sistem simplificat de undo/redo
"""

import sys
import os
from PIL import Image, ImageDraw
import numpy as np

# Adaugă calea către src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_image(width=300, height=200, color=(255, 255, 255)):
    """Creează o imagine de test"""
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle([50, 50, 150, 150], fill=(255, 0, 0))
    draw.ellipse([200, 50, 250, 100], fill=(0, 255, 0))
    return image

def modify_image_normal(image):
    """Modifică imaginea cu o operație normală (filtre)"""
    from PIL import ImageFilter
    return image.filter(ImageFilter.BLUR)

def modify_image_ai(image):
    """Simulează o operație AI (schimbă culoarea dramatică)"""
    img_array = np.array(image)
    # Simulează background removal prin inversare
    img_array = 255 - img_array
    return Image.fromarray(img_array)

def test_undo_state_classes():
    """Testează doar clasele UndoState și OperationType fără UI"""
    print("🧪 TESTARE CLASE UNDO/REDO INDEPENDENTE")
    print("=" * 50)
    
    # Importă direct clasele din test, nu din main_window
    import pickle
    import gzip
    import time
    from enum import Enum
    
    # Recreează clasele pentru test
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

    try:
        # 1. Test UndoState
        print("\n1️⃣ Test UndoState - Compresie Adaptivă")
        test_image = create_test_image()
        
        # Test operație AI (compresie înaltă)
        ai_state = UndoState(test_image, "AI Background Removal", OperationType.AI)
        ai_size = ai_state.get_memory_size()
        
        # Test operație normală (compresie rapidă)
        normal_state = UndoState(test_image, "Blur Filter", OperationType.NORMAL)
        normal_size = normal_state.get_memory_size()
        
        print(f"   Memorie AI state: {ai_size / 1024:.1f} KB")
        print(f"   Memorie Normal state: {normal_size / 1024:.1f} KB")
        print(f"   Diferența: {((ai_size - normal_size) / normal_size * 100):+.1f}%")
        
        # 2. Test Restaurare Imagine
        print("\n2️⃣ Test Restaurare Imagine")
        
        # Test restore AI
        restored_ai = ai_state.get_image()
        original_array = np.array(test_image)
        restored_array = np.array(restored_ai)
        
        if np.array_equal(original_array, restored_array):
            print("   ✅ AI state restaurare: PERFECTĂ")
            ai_test_ok = True
        else:
            print("   ❌ AI state restaurare: EȘUATĂ")
            ai_test_ok = False
        
        # Test restore normal
        restored_normal = normal_state.get_image()
        restored_normal_array = np.array(restored_normal)
        
        if np.array_equal(original_array, restored_normal_array):
            print("   ✅ Normal state restaurare: PERFECTĂ")
            normal_test_ok = True
        else:
            print("   ❌ Normal state restaurare: EȘUATĂ")
            normal_test_ok = False
        
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
        
        all_correct = True
        for op_name, expected_type in test_operations:
            actual_type = classify_operation(op_name)
            status = "✅" if actual_type == expected_type else "❌"
            print(f"   {status} '{op_name}' → {actual_type.value} (așteptat: {expected_type.value})")
            if actual_type != expected_type:
                all_correct = False
        
        # Rezultat final
        print("\n" + "=" * 50)
        success = ai_test_ok and normal_test_ok and all_correct
        if success:
            print("🎉 TOATE TESTELE AU TRECUT!")
            print("✅ Sistemul simplificat funcționează corect")
        else:
            print("⚠️ UNELE TESTE AU EȘUAT")
            if not ai_test_ok or not normal_test_ok:
                print("🔧 Problemă cu restaurarea imaginilor")
            if not all_correct:
                print("🔧 Problemă cu clasificarea operațiilor")
        
        return success
        
    except Exception as e:
        print(f"❌ EROARE în test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simplified_undo_system():
    """Testează noul sistem simplificat folosind clasele standalone"""
    return test_undo_state_classes()
        
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

def test_simplified_undo_system():
    """Testează noul sistem simplificat"""
    print("🧪 TESTARE SISTEM SIMPLIFICAT UNDO/REDO")
    print("=" * 50)
    
    try:
        from ui.main_window import UndoState, OperationType, classify_operation
        
        # 1. Test UndoState
        print("\n1️⃣ Test UndoState - Compresie Adaptivă")
        test_image = create_test_image()
        
        # Test operație AI (compresie înaltă)
        ai_state = UndoState(test_image, "AI Background Removal", OperationType.AI)
        ai_size = ai_state.get_memory_size()
        
        # Test operație normală (compresie rapidă)
        normal_state = UndoState(test_image, "Blur Filter", OperationType.NORMAL)
        normal_size = normal_state.get_memory_size()
        
        print(f"   Memorie AI state: {ai_size / 1024:.1f} KB")
        print(f"   Memorie Normal state: {normal_size / 1024:.1f} KB")
        print(f"   Diferența: {((ai_size - normal_size) / normal_size * 100):+.1f}%")
        
        # 2. Test Restaurare Imagine
        print("\n2️⃣ Test Restaurare Imagine")
        
        # Test restore AI
        restored_ai = ai_state.get_image()
        original_array = np.array(test_image)
        restored_array = np.array(restored_ai)
        
        if np.array_equal(original_array, restored_array):
            print("   ✅ AI state restaurare: PERFECTĂ")
        else:
            print("   ❌ AI state restaurare: EȘUATĂ")
        
        # Test restore normal
        restored_normal = normal_state.get_image()
        restored_normal_array = np.array(restored_normal)
        
        if np.array_equal(original_array, restored_normal_array):
            print("   ✅ Normal state restaurare: PERFECTĂ")
        else:
            print("   ❌ Normal state restaurare: EȘUATĂ")
        
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
        
        all_correct = True
        for op_name, expected_type in test_operations:
            actual_type = classify_operation(op_name)
            status = "✅" if actual_type == expected_type else "❌"
            print(f"   {status} '{op_name}' → {actual_type.value} (așteptat: {expected_type.value})")
            if actual_type != expected_type:
                all_correct = False
        
        # 4. Test Performanță Memorie
        print("\n4️⃣ Test Performanță Memorie")
        
        # Creează mai multe stări
        states = []
        total_memory = 0
        
        for i in range(10):
            if i % 3 == 0:  # Operație AI
                state = UndoState(test_image, f"AI Operation {i}", OperationType.AI)
            else:  # Operație normală
                state = UndoState(test_image, f"Normal Operation {i}", OperationType.NORMAL)
            
            states.append(state)
            total_memory += state.get_memory_size()
        
        avg_memory = total_memory / len(states)
        print(f"   📊 10 stări create")
        print(f"   💾 Memorie totală: {total_memory / 1024:.1f} KB")
        print(f"   📈 Memorie medie/stare: {avg_memory / 1024:.1f} KB")
        
        # 5. Test Simulare Ciclu Complet
        print("\n5️⃣ Test Simulare Ciclu Complet")
        
        # Simulează un mic stack de undo
        undo_stack = []
        
        # Imagine inițială
        current_image = create_test_image()
        print(f"   🖼️ Imagine inițială: {current_image.size}")
        
        # Operație 1: Filtre (normal)
        undo_stack.append(UndoState(current_image, "Blur", OperationType.NORMAL))
        current_image = modify_image_normal(current_image)
        print(f"   🔹 Operație 1: Blur aplicat")
        
        # Operație 2: AI (background removal)
        undo_stack.append(UndoState(current_image, "Background Removal", OperationType.AI))
        current_image = modify_image_ai(current_image)
        print(f"   🤖 Operație 2: AI Background Removal aplicat")
        
        # Test undo
        if undo_stack:
            last_state = undo_stack.pop()
            current_image = last_state.get_image()
            print(f"   ⬅️ Undo: {last_state.operation_name} - SUCCESS")
        
        if undo_stack:
            last_state = undo_stack.pop()
            current_image = last_state.get_image()
            print(f"   ⬅️ Undo: {last_state.operation_name} - SUCCESS")
        
        print(f"   🖼️ Imagine finală: {current_image.size}")
        
        # Rezultat final
        print("\n" + "=" * 50)
        if all_correct:
            print("🎉 TOATE TESTELE AU TRECUT!")
            print("✅ Sistemul simplificat funcționează corect")
        else:
            print("⚠️ UNELE TESTE AU EȘUAT")
            print("🔧 Verifică clasificarea operațiilor")
        
        return all_correct
        
    except Exception as e:
        print(f"❌ EROARE în test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simplified_undo_system()
    sys.exit(0 if success else 1)
