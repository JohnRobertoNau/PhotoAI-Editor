import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
from pathlib import Path
import os

from ..models.upscaler import ImageUpscaler
from ..models.background_remover import BackgroundRemover
from ..models.generative_fill import GenerativeFill
from ..models.image_recognition import ImageRecognition
from ..utils.image_processor import ImageProcessor

class PhotoEditorApp:
    def add_text_to_image(self):
        """Permite adăugarea de text pe imagine prin selectarea unei zone cu mouse-ul și introducerea textului cu alegerea culorii. Include editare interactivă."""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded!")
            return
        text_win = tk.Toplevel(self.root)
        text_win.title("Add Text")
        text_win.geometry("800x700")
        text_win.resizable(False, False)
        
        # Color selection dropdown at top
        color_options = {
            "White": "white",
            "Black": "black",
            "Red": "#ef4444",
            "Yellow": "#fde047",
            "Blue": "#3b82f6",
            "Green": "#22c55e",
            "Orange": "#f97316",
            "Purple": "#a21caf"
        }
        color_var = tk.StringVar(value="White")
        
        # Control panel at top
        controls_frame = tk.Frame(text_win)
        controls_frame.pack(pady=10)
        
        # Color selection
        color_frame = tk.Frame(controls_frame)
        color_frame.pack(side="left", padx=(0, 20))
        tk.Label(color_frame, text="Text color:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
        color_menu = tk.OptionMenu(color_frame, color_var, *color_options.keys())
        color_menu.config(font=("Arial", 10))
        color_menu.pack(side="left")
        
        # Font size control
        size_frame = tk.Frame(controls_frame)
        size_frame.pack(side="left", padx=(0, 20))
        tk.Label(size_frame, text="Font size:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
        size_var = tk.IntVar(value=60)
        size_spinbox = tk.Spinbox(size_frame, from_=20, to=200, textvariable=size_var, width=5)
        size_spinbox.pack(side="left")
        
        # Text input
        text_frame = tk.Frame(controls_frame)
        text_frame.pack(side="left")
        tk.Label(text_frame, text="Text:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
        text_var = tk.StringVar()
        text_entry = tk.Entry(text_frame, textvariable=text_var, width=20, font=("Arial", 12))
        text_entry.pack(side="left")
        
        disp_img = self.current_image.copy()
        disp_img.thumbnail((760, 560), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(disp_img)
        canvas = tk.Canvas(text_win, width=tk_img.width(), height=tk_img.height(), cursor="cross")
        canvas.pack(padx=20, pady=10)
        canvas.create_image(0, 0, anchor="nw", image=tk_img)
        
        # Variables for text management
        text_objects = []  # List of text objects with their properties
        selected_text = None
        dragging = False
        drag_start_x = drag_start_y = 0
        scale_x = self.current_image.width / tk_img.width()
        scale_y = self.current_image.height / tk_img.height()
        
        def add_text_at_position(x, y):
            """Add text at specified position on canvas"""
            text = text_var.get().strip()
            if not text:
                messagebox.showwarning("Warning", "Please enter some text!")
                return
                
            color = color_options.get(color_var.get(), "white")
            size = size_var.get()
            
            # Create text object on canvas for preview
            text_id = canvas.create_text(x, y, text=text, fill=color, font=("Arial", size), anchor="center")
            
            # Store text properties
            text_obj = {
                'id': text_id,
                'text': text,
                'x': x,
                'y': y,
                'color': color,
                'size': size,
                'real_x': int(x * scale_x),
                'real_y': int(y * scale_y)
            }
            text_objects.append(text_obj)
            
            # Create selection rectangle
            bbox = canvas.bbox(text_id)
            if bbox:
                rect_id = canvas.create_rectangle(bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5, 
                                                outline="blue", width=2, dash=(5,5))
                text_obj['rect_id'] = rect_id
        
        def update_text_display():
            """Update the visual representation of text"""
            nonlocal selected_text
            if selected_text:
                text_obj = selected_text
                color = color_options.get(color_var.get(), "white")
                size = size_var.get()
                text = text_var.get().strip()
                
                if text:
                    # Update canvas text
                    canvas.itemconfig(text_obj['id'], text=text, fill=color, font=("Arial", size))
                    
                    # Update stored properties
                    text_obj['text'] = text
                    text_obj['color'] = color
                    text_obj['size'] = size
                    text_obj['real_x'] = int(text_obj['x'] * scale_x)
                    text_obj['real_y'] = int(text_obj['y'] * scale_y)
                    
                    # Update selection rectangle
                    bbox = canvas.bbox(text_obj['id'])
                    if bbox and 'rect_id' in text_obj:
                        canvas.coords(text_obj['rect_id'], bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5)
        
        def on_canvas_click(event):
            nonlocal selected_text, dragging, drag_start_x, drag_start_y
            
            # Check if clicking on existing text
            clicked_item = canvas.find_closest(event.x, event.y)[0]
            clicked_text = None
            
            for text_obj in text_objects:
                if text_obj['id'] == clicked_item:
                    clicked_text = text_obj
                    break
            
            if clicked_text:
                # Select existing text
                selected_text = clicked_text
                text_var.set(clicked_text['text'])
                color_var.set([k for k, v in color_options.items() if v == clicked_text['color']][0])
                size_var.set(clicked_text['size'])
                
                # Prepare for dragging
                dragging = True
                drag_start_x = event.x
                drag_start_y = event.y
                
                # Highlight selected text
                for text_obj in text_objects:
                    if 'rect_id' in text_obj:
                        canvas.itemconfig(text_obj['rect_id'], outline="gray" if text_obj != selected_text else "blue")
            else:
                # Add new text at click position
                add_text_at_position(event.x, event.y)
        
        def on_canvas_drag(event):
            nonlocal dragging, drag_start_x, drag_start_y, selected_text
            
            if dragging and selected_text:
                # Calculate movement
                dx = event.x - drag_start_x
                dy = event.y - drag_start_y
                
                # Move text
                canvas.move(selected_text['id'], dx, dy)
                if 'rect_id' in selected_text:
                    canvas.move(selected_text['rect_id'], dx, dy)
                
                # Update stored position
                selected_text['x'] += dx
                selected_text['y'] += dy
                selected_text['real_x'] = int(selected_text['x'] * scale_x)
                selected_text['real_y'] = int(selected_text['y'] * scale_y)
                
                # Update drag start position
                drag_start_x = event.x
                drag_start_y = event.y
        
        def on_canvas_release(event):
            nonlocal dragging
            dragging = False
        
        def delete_selected_text():
            nonlocal selected_text
            if selected_text:
                canvas.delete(selected_text['id'])
                if 'rect_id' in selected_text:
                    canvas.delete(selected_text['rect_id'])
                text_objects.remove(selected_text)
                selected_text = None
                text_var.set("")
        
        def apply_text_to_image():
            """Apply all text objects to the actual image"""
            if not text_objects:
                messagebox.showwarning("Warning", "No text to apply!")
                return
            
            # Create description of texts being added
            text_descriptions = [text_obj['text'][:20] + "..." if len(text_obj['text']) > 20 else text_obj['text'] for text_obj in text_objects]
            if len(text_descriptions) == 1:
                operation_name = f"Add Text: '{text_descriptions[0]}'"
            else:
                operation_name = f"Add {len(text_descriptions)} Texts"
                
            self.push_undo(operation_name)
            img = self.current_image.copy()
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            for text_obj in text_objects:
                # Scale font size to match the actual image size
                scaled_font_size = int(text_obj['size'] * max(scale_x, scale_y))
                
                # Try to load a TrueType font
                font = None
                font_paths = [
                    "arial.ttf",
                    "C:/Windows/Fonts/arial.ttf", 
                    "/System/Library/Fonts/Arial.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                ]
                
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, size=scaled_font_size)
                        break
                    except:
                        continue
                
                if font is None:
                    font = ImageFont.load_default()
                
                # Get text dimensions for centering
                try:
                    bbox = draw.textbbox((0, 0), text_obj['text'], font=font)
                    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                except AttributeError:
                    w, h = draw.textsize(text_obj['text'], font=font)
                
                # Draw text centered at position
                tx = text_obj['real_x'] - w//2
                ty = text_obj['real_y'] - h//2
                draw.text((tx, ty), text_obj['text'], fill=text_obj['color'], font=font)
            
            self.current_image = img
            self._current_operation = operation_name  # Track current operation
            self.display_image()
            self.update_info(f"Applied {len(text_objects)} text element(s) to image")
            text_win.destroy()
        
        def on_cancel():
            text_win.destroy()
        
        # Bind events to update text in real-time
        text_var.trace('w', lambda *args: update_text_display())
        color_var.trace('w', lambda *args: update_text_display())
        size_var.trace('w', lambda *args: update_text_display())
        
        # Bind canvas events
        canvas.bind("<Button-1>", on_canvas_click)
        canvas.bind("<B1-Motion>", on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", on_canvas_release)
        
        # Instructions
        instructions = tk.Label(text_win, text="Click to add text • Click text to select • Drag to move • Modify controls to edit", 
                              font=("Arial", 10), fg="gray")
        instructions.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(text_win)
        btn_frame.pack(pady=10)
        apply_btn = tk.Button(btn_frame, text="Apply to Image", width=15, command=apply_text_to_image, 
                             font=("Arial", 10), bg="#4CAF50", fg="white")
        apply_btn.pack(side="left", padx=5)
        delete_btn = tk.Button(btn_frame, text="Delete Selected", width=15, command=delete_selected_text, 
                              font=("Arial", 10), bg="#f44336", fg="white")
        delete_btn.pack(side="left", padx=5)
        cancel_btn = tk.Button(btn_frame, text="Cancel", width=12, command=on_cancel, font=("Arial", 10))
        cancel_btn.pack(side="left", padx=5)
        
        text_win.mainloop()
    
    def _calculate_image_diff(self, before_image, after_image):
        """Calculează diferențele între două imagini și returnează doar zona modificată."""
        import numpy as np
        
        # Convert to same size if different
        if before_image.size != after_image.size:
            return {
                'type': 'size_change',
                'before_image': before_image,
                'after_image': after_image
            }
        
        # Convert to numpy arrays for comparison
        before_array = np.array(before_image)
        after_array = np.array(after_image)
        
        # Find differences
        if before_array.shape != after_array.shape:
            return {
                'type': 'format_change',
                'before_image': before_image,
                'after_image': after_image
            }
        
        # Calculate pixel differences
        if len(before_array.shape) == 3:
            diff = np.any(before_array != after_array, axis=2)
        else:
            diff = before_array != after_array
        
        # If no differences, return None
        if not np.any(diff):
            return None
        
        # Find bounding box of changes
        rows = np.any(diff, axis=1)
        cols = np.any(diff, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return None
        
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        # Add some padding
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
    
    def _apply_diff(self, base_image, diff_data, reverse=False):
        """Aplică diferențele pe o imagine de bază."""
        if not diff_data:
            return base_image
        
        if diff_data['type'] == 'no_change':
            return base_image
        
        if diff_data['type'] == 'full_image':
            return diff_data['image'].copy()
        
        if diff_data['type'] in ['size_change', 'format_change']:
            if reverse:
                return diff_data['before_image'].copy()
            else:
                return diff_data['after_image'].copy()
        
        if diff_data['type'] == 'patch':
            result = base_image.copy()
            bbox = diff_data['bbox']
            
            if reverse:
                patch = diff_data['before_patch']
            else:
                patch = diff_data['after_patch']
            
            result.paste(patch, (bbox[0], bbox[1]))
            return result
        
        return base_image
    
    def get_memory_usage_info(self):
        """Returnează informații despre utilizarea memoriei pentru undo/redo."""
        import sys
        
        if not hasattr(self, '_undo_stack') or not hasattr(self, '_redo_stack'):
            return "Undo/Redo: Not initialized"
        
        undo_count = len(self._undo_stack)
        redo_count = len(self._redo_stack)
        
        # Estimate memory usage
        total_memory = 0
        for item in self._undo_stack:
            if item.get('type') == 'full_image' and 'image' in item:
                # Full image size
                img = item['image']
                total_memory += img.width * img.height * len(img.getbands()) * 4  # 4 bytes per channel
            elif item.get('type') == 'patch' and 'before_patch' in item and 'after_patch' in item:
                # Patch size
                before = item['before_patch']
                after = item['after_patch']
                total_memory += (before.width * before.height + after.width * after.height) * len(before.getbands()) * 4
        
        for item in self._redo_stack:
            if item.get('type') == 'full_image' and 'image' in item:
                img = item['image']
                total_memory += img.width * img.height * len(img.getbands()) * 4
            elif item.get('type') == 'patch' and 'before_patch' in item and 'after_patch' in item:
                before = item['before_patch']
                after = item['after_patch']
                total_memory += (before.width * before.height + after.width * after.height) * len(before.getbands()) * 4
        
        memory_mb = total_memory / (1024 * 1024)
        
        return f"Undo: {undo_count} | Redo: {redo_count} | Memory: {memory_mb:.1f} MB"
    
    def push_undo(self, operation_name="Operation"):
        if not hasattr(self, '_undo_stack'):
            self._undo_stack = []
        if not hasattr(self, '_undo_operations'):
            self._undo_operations = []
        if not hasattr(self, '_redo_stack'):
            self._redo_stack = []
        if not hasattr(self, '_redo_operations'):
            self._redo_operations = []
        
        if self.current_image:
            # NEW: Save only differences instead of full images
            if hasattr(self, '_previous_image') and self._previous_image:
                diff_data = self._calculate_image_diff(self._previous_image, self.current_image)
                if diff_data:
                    self._undo_stack.append(diff_data)
                else:
                    # No changes detected, don't save anything
                    return
            else:
                # First image - save full image as baseline
                self._undo_stack.append({
                    'type': 'full_image',
                    'image': self.current_image.copy()
                })
            
            self._undo_operations.append(operation_name)
            
            # Update previous image reference
            self._previous_image = self.current_image.copy()
            
            # Limit stack size if needed (can afford more entries now)
            if len(self._undo_stack) > 50:
                self._undo_stack.pop(0)
                self._undo_operations.pop(0)
                
            # Clear redo stack when new operation is added
            self._redo_stack.clear()
            self._redo_operations.clear()
        self.update_undo_redo_buttons()

    def undo(self):
        if hasattr(self, '_undo_stack') and self._undo_stack:
            if not hasattr(self, '_redo_stack'):
                self._redo_stack = []
            if not hasattr(self, '_redo_operations'):
                self._redo_operations = []
            
            # Get the diff data to undo
            diff_data = self._undo_stack.pop()
            undone_operation = self._undo_operations.pop() if hasattr(self, '_undo_operations') and self._undo_operations else "Unknown operation"
            
            if self.current_image:
                # Save current state for redo (as diff)
                if hasattr(self, '_previous_image') and self._previous_image:
                    redo_diff = self._calculate_image_diff(self._previous_image, self.current_image)
                    if redo_diff:
                        self._redo_stack.append(redo_diff)
                else:
                    # Save as full image if no previous reference
                    self._redo_stack.append({
                        'type': 'full_image',
                        'image': self.current_image.copy()
                    })
                
                current_op = getattr(self, '_current_operation', "Operation")
                self._redo_operations.append(current_op)
                
                # Apply the reverse diff to get previous state
                if hasattr(self, '_previous_image') and self._previous_image:
                    self.current_image = self._apply_diff(self._previous_image, diff_data, reverse=True)
                else:
                    # If it's a full image diff, just use it directly
                    if diff_data.get('type') == 'full_image':
                        self.current_image = diff_data['image'].copy()
                
                # Update previous image reference
                self._previous_image = self.current_image.copy()
            
            self.display_image()
            self.update_image_info()
            self.update_info(f"⬅️ Undo: {undone_operation}")
        self.update_undo_redo_buttons()

    def redo(self):
        if hasattr(self, '_redo_stack') and self._redo_stack:
            if not hasattr(self, '_undo_stack'):
                self._undo_stack = []
            if not hasattr(self, '_undo_operations'):
                self._undo_operations = []
            
            # Get the diff data to redo
            diff_data = self._redo_stack.pop()
            redone_operation = self._redo_operations.pop() if hasattr(self, '_redo_operations') and self._redo_operations else "Unknown operation"
            
            if self.current_image:
                # Save current state for undo (as diff)
                if hasattr(self, '_previous_image') and self._previous_image:
                    undo_diff = self._calculate_image_diff(self._previous_image, self.current_image)
                    if undo_diff:
                        self._undo_stack.append(undo_diff)
                else:
                    # Save as full image if no previous reference
                    self._undo_stack.append({
                        'type': 'full_image',
                        'image': self.current_image.copy()
                    })
                
                current_op = getattr(self, '_current_operation', "Operation")
                self._undo_operations.append(current_op)
                
                # Apply the diff to get the redo state
                if hasattr(self, '_previous_image') and self._previous_image:
                    self.current_image = self._apply_diff(self._previous_image, diff_data, reverse=False)
                else:
                    # If it's a full image diff, just use it directly
                    if diff_data.get('type') == 'full_image':
                        self.current_image = diff_data['image'].copy()
                
                # Update previous image reference
                self._previous_image = self.current_image.copy()
            
            self._current_operation = redone_operation
            self.display_image()
            self.update_image_info()
            self.update_info(f"➡️ Redo: {redone_operation}")
        self.update_undo_redo_buttons()


    def apply_filter(self):
        """Displays a dropdown for filter selection and applies the effect to the current image."""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return

        import tkinter.simpledialog
        from PIL import ImageFilter, ImageOps, ImageEnhance

        FILTERS = {
            "Grayscale": lambda img: ImageOps.grayscale(img).convert("RGB"),
            "Sepia": lambda img: ImageOps.colorize(ImageOps.grayscale(img), '#704214', '#C0C080'),
            "Invert": lambda img: ImageOps.invert(img.convert("RGB")),
            "Blur": lambda img: img.filter(ImageFilter.GaussianBlur(radius=2)),
            "Sharpen": lambda img: img.filter(ImageFilter.SHARPEN),
            "Contrast+": lambda img: ImageEnhance.Contrast(img).enhance(1.8),
            "Brightness+": lambda img: ImageEnhance.Brightness(img).enhance(1.5),
            "Color+": lambda img: ImageEnhance.Color(img).enhance(1.5),
            "Edge Enhance": lambda img: img.filter(ImageFilter.EDGE_ENHANCE),
            "Emboss": lambda img: img.filter(ImageFilter.EMBOSS),
            "Smooth": lambda img: img.filter(ImageFilter.SMOOTH),
        }

        # Custom dialog with dropdown
        class FilterDialog(tkinter.simpledialog.Dialog):
            def body(self, master):
                tk.Label(master, text="Select filter:").pack(padx=10, pady=5)
                self.var = tk.StringVar(value=list(FILTERS.keys())[0])
                self.dropdown = tk.OptionMenu(master, self.var, *FILTERS.keys())
                self.dropdown.pack(padx=10, pady=5)
                return self.dropdown
            def apply(self):
                self.result = self.var.get()

        dialog = FilterDialog(self.root, title="Apply Filter")
        if dialog.result and dialog.result in FILTERS:
            try:
                # Save for undo with specific filter name
                self.push_undo(f"Apply Filter: {dialog.result}")
                filtered = FILTERS[dialog.result](self.current_image)
                self.current_image = filtered
                self._current_operation = f"Apply Filter: {dialog.result}"  # Track current operation
                self.display_image()
                self.update_info(f"✅ Filter '{dialog.result}' applied!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not apply filter: {e}")
    def __init__(self):
        # Configure theme for customtkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create root with native drag and drop support
        self.root = ctk.CTk()
        self.root.title("AI Photo Editor")
        self.root.geometry("1200x800")
        
        # State variables
        self.current_image = None
        self.original_image = None
        self.image_path = None
        self.saved_files_history = []  # Lista pentru ultimele 5 fișiere salvate
        self.history_file = "recent_files.json"  # Fișier pentru persistența istoricului
        
        # Încarcă istoricul salvat
        self.load_history_from_file()
        
        # Initialize AI models
        self.init_ai_models()
        
        # Create interface
        self.create_widgets()
        
        # Configure drag and drop
        self.setup_drag_drop()


    def init_ai_models(self):
        """Initializes AI models."""
        try:
            self.upscaler = ImageUpscaler()
            self.bg_remover = BackgroundRemover()
            self.gen_fill = GenerativeFill()
            self.img_recognition = ImageRecognition()
            self.image_processor = ImageProcessor()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load AI models: {e}")
    
    def create_widgets(self):
        """Creates UI elements."""
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Toolbar
        self.create_toolbar(main_frame)
        
        # Workspace area
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Left panel - controls
        self.create_control_panel(content_frame)
        
        # Center panel - image
        self.create_image_panel(content_frame)
        
        # Right panel - information
        self.create_info_panel(content_frame)
    
    def create_toolbar(self, parent):
        """Creates the main toolbar with buttons."""
        toolbar = ctk.CTkFrame(parent)
        toolbar.pack(fill="x", pady=(0, 10))
        
        # Button for loading image
        load_btn = ctk.CTkButton(
            toolbar, 
            text="Load Image",
            command=self.load_image,
            width=120
        )
        load_btn.pack(side="left", padx=5, pady=5)
        
        # Button for reset
        reset_btn = ctk.CTkButton(
            toolbar,
            text="Reset",
            command=self.reset_image,
            width=80
        )
        reset_btn.pack(side="left", padx=5, pady=5)
        
        # Button for file history
        history_btn = ctk.CTkButton(
            toolbar,
            text="Recent Files",
            command=self.show_file_history,
            width=120
        )
        history_btn.pack(side="left", padx=5, pady=5)
        
        # Button for export
        export_btn = ctk.CTkButton(
            toolbar,
            text="Export as...",
            command=self.export_image_as,
            width=120
        )
        export_btn.pack(side="left", padx=5, pady=5)
    
    def create_control_panel(self, parent):
        """Creates the AI and image adjustment control panel."""
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(side="left", fill="y", padx=(0, 10))

        # Title
        title = ctk.CTkLabel(control_frame, text="AI Operations", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # --- Sliders for brightness, contrast, saturation ---
        from PIL import ImageEnhance
        self._slider_original = None  # To keep the original image for adjustments

        def on_slider_change(event=None):
            if self._slider_original is None:
                return
            img = self._slider_original.copy()
            brightness = brightness_slider.get()
            img = ImageEnhance.Brightness(img).enhance(brightness)
            contrast = contrast_slider.get()
            img = ImageEnhance.Contrast(img).enhance(contrast)
            saturation = saturation_slider.get()
            img = ImageEnhance.Color(img).enhance(saturation)
            self.current_image = img
            self.display_image()

        def on_slider_start(event=None):
            if self.current_image:
                self._slider_original = self.current_image.copy()

        def on_slider_release(event=None):
            if self._slider_original is None:
                return
            # Save for undo
            self.push_undo("Adjust Image")
            # Final update (optional, since on_slider_change already updates)
            img = self._slider_original.copy()
            brightness = brightness_slider.get()
            img = ImageEnhance.Brightness(img).enhance(brightness)
            contrast = contrast_slider.get()
            img = ImageEnhance.Contrast(img).enhance(contrast)
            saturation = saturation_slider.get()
            img = ImageEnhance.Color(img).enhance(saturation)
            self.current_image = img
            self._current_operation = "Adjust Image"
            self.display_image()
            self._slider_original = None

        def on_slider_start(event=None):
            if self.current_image:
                self._slider_original = self.current_image.copy()

        def reset_sliders():
            brightness_slider.set(1.0)
            contrast_slider.set(1.0)
            saturation_slider.set(1.0)
            self._slider_original = None
            # Reset image to original (if exists)
            if self.original_image:
                self.push_undo("Reset Sliders")
                self.current_image = self.original_image.copy()
                self._current_operation = "Reset Sliders"
                self.display_image()

        self._reset_sliders_ref = reset_sliders  # reference for global reset

        sliders_label = ctk.CTkLabel(control_frame, text="Adjust Image", font=("Arial", 13, "bold"))
        sliders_label.pack(pady=(10, 0))

        brightness_slider = ctk.CTkSlider(control_frame, from_=0.2, to=2.0, number_of_steps=36, width=140)
        brightness_slider.set(1.0)
        brightness_label = ctk.CTkLabel(control_frame, text="Brightness")
        brightness_label.pack(pady=(8,0))
        brightness_slider.pack(pady=(0,0))
        brightness_slider.bind("<ButtonPress-1>", on_slider_start)
        brightness_slider.bind("<B1-Motion>", on_slider_change)
        brightness_slider.bind("<ButtonRelease-1>", on_slider_release)

        contrast_slider = ctk.CTkSlider(control_frame, from_=0.2, to=2.0, number_of_steps=36, width=140)
        contrast_slider.set(1.0)
        contrast_label = ctk.CTkLabel(control_frame, text="Contrast")
        contrast_label.pack(pady=(8,0))
        contrast_slider.pack(pady=(0,0))
        contrast_slider.bind("<ButtonPress-1>", on_slider_start)
        contrast_slider.bind("<B1-Motion>", on_slider_change)
        contrast_slider.bind("<ButtonRelease-1>", on_slider_release)

        saturation_slider = ctk.CTkSlider(control_frame, from_=0.0, to=2.0, number_of_steps=40, width=140)
        saturation_slider.set(1.0)
        saturation_label = ctk.CTkLabel(control_frame, text="Saturation")
        saturation_label.pack(pady=(8,0))
        saturation_slider.pack(pady=(0,8))
        saturation_slider.bind("<ButtonPress-1>", on_slider_start)
        saturation_slider.bind("<B1-Motion>", on_slider_change)
        saturation_slider.bind("<ButtonRelease-1>", on_slider_release)

        # --- Rotate Button ---
        rotate_btn = ctk.CTkButton(control_frame, text="Rotate 90°", width=150, height=38, font=("Arial", 13, "bold"), corner_radius=12, fg_color="#fbbf24", hover_color="#f59e42", command=self.rotate_image)
        rotate_btn.pack(pady=5)

        # --- Mirror Button ---
        mirror_btn = ctk.CTkButton(control_frame, text="Mirror", width=150, height=38, font=("Arial", 13, "bold"), corner_radius=12, fg_color="#a3e635", hover_color="#65a30d", command=self.mirror_image)
        mirror_btn.pack(pady=5)

        # --- Flip Vertical Button ---
        flip_v_btn = ctk.CTkButton(control_frame, text="Flip Vertical", width=150, height=38, font=("Arial", 13, "bold"), corner_radius=12, fg_color="#f472b6", hover_color="#db2777", command=self.flip_vertical_image)
        flip_v_btn.pack(pady=5)

        # --- Crop Button ---
        crop_btn = ctk.CTkButton(control_frame, text="Crop", width=150, height=38, font=("Arial", 13, "bold"), corner_radius=122, fg_color="#38bdf8", hover_color="#0ea5e9", command=self.crop_image)
        crop_btn.pack(pady=5)

        # --- Aspect Ratio Crop Button (Dropdown) ---
        def crop_aspect_ratio():
            if not self.current_image:
                messagebox.showwarning("Warning", "No image loaded!")
                return
            # Dropdown dialog for aspect ratio
            aspect_win = tk.Toplevel(self.root)
            aspect_win.title("Select Aspect Ratio")
            aspect_win.geometry("280x180")
            aspect_win.resizable(False, False)
            tk.Label(aspect_win, text="Choose aspect ratio:", font=("Arial", 12)).pack(pady=(18, 8))
            aspect_options = [
                "1:1", "3:4", "4:3", "9:16", "16:9", "2:3", "3:2", "5:4", "4:5", "7:5", "5:7", "21:9", "1:2", "2:1"
            ]
            var = tk.StringVar(value="3:4")
            dropdown = tk.OptionMenu(aspect_win, var, *aspect_options)
            dropdown.pack(pady=(0, 10))
            btn_frame = tk.Frame(aspect_win)
            btn_frame.pack(pady=5)
            def on_ok():
                aspect = var.get()
                aspect_win.destroy()
                w, h = self.current_image.width, self.current_image.height
                # Parse aspect ratio string
                try:
                    num, den = aspect.split(":")
                    num = float(num)
                    den = float(den)
                    target_ratio = num / den
                except Exception:
                    messagebox.showwarning("Warning", "Invalid aspect ratio!")
                    return
                img_ratio = w / h
                if img_ratio > target_ratio:
                    new_w = int(h * target_ratio)
                    new_h = h
                else:
                    new_w = w
                    new_h = int(w / target_ratio)
                left = (w - new_w) // 2
                top = (h - new_h) // 2
                right = left + new_w
                bottom = top + new_h
                self.push_undo("Aspect Ratio Crop")
                self.current_image = self.current_image.crop((left, top, right, bottom))
                self._current_operation = "Aspect Ratio Crop"
                self.display_image()
                self.update_info(f"Image cropped to {aspect} aspect ratio.")
            ok_btn = tk.Button(btn_frame, text="Crop", width=10, command=on_ok)
            ok_btn.pack(side="left", padx=5)
            cancel_btn = tk.Button(btn_frame, text="Cancel", width=10, command=aspect_win.destroy)
            cancel_btn.pack(side="left", padx=5)
            aspect_win.transient(self.root)
            aspect_win.grab_set()
            self.root.wait_window(aspect_win)

        crop_aspect_btn = ctk.CTkButton(control_frame, text="Aspect Ratio Crop", width=150, height=38, font=("Arial", 13, "bold"), corner_radius=12, fg_color="#818cf8", hover_color="#6366f1", command=crop_aspect_ratio)
        crop_aspect_btn.pack(pady=5)

        # --- AI Operations Frame ---
        ai_frame = ctk.CTkFrame(control_frame)
        ai_frame.pack(pady=(10, 5), padx=5, fill="x")
        
        ai_title = ctk.CTkLabel(ai_frame, text="AI Operations", font=("Arial", 13, "bold"))
        ai_title.pack(pady=(10, 5))
        
        upscale_btn = ctk.CTkButton(
            ai_frame,
            text="Upscale Image",
            command=self.upscale_image,
            width=140
        )
        upscale_btn.pack(pady=3)

        bg_remove_btn = ctk.CTkButton(
            ai_frame,
            text="Remove Background",
            command=self.remove_background,
            width=140
        )
        bg_remove_btn.pack(pady=3)

        bg_replace_btn = ctk.CTkButton(
            ai_frame,
            text="Replace Background",
            command=self.replace_background,
            width=140
        )
        bg_replace_btn.pack(pady=3)

        gen_fill_btn = ctk.CTkButton(
            ai_frame,
            text="Generative Fill",
            command=self.generative_fill,
            width=140
        )
        gen_fill_btn.pack(pady=3)

        recognize_btn = ctk.CTkButton(
            ai_frame,
            text="Recognize Image",
            command=self.recognize_image,
            width=140
        )
        recognize_btn.pack(pady=(3, 10))

        # --- Image Tools Frame ---
        tools_frame = ctk.CTkFrame(control_frame)
        tools_frame.pack(pady=5, padx=5, fill="x")
        
        tools_title = ctk.CTkLabel(tools_frame, text="Image Tools", font=("Arial", 13, "bold"))
        tools_title.pack(pady=(10, 5))
        
        add_text_btn = ctk.CTkButton(
            tools_frame,
            text="Add Text",
            command=self.add_text_to_image,
            width=140
        )
        add_text_btn.pack(pady=3)

        filter_btn = ctk.CTkButton(
            tools_frame,
            text="Apply Filter",
            command=self.apply_filter,
            width=140
        )
        filter_btn.pack(pady=3)

        gen_fill_simple_btn = ctk.CTkButton(
            tools_frame,
            text="Generative Fill (No AI)",
            command=self.generative_fill_simple,
            width=140
        )
        gen_fill_simple_btn.pack(pady=(3, 10))

        self.progress = ctk.CTkProgressBar(control_frame)
        self.progress.pack(pady=20, padx=10, fill="x")
        self.progress.set(0)
    def replace_background(self):
        """Removes the background and allows choosing a new background for the image."""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return

        def worker():
            try:
                self.progress.set(0.1)
                self.update_info("Removing background...")
                # Save for undo before starting
                self.push_undo("Replace Background")
                
                # Remove background (get RGBA image with transparency)
                fg_img = self.bg_remover.remove_background(self.current_image)

                self.progress.set(0.4)
                self.update_info("Select a new background image...")
                # Select background image
                bg_path = filedialog.askopenfilename(
                    title="Select background image",
                    filetypes=[
                        ("All Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
                        ("PNG", "*.png"),
                        ("JPEG", "*.jpg *.jpeg"),
                        ("All files", "*.*")
                    ]
                )
                if not bg_path:
                    self.update_info("Background replace cancelled.")
                    self.progress.set(0)
                    return

                bg_img = Image.open(bg_path).convert("RGBA")

                # Resize background to foreground size
                bg_img = bg_img.resize(fg_img.size, Image.LANCZOS)

                # Ensure foreground is RGBA
                if fg_img.mode != "RGBA":
                    fg_img = fg_img.convert("RGBA")

                # Combine foreground with background
                result = Image.alpha_composite(bg_img, fg_img)

                self.current_image = result.convert("RGB")
                self._current_operation = "Replace Background"
                self.display_image()
                self.progress.set(1.0)
                self.update_info("Background replaced successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Background replace failed: {e}")
            finally:
                self.progress.set(0)

        threading.Thread(target=worker, daemon=True).start()
    
    def create_image_panel(self, parent):
        """Creates the panel for displaying original vs. edited image comparison."""
        self.image_frame = ctk.CTkFrame(parent)
        self.image_frame.pack(side="left", fill="both", expand=True)

        # Frames for comparison
        compare_frame = ctk.CTkFrame(self.image_frame)
        compare_frame.pack(expand=True, fill="both", padx=0, pady=0)

        # Left panel - Edited
        left_panel = ctk.CTkFrame(compare_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0,2))
        # Header frame pentru titlu + zoom (EDITED)
        edited_header_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        edited_header_frame.pack(fill="x", pady=(0,2))
        left_label_title = ctk.CTkLabel(edited_header_frame, text="Edited", font=("Arial", 12, "bold"))
        left_label_title.pack(side="left", padx=(0,4))
        # Zoom controls sus, langa titlu (doar +, -, Reset)
        zoom_btn_frame_edit = ctk.CTkFrame(edited_header_frame, fg_color="transparent")
        zoom_btn_frame_edit.pack(side="left")
        def zoom_in_edit():
            self._zoom_factor_edit = min(self._zoom_factor_edit * 1.2, self._zoom_max)
            self.display_image()
        def zoom_out_edit():
            self._zoom_factor_edit = max(self._zoom_factor_edit / 1.2, self._zoom_min)
            self.display_image()
        def reset_zoom_edit():
            self._zoom_factor_edit = self._zoom_default
            self.display_image()
        zoom_in_btn_edit = ctk.CTkButton(zoom_btn_frame_edit, text="+", width=28, height=22, command=zoom_in_edit)
        zoom_in_btn_edit.pack(side="left", padx=1)
        zoom_out_btn_edit = ctk.CTkButton(zoom_btn_frame_edit, text="-", width=28, height=22, command=zoom_out_edit)
        zoom_out_btn_edit.pack(side="left", padx=1)
        reset_zoom_btn_edit = ctk.CTkButton(zoom_btn_frame_edit, text="Reset", width=48, height=22, command=reset_zoom_edit)
        reset_zoom_btn_edit.pack(side="left", padx=1)
        # --- ZOOM state for both images ---
        self._zoom_factor_edit = 1.0
        self._zoom_factor_orig = 1.0
        self._zoom_min = 0.2
        self._zoom_max = 5.0
        self._zoom_default = 1.0
        self._zoom_display_size = (600, 400)
        # --- Frame pentru imagine editată + zoom controls ---
        edited_img_frame = ctk.CTkFrame(left_panel)
        edited_img_frame.pack(expand=True, fill="both")
        self.edited_image_label = ctk.CTkLabel(edited_img_frame, text="No image loaded.", font=("Arial", 12))
        self.edited_image_label.pack(expand=True, fill="both")

        # ...existing code...

        # Right panel - Original
        right_panel = ctk.CTkFrame(compare_frame)
        right_panel.pack(side="left", fill="both", expand=True, padx=(2,0))
        # Header frame pentru titlu + zoom (ORIGINAL)
        original_header_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        original_header_frame.pack(fill="x", pady=(0,2))
        right_label_title = ctk.CTkLabel(original_header_frame, text="Original", font=("Arial", 12, "bold"))
        right_label_title.pack(side="left", padx=(0,4))
        # Zoom controls sus, langa titlu (doar +, -, Reset)
        zoom_btn_frame_orig = ctk.CTkFrame(original_header_frame, fg_color="transparent")
        zoom_btn_frame_orig.pack(side="left")
        def zoom_in_orig():
            self._zoom_factor_orig = min(self._zoom_factor_orig * 1.2, self._zoom_max)
            self.display_image()
        def zoom_out_orig():
            self._zoom_factor_orig = max(self._zoom_factor_orig / 1.2, self._zoom_min)
            self.display_image()
        def reset_zoom_orig():
            self._zoom_factor_orig = self._zoom_default
            self.display_image()
        zoom_in_btn_orig = ctk.CTkButton(zoom_btn_frame_orig, text="+", width=28, height=22, command=zoom_in_orig)
        zoom_in_btn_orig.pack(side="left", padx=1)
        zoom_out_btn_orig = ctk.CTkButton(zoom_btn_frame_orig, text="-", width=28, height=22, command=zoom_out_orig)
        zoom_out_btn_orig.pack(side="left", padx=1)
        reset_zoom_btn_orig = ctk.CTkButton(zoom_btn_frame_orig, text="Reset", width=48, height=22, command=reset_zoom_orig)
        reset_zoom_btn_orig.pack(side="left", padx=1)
        # --- Frame pentru imagine originală + zoom controls ---
        original_img_frame = ctk.CTkFrame(right_panel)
        original_img_frame.pack(expand=True, fill="both")
        self.original_image_label = ctk.CTkLabel(original_img_frame, text="No image loaded.", font=("Arial", 12))
        self.original_image_label.pack(expand=True, fill="both")

        # ...existing code...
    
    def create_info_panel(self, parent):
        """Creates the information panel."""
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(side="right", fill="y", padx=(10, 0))
        
        # Title
        title = ctk.CTkLabel(info_frame, text="Information", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # --- Undo/Redo buttons ---
        undo_redo_frame = ctk.CTkFrame(info_frame)
        undo_redo_frame.pack(pady=(0, 10))
        self.undo_btn = ctk.CTkButton(undo_redo_frame, text="Undo", width=65, command=self.undo)
        self.redo_btn = ctk.CTkButton(undo_redo_frame, text="Redo", width=65, command=self.redo)
        self.undo_btn.pack(side="left", padx=(0, 5))
        self.redo_btn.pack(side="left", padx=(5, 0))
        self.edit_progress_label = ctk.CTkLabel(undo_redo_frame, text="")
        self.edit_progress_label.pack(side="left", padx=(10,0))
        
        # Text widget for displaying information (read-only)
        self.info_text = ctk.CTkTextbox(info_frame, width=250, height=400)
        self.info_text.pack(pady=10, padx=10, fill="both", expand=True)
        self.info_text.configure(state="disabled")
        self.update_info("Load an image to see details.")
    
    def setup_drag_drop(self):
        """(Removed) No longer configures paste path or clipboard button."""
        pass
    
    # paste_image_path removed
    
    # add_quick_load_button removed
    
    # Removed hover handlers for drag and drop, no longer needed
    
    def is_valid_image_file(self, file_path):
        """Checks if the file is a valid image."""
        try:
            if not file_path or not isinstance(file_path, str):
                return False
                
            # Check if path exists
            path_obj = Path(file_path)
            if not path_obj.exists() or not path_obj.is_file():
                return False
                
            valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
            file_extension = path_obj.suffix.lower()
            return file_extension in valid_extensions
        except:
            return False
    
    def load_image_from_path(self, file_path):
        """Loads image from the specified path."""
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            self.current_image = self.original_image.copy()
            
            # Initialize diff tracking
            self._previous_image = self.current_image.copy()
            
            # Clear undo/redo stacks when loading new image
            if hasattr(self, '_undo_stack'):
                self._undo_stack.clear()
            if hasattr(self, '_undo_operations'):
                self._undo_operations.clear()
            if hasattr(self, '_redo_stack'):
                self._redo_stack.clear()
            if hasattr(self, '_redo_operations'):
                self._redo_operations.clear()
                
            self.display_image()
            self.update_image_info()
            self.update_undo_redo_buttons()
            
            # Positive feedback
            self.update_info(f"Image loaded successfully!\n\n{self.get_image_info_text()}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")
    
    def get_image_info_text(self):
        """Generates text with image information."""
        if self.current_image and self.image_path:
            return f"""File: {Path(self.image_path).name}
Dimensions: {self.current_image.width} x {self.current_image.height}
Format: {self.current_image.format}
Mode: {self.current_image.mode}
Size: {os.path.getsize(self.image_path) / (1024*1024):.2f} MB"""
        return ""
    
    def load_image(self):
        """Loads an image from file."""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("All Images", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_image_from_path(file_path)
    
    def display_image(self):
        """Displays the original and edited image side-by-side in the interface, both scaled to the same maximum size. Suportă zoom independent pentru ambele imagini cu păstrarea aspect ratio-ului."""
        max_w, max_h = self._zoom_display_size if hasattr(self, '_zoom_display_size') else (600, 400)
        
        # Original
        if self.original_image:
            zoom_orig = self._zoom_factor_orig if hasattr(self, '_zoom_factor_orig') else 1.0
            orig_disp = self.original_image.copy()
            
            # Calculate the base display size maintaining aspect ratio
            base_display = self.image_processor.resize_for_display(orig_disp, max_width=max_w, max_height=max_h)
            
            # Apply zoom factor while maintaining aspect ratio
            if zoom_orig != 1.0:
                new_width = int(base_display.width * zoom_orig)
                new_height = int(base_display.height * zoom_orig)
                orig_disp = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            else:
                orig_disp = base_display
                
            orig_photo = ImageTk.PhotoImage(orig_disp)
            self.original_image_label.configure(image=orig_photo, text="")
            self.original_image_label.image = orig_photo
        else:
            self.original_image_label.configure(image=None, text="No image loaded.")
            self.original_image_label.image = None
            
        # Edited
        if self.current_image:
            zoom_edit = self._zoom_factor_edit if hasattr(self, '_zoom_factor_edit') else 1.0
            edit_disp = self.current_image.copy()
            
            # Calculate the base display size maintaining aspect ratio
            base_display = self.image_processor.resize_for_display(edit_disp, max_width=max_w, max_height=max_h)
            
            # Apply zoom factor while maintaining aspect ratio
            if zoom_edit != 1.0:
                new_width = int(base_display.width * zoom_edit)
                new_height = int(base_display.height * zoom_edit)
                edit_disp = self.current_image.resize((new_width, new_height), Image.LANCZOS)
            else:
                edit_disp = base_display
                
            edit_photo = ImageTk.PhotoImage(edit_disp)
            self.edited_image_label.configure(image=edit_photo, text="")
            self.edited_image_label.image = edit_photo
        else:
            self.edited_image_label.configure(image=None, text="No image loaded.")
            self.edited_image_label.image = None
    
    def update_image_info(self):
        """Updates image information."""
        if self.current_image:
            info_text = self.get_image_info_text()
            self.update_info(info_text)
        
    def update_info(self, text):
        """Appends a new message to the information panel, with numbering."""
        if not hasattr(self, '_info_history'):
            self._info_history = []
        # If this is a reset/load event, clear history
        if text.startswith("✅ Image loaded successfully!") or text.startswith("Image has been reset") or text.startswith("Load an image to see details."):
            self._info_history = []
        self._info_history.append(text)
        # Build numbered info
        info_lines = []
        for idx, msg in enumerate(self._info_history, 1):
            # Only number the first line of each message
            msg_lines = msg.splitlines()
            if msg_lines:
                info_lines.append(f"{idx}. {msg_lines[0]}")
                if len(msg_lines) > 1:
                    info_lines.extend(msg_lines[1:])
        info_text = "\n".join(info_lines)
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info_text)
        self.info_text.configure(state="disabled")
    
    def run_ai_operation(self, operation_func, operation_name):
        """Runs an AI operation in the background and saves for undo."""
        def worker():
            try:
                self.progress.set(0.1)
                self.update_info(f"Running {operation_name}...")
                # Save for undo with operation name
                self.push_undo(operation_name)
                result = operation_func(self.current_image)
                self.progress.set(0.9)
                self.current_image = result
                self._current_operation = operation_name  # Track current operation
                self.display_image()
                self.progress.set(1.0)
                self.update_info(f"{operation_name} completed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error in {operation_name}: {e}")
            finally:
                self.progress.set(0)
        if self.current_image:
            threading.Thread(target=worker, daemon=True).start()
        else:
            messagebox.showwarning("Warning", "Please load an image first!")
    
    def upscale_image(self):
        """Upscales the image using AI."""
        self.run_ai_operation(self.upscaler.upscale, "Upscale")
    
    def remove_background(self):
        """Removes the background from the image."""
        self.run_ai_operation(self.bg_remover.remove_background, "Remove Background")
    
    def generative_fill(self):
        """Applies generative fill only on the background if it has been removed (RGBA image with transparency)."""
        # Show prompt dialog
        class PromptDialog(tk.Toplevel):
            def __init__(self, master):
                super().__init__(master)
                self.title("How to fill the image?")
                self.geometry("350x140")
                self.resizable(False, False)
                self.prompt = None
                label = tk.Label(self, text="How to fill the image?", font=("Arial", 12))
                label.pack(pady=(15, 5))
                self.entry = tk.Entry(self, width=40)
                self.entry.pack(pady=5)
                btn_frame = tk.Frame(self)
                btn_frame.pack(pady=10)
                fill_btn = tk.Button(btn_frame, text="Fill now", width=10, command=self.on_fill)
                fill_btn.pack(side="left", padx=5)
                cancel_btn = tk.Button(btn_frame, text="Cancel", width=10, command=self.on_cancel)
                cancel_btn.pack(side="left", padx=5)
                self.entry.focus_set()
                self.result = None
            def on_fill(self):
                self.result = self.entry.get()
                self.destroy()
            def on_cancel(self):
                self.result = None
                self.destroy()

        dialog = PromptDialog(self.root)
        self.root.wait_window(dialog)
        prompt = dialog.result
        if prompt is None:
            self.update_info("Generative fill cancelled.")
            return
        def fill_background_only(image):
            # If the image has an alpha channel (background removed)
            if image.mode == "RGBA":
                import numpy as np
                from PIL import Image
                arr = np.array(image)
                alpha = arr[..., 3]
                mask = (alpha == 0)
                gen_filled = self.gen_fill.fill(image.convert("RGB"), prompt=prompt)
                gen_filled = gen_filled.convert("RGBA").resize(image.size)
                gen_arr = np.array(gen_filled)
                result_arr = arr.copy()
                result_arr[mask] = gen_arr[mask]
                result = Image.fromarray(result_arr, mode="RGBA")
                return result.convert("RGB")
            else:
                return self.gen_fill.fill(image, prompt=prompt)
        self.run_ai_operation(fill_background_only, "Generative Fill")
    
    def generative_fill_simple(self):
        """Applies simple generative fill (OpenCV inpainting, no AI) to the current image."""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded!")
            return
        self.push_undo("Generative Fill (No AI)")
        result = self.gen_fill.generative_fill_no_ai(self.current_image)
        self.current_image = result
        self._current_operation = "Generative Fill (No AI)"
        self.display_image()
        self.update_info("Simple generative fill applied (no AI).")
    
    def recognize_image(self):
        """Recognizes the content of the image."""
        def recognize():
            if self.current_image:
                try:
                    self.progress.set(0.5)
                    description = self.img_recognition.recognize(self.current_image)
                    self.update_info(f"Image Recognition:\n\n{description}")
                    self.progress.set(1.0)
                except Exception as e:
                    messagebox.showerror("Error", f"Recognition error: {e}")
                finally:
                    self.progress.set(0)
            else:
                messagebox.showwarning("Warning", "Please load an image first!")
        
        threading.Thread(target=recognize, daemon=True).start()
    
    def reset_image(self):
        """Resets the image to its original state and resets adjustment sliders."""
        if self.original_image:
            self.push_undo("Reset Image")
            self.current_image = self.original_image.copy()
            self._current_operation = "Reset Image"
            # Also resets sliders if they exist
            if hasattr(self, '_reset_sliders_ref') and callable(self._reset_sliders_ref):
                self._reset_sliders_ref()
            self.display_image()
            self.update_info("Image has been reset to original state.")
            self.update_undo_redo_buttons()
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def update_undo_redo_buttons(self):
        """Enables/disables Undo/Redo buttons and updates modification progress with memory info."""
        undo_stack = getattr(self, '_undo_stack', [])
        redo_stack = getattr(self, '_redo_stack', [])
        # Undo
        if hasattr(self, 'undo_btn'):
            if undo_stack:
                self.undo_btn.configure(state="normal")
            else:
                self.undo_btn.configure(state="disabled")
        # Redo
        if hasattr(self, 'redo_btn'):
            if redo_stack:
                self.redo_btn.configure(state="normal")
            else:
                self.redo_btn.configure(state="disabled")
        # Progress and memory info
        if hasattr(self, 'edit_progress_label'):
            total = len(undo_stack) + 1 + len(redo_stack) if (undo_stack or redo_stack) else 1
            current = len(undo_stack) + 1 if (undo_stack or redo_stack) else 1
            
            # Add memory usage info
            memory_info = self.get_memory_usage_info()
            
            if total > 1:
                progress_text = f"{current}/{total}\n{memory_info}"
            else:
                progress_text = memory_info if undo_stack or redo_stack else ""
                
            self.edit_progress_label.configure(text=progress_text)

    def run(self):
        """Start the application."""
        # Configurează acțiunea de închidere
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Funcție apelată când se închide aplicația."""
        # Salvează istoricul înainte de închidere
        self.save_history_to_file()
        self.root.destroy()

    def rotate_image(self):
        """Rotește imaginea cu 90° la dreapta și salvează pentru undo."""
        if self.current_image:
            self.push_undo("Rotate 90°")
            self.current_image = self.current_image.rotate(-90, expand=True)
            self._current_operation = "Rotate 90°"
            self.display_image()
            self.update_info("Image rotated 90° to the right.")
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def mirror_image(self):
        """Reflectă imaginea pe orizontală (mirror) și salvează pentru undo."""
        if self.current_image:
            self.push_undo("Mirror")
            self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            self._current_operation = "Mirror"
            self.display_image()
            self.update_info("Image mirrored horizontally.")
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def flip_vertical_image(self):
        """Reflectă imaginea pe verticală (flip vertical) și salvează pentru undo."""
        if self.current_image:
            self.push_undo("Flip Vertical")
            self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
            self._current_operation = "Flip Vertical"
            self.display_image()
            self.update_info("Image flipped vertically.")
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def crop_image(self):
        """Permite utilizatorului să selecteze zona de crop cu mouse-ul pe imaginea editată."""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded!")
            return
        # Fereastră nouă cu canvas pentru crop interactiv
        crop_win = tk.Toplevel(self.root)
        crop_win.title("Select Crop Area")
        crop_win.geometry("800x600")
        crop_win.resizable(False, False)
        # Redimensionează imaginea pentru display
        disp_img = self.current_image.copy()
        disp_img.thumbnail((760, 560), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(disp_img)
        canvas = tk.Canvas(crop_win, width=tk_img.width(), height=tk_img.height(), cursor="cross")
        canvas.pack(padx=20, pady=20)
        canvas.create_image(0, 0, anchor="nw", image=tk_img)
        # Variabile pentru selecție
        rect = None
        start_x = start_y = end_x = end_y = 0
        # Coordonate reale pentru crop

        scale_x = self.current_image.width / tk_img.width()
        scale_y = self.current_image.height / tk_img.height()
        def on_mouse_down(event):
            nonlocal start_x, start_y, rect
            start_x, start_y = event.x, event.y
            if rect:
                canvas.delete(rect)
            rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="#38bdf8", width=2)
        def on_mouse_drag(event):
            nonlocal rect
            if rect:
                canvas.coords(rect, start_x, start_y, event.x, event.y)
        def on_mouse_up(event):
            nonlocal end_x, end_y, rect
            end_x, end_y = event.x, event.y
            # Asigură coordonate pozitive
            x1, y1 = min(start_x, end_x), min(start_y, end_y)
            x2, y2 = max(start_x, end_x), max(start_y, end_y)
            # Transformă în coordonate reale
            rx1 = int(x1 * scale_x)
            ry1 = int(y1 * scale_y)
            rx2 = int(x2 * scale_x)
            ry2 = int(y2 * scale_y)
            w, h = rx2 - rx1, ry2 - ry1
            if w > 0 and h > 0 and rx2 <= self.current_image.width and ry2 <= self.current_image.height:
                self.push_undo("Crop")
                self.current_image = self.current_image.crop((rx1, ry1, rx2, ry2))
                self._current_operation = "Crop"
                self.display_image()
                self.update_info(f"Image cropped: x={rx1}, y={ry1}, w={w}, h={h}")
                crop_win.destroy()
            else:
                messagebox.showwarning("Warning", "Invalid crop area!")
        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        crop_win.mainloop()

    def export_image_as(self):
        """Permite exportul imaginii curente în format PNG, JPEG sau WEBP."""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to export!")
            return
        file_path = filedialog.asksaveasfilename(
            title="Export image as...",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("WEBP", "*.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                format_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
                fmt = format_map.get(ext, "PNG")
                save_kwargs = {}
                if fmt == "JPEG":
                    save_kwargs["quality"] = 95
                self.current_image.save(file_path, format=fmt, **save_kwargs)
                self.add_to_file_history(file_path)  # Adaugă în istoric
                messagebox.showinfo("Success", f"Image exported as {fmt}!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export image: {e}")
    
    def add_to_file_history(self, file_path):
        """Adaugă un fișier în istoricul de fișiere salvate."""
        import time
        from pathlib import Path
        
        # Creează entry-ul pentru istoric
        history_entry = {
            'path': file_path,
            'name': Path(file_path).name,
            'timestamp': time.time(),
            'size': self.get_file_size(file_path)
        }
        
        # Elimină duplicatele (dacă există deja)
        self.saved_files_history = [entry for entry in self.saved_files_history if entry['path'] != file_path]
        
        # Adaugă la început
        self.saved_files_history.insert(0, history_entry)
        
        # Păstrează doar ultimele 5
        if len(self.saved_files_history) > 5:
            self.saved_files_history = self.saved_files_history[:5]
        
        # Salvează istoricul persistent
        self.save_history_to_file()
    
    def get_file_size(self, file_path):
        """Returnează dimensiunea fișierului în format lizibil."""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    def show_file_history(self):
        """Afișează istoricul fișierelor salvate."""
        if not self.saved_files_history:
            messagebox.showinfo("Recent Files", "No recent files found.")
            return
        
        # Creează fereastra pentru istoric - mai mare și redimensionabilă
        history_win = tk.Toplevel(self.root)
        history_win.title("Recent Saved Files")
        history_win.geometry("600x500")
        history_win.resizable(True, True)
        history_win.minsize(500, 400)
        
        # Título
        title_label = tk.Label(history_win, text="Recent Saved Files", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Frame principal cu scroll
        main_frame = tk.Frame(history_win)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Canvas și scrollbar pentru scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas și scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel pentru scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        import time
        for i, entry in enumerate(self.saved_files_history, 1):
            # Frame pentru fiecare fișier
            file_frame = tk.Frame(scrollable_frame, relief="raised", bd=1)
            file_frame.pack(fill="x", pady=5, padx=5)
            
            # Informații despre fișier
            file_info = f"{i}. {entry['name']}"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry['timestamp']))
            file_details = f"Size: {entry['size']} | Saved: {timestamp}"
            
            # Label cu numele fișierului
            name_label = tk.Label(file_frame, text=file_info, font=("Arial", 11, "bold"), anchor="w")
            name_label.pack(fill="x", padx=10, pady=(5, 0))
            
            # Label cu detaliile
            details_label = tk.Label(file_frame, text=file_details, font=("Arial", 9), fg="gray", anchor="w")
            details_label.pack(fill="x", padx=10, pady=(0, 5))
            
            # Frame pentru butoane
            btn_frame = tk.Frame(file_frame)
            btn_frame.pack(fill="x", padx=10, pady=(0, 5))
            
            # Buton pentru a deschide fișierul
            open_btn = tk.Button(btn_frame, text="Open", width=15,
                               command=lambda path=entry['path']: self.open_file_from_history(path))
            open_btn.pack(side="left")
        
        # Frame pentru butonul de închidere (în afara scroll-ului)
        bottom_frame = tk.Frame(history_win)
        bottom_frame.pack(fill="x", pady=10)
        
        # Buton pentru a închide
        close_btn = tk.Button(bottom_frame, text="Close", width=10, command=lambda: [canvas.unbind_all("<MouseWheel>"), history_win.destroy()])
        close_btn.pack()
        
        history_win.transient(self.root)
        history_win.grab_set()
    
    def open_file_from_history(self, file_path):
        """Deschide un fișier din istoric."""
        try:
            if os.path.exists(file_path):
                self.load_image_from_path(file_path)
                messagebox.showinfo("Success", f"File loaded: {os.path.basename(file_path)}")
            else:
                messagebox.showwarning("File Not Found", f"The file no longer exists:\n{file_path}")
                # Elimină din istoric
                self.saved_files_history = [entry for entry in self.saved_files_history if entry['path'] != file_path]
                self.save_history_to_file()  # Salvează modificările
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_history_to_file(self):
        """Salvează istoricul fișierelor într-un fișier JSON."""
        try:
            import json
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_files_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history_from_file(self):
        """Încarcă istoricul fișierelor dintr-un fișier JSON."""
        try:
            import json
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.saved_files_history = json.load(f)
                # Validează că fișierele încă există și elimină cele care nu mai există
                valid_history = []
                for entry in self.saved_files_history:
                    if os.path.exists(entry.get('path', '')):
                        valid_history.append(entry)
                self.saved_files_history = valid_history
                # Salvează lista curățată
                if len(valid_history) != len(self.saved_files_history):
                    self.save_history_to_file()
        except Exception as e:
            print(f"Error loading history: {e}")
            self.saved_files_history = []