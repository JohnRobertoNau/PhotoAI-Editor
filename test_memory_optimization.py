#!/usr/bin/env python3
"""
Test script to compare memory usage between old and new undo/redo system.
"""

import sys
import os
from PIL import Image, ImageDraw
import numpy as np
import tracemalloc
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_image(width=1000, height=1000):
    """Creates a test image with random colors."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Add some content
    for i in range(10):
        x1, y1 = np.random.randint(0, width-50, 2)
        x2, y2 = np.random.randint(0, height-50, 2)
        # Ensure x1 <= x2 and y1 <= y2
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        # Ensure minimum size
        if x2 - x1 < 20:
            x2 = x1 + 20
        if y2 - y1 < 20:
            y2 = y1 + 20
        color = tuple(np.random.randint(0, 255, 3))
        draw.rectangle([x1, y1, x2, y2], fill=color)
    
    return img

def test_old_system_memory():
    """Simulates the old system where full images are stored."""
    print("Testing OLD system (full images)...")
    tracemalloc.start()
    
    # Create base image
    base_img = create_test_image()
    undo_stack = []
    
    # Simulate 20 operations
    current_img = base_img.copy()
    for i in range(20):
        # Save full image copy (old method)
        undo_stack.append(current_img.copy())
        
        # Simulate an edit (modify a small area)
        draw = ImageDraw.Draw(current_img)
        x = np.random.randint(100, 850)  # Leave margin
        y = np.random.randint(100, 850)
        color = tuple(np.random.randint(0, 255, 3))
        draw.rectangle([x, y, x+50, y+50], fill=color)
        
        if i % 5 == 0:
            current, peak = tracemalloc.get_traced_memory()
            print(f"  Operation {i+1}: Current={current/1024/1024:.1f}MB, Peak={peak/1024/1024:.1f}MB")
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Final OLD system: {len(undo_stack)} operations")
    print(f"Memory - Current: {current/1024/1024:.1f}MB, Peak: {peak/1024/1024:.1f}MB")
    return current, peak

def calculate_image_diff(before_image, after_image):
    """Same function as in the optimized system."""
    import numpy as np
    
    if before_image.size != after_image.size:
        return {
            'type': 'size_change',
            'before_image': before_image,
            'after_image': after_image
        }
    
    before_array = np.array(before_image)
    after_array = np.array(after_image)
    
    if before_array.shape != after_array.shape:
        return {
            'type': 'format_change',
            'before_image': before_image,
            'after_image': after_image
        }
    
    if len(before_array.shape) == 3:
        diff = np.any(before_array != after_array, axis=2)
    else:
        diff = before_array != after_array
    
    if not np.any(diff):
        return None
    
    rows = np.any(diff, axis=1)
    cols = np.any(diff, axis=0)
    
    if not np.any(rows) or not np.any(cols):
        return None
    
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    padding = 5
    rmin = max(0, rmin - padding)
    cmin = max(0, cmin - padding)
    rmax = min(before_image.height - 1, rmax + padding)
    cmax = min(before_image.width - 1, cmax + padding)
    
    bbox = (cmin, rmin, cmax + 1, rmax + 1)
    
    return {
        'type': 'patch',
        'bbox': bbox,
        'before_patch': before_image.crop(bbox),
        'after_patch': after_image.crop(bbox)
    }

def test_new_system_memory():
    """Tests the new optimized system with diffs."""
    print("\nTesting NEW system (diff-based)...")
    tracemalloc.start()
    
    # Create base image
    base_img = create_test_image()
    undo_stack = []
    
    # Simulate 20 operations
    current_img = base_img.copy()
    previous_img = base_img.copy()
    
    for i in range(20):
        # Simulate an edit (modify a small area)
        draw = ImageDraw.Draw(current_img)
        x = np.random.randint(100, 850)  # Leave margin
        y = np.random.randint(100, 850)
        color = tuple(np.random.randint(0, 255, 3))
        draw.rectangle([x, y, x+50, y+50], fill=color)
        
        # Save only diff (new method)
        diff_data = calculate_image_diff(previous_img, current_img)
        if diff_data:
            undo_stack.append(diff_data)
        
        previous_img = current_img.copy()
        
        if i % 5 == 0:
            current, peak = tracemalloc.get_traced_memory()
            print(f"  Operation {i+1}: Current={current/1024/1024:.1f}MB, Peak={peak/1024/1024:.1f}MB")
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Final NEW system: {len(undo_stack)} operations")
    print(f"Memory - Current: {current/1024/1024:.1f}MB, Peak: {peak/1024/1024:.1f}MB")
    
    # Analyze patch sizes
    total_patch_pixels = 0
    full_image_pixels = base_img.width * base_img.height
    
    for diff in undo_stack:
        if diff.get('type') == 'patch':
            bbox = diff['bbox']
            patch_pixels = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            total_patch_pixels += patch_pixels * 2  # before + after patches
    
    compression_ratio = total_patch_pixels / (full_image_pixels * len(undo_stack)) * 100
    print(f"Compression ratio: {compression_ratio:.1f}% of original size")
    
    return current, peak

def main():
    print("Memory Usage Comparison: Old vs New Undo/Redo System")
    print("=" * 60)
    
    # Test old system
    old_current, old_peak = test_old_system_memory()
    
    # Small delay to clear memory
    time.sleep(1)
    
    # Test new system
    new_current, new_peak = test_new_system_memory()
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS COMPARISON:")
    print(f"Old system - Current: {old_current/1024/1024:.1f}MB, Peak: {old_peak/1024/1024:.1f}MB")
    print(f"New system - Current: {new_current/1024/1024:.1f}MB, Peak: {new_peak/1024/1024:.1f}MB")
    print(f"Memory savings - Current: {(old_current-new_current)/old_current*100:.1f}%")
    print(f"Memory savings - Peak: {(old_peak-new_peak)/old_peak*100:.1f}%")

if __name__ == "__main__":
    main()
