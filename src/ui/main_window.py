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
    def push_undo(self):
        if not hasattr(self, '_undo_stack'):
            self._undo_stack = []
        if not hasattr(self, '_redo_stack'):
            self._redo_stack = []
        if self.current_image:
            self._undo_stack.append(self.current_image.copy())
            # Limit stack size if needed
            if len(self._undo_stack) > 20:
                self._undo_stack.pop(0)
        self.update_undo_redo_buttons()

    def undo(self):
        if hasattr(self, '_undo_stack') and self._undo_stack:
            if not hasattr(self, '_redo_stack'):
                self._redo_stack = []
            if self.current_image:
                self._redo_stack.append(self.current_image.copy())
            self.current_image = self._undo_stack.pop()
            self.display_image()
            self.update_image_info()
        self.update_undo_redo_buttons()

    def redo(self):
        if hasattr(self, '_redo_stack') and self._redo_stack:
            if not hasattr(self, '_undo_stack'):
                self._undo_stack = []
            if self.current_image:
                self._undo_stack.append(self.current_image.copy())
            self.current_image = self._redo_stack.pop()
            self.display_image()
            self.update_image_info()
        self.update_undo_redo_buttons()


    def apply_filter(self):
        """Displays a dropdown for filter selection and applies the effect to the current image."""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return

        # Save state for undo before applying the filter
        self.push_undo()

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
                filtered = FILTERS[dialog.result](self.current_image)
                self.current_image = filtered
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
        
        # Button for saving
        save_btn = ctk.CTkButton(
            toolbar,
            text="Save",
            command=self.save_image,
            width=100
        )
        save_btn.pack(side="left", padx=5, pady=5)
        
        # Button for reset
        reset_btn = ctk.CTkButton(
            toolbar,
            text="Reset",
            command=self.reset_image,
            width=80
        )
        reset_btn.pack(side="left", padx=5, pady=5)
    
    def create_control_panel(self, parent):
        """Creates the AI and image adjustment control panel."""
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(side="left", fill="y", padx=(0, 10))

        # Title
        title = ctk.CTkLabel(control_frame, text="AI Operations", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # --- Undo/Redo buttons ---
        undo_redo_frame = ctk.CTkFrame(control_frame)
        undo_redo_frame.pack(pady=(5, 5))
        self.undo_btn = ctk.CTkButton(undo_redo_frame, text="Undo", width=65, command=self.undo)
        self.redo_btn = ctk.CTkButton(undo_redo_frame, text="Redo", width=65, command=self.redo)
        self.undo_btn.pack(side="left", padx=(0, 5))
        self.redo_btn.pack(side="left", padx=(5, 0))
        self.edit_progress_label = ctk.CTkLabel(undo_redo_frame, text="")
        self.edit_progress_label.pack(side="left", padx=(10,0))

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
            self.push_undo()
            # Final update (optional, since on_slider_change already updates)
            img = self._slider_original.copy()
            brightness = brightness_slider.get()
            img = ImageEnhance.Brightness(img).enhance(brightness)
            contrast = contrast_slider.get()
            img = ImageEnhance.Contrast(img).enhance(contrast)
            saturation = saturation_slider.get()
            img = ImageEnhance.Color(img).enhance(saturation)
            self.current_image = img
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
                self.push_undo()
                self.current_image = self.original_image.copy()
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

        # --- Other AI buttons ---
        upscale_btn = ctk.CTkButton(
            control_frame,
            text="Upscale Image",
            command=self.upscale_image,
            width=150
        )
        upscale_btn.pack(pady=5)

        bg_remove_btn = ctk.CTkButton(
            control_frame,
            text="Remove Background",
            command=self.remove_background,
            width=150
        )
        bg_remove_btn.pack(pady=5)

        bg_replace_btn = ctk.CTkButton(
            control_frame,
            text="Replace Background",
            command=self.replace_background,
            width=150
        )
        bg_replace_btn.pack(pady=5)

        filter_btn = ctk.CTkButton(
            control_frame,
            text="Apply Filter",
            command=self.apply_filter,
            width=150
        )
        filter_btn.pack(pady=5)

        gen_fill_btn = ctk.CTkButton(
            control_frame,
            text="Generative Fill",
            command=self.generative_fill,
            width=150
        )
        gen_fill_btn.pack(pady=5)

        gen_fill_simple_btn = ctk.CTkButton(
            control_frame,
            text="Generative Fill (No AI)",
            command=self.generative_fill_simple,
            width=150
        )
        gen_fill_simple_btn.pack(pady=5)

        recognize_btn = ctk.CTkButton(
            control_frame,
            text="Recognize Image",
            command=self.recognize_image,
            width=150
        )
        recognize_btn.pack(pady=5)

        # --- Export Button ---
        export_btn = ctk.CTkButton(control_frame, text="Export as...", width=150, height=38, font=("Arial", 13, "bold"), corner_radius=12, fg_color="#facc15", hover_color="#eab308", command=self.export_image_as)
        export_btn.pack(pady=5)

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
            self.display_image()
            self.update_image_info()
            
            # Positive feedback
            self.update_info(f"✅ Image loaded successfully!\n\n{self.get_image_info_text()}")
            
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
        """Displays the original and edited image side-by-side in the interface, both scaled to the same maximum size. Suportă zoom independent pentru ambele imagini."""
        max_w, max_h = self._zoom_display_size if hasattr(self, '_zoom_display_size') else (600, 400)
        # Original
        if self.original_image:
            zoom_orig = self._zoom_factor_orig if hasattr(self, '_zoom_factor_orig') else 1.0
            # Calculate display size: allow zoom > 1.0 to exceed max_w/max_h
            base_w, base_h = max_w, max_h
            disp_w, disp_h = int(base_w * zoom_orig), int(base_h * zoom_orig)
            orig_disp = self.original_image.copy()
            # If zoom > 1, allow upscaling beyond the default display size
            if zoom_orig > 1.0:
                # Don't limit to max_width/max_height, just resize to (disp_w, disp_h)
                orig_disp = orig_disp.resize((disp_w, disp_h), Image.LANCZOS)
            else:
                orig_disp = self.image_processor.resize_for_display(orig_disp, max_width=disp_w, max_height=disp_h)
            orig_photo = ImageTk.PhotoImage(orig_disp)
            self.original_image_label.configure(image=orig_photo, text="")
            self.original_image_label.image = orig_photo
        else:
            self.original_image_label.configure(image=None, text="No image loaded.")
            self.original_image_label.image = None
        # Edited
        if self.current_image:
            zoom_edit = self._zoom_factor_edit if hasattr(self, '_zoom_factor_edit') else 1.0
            base_w, base_h = max_w, max_h
            disp_w, disp_h = int(base_w * zoom_edit), int(base_h * zoom_edit)
            edit_disp = self.current_image.copy()
            if zoom_edit > 1.0:
                edit_disp = edit_disp.resize((disp_w, disp_h), Image.LANCZOS)
            else:
                edit_disp = self.image_processor.resize_for_display(edit_disp, max_width=disp_w, max_height=disp_h)
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
        """Updates the information panel (read-only)."""
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", text)
        self.info_text.configure(state="disabled")
    
    def run_ai_operation(self, operation_func, operation_name):
        """Runs an AI operation in the background and saves for undo."""
        def worker():
            try:
                self.progress.set(0.1)
                self.update_info(f"Running {operation_name}...")
                # Save for undo
                self.push_undo()
                result = operation_func(self.current_image)
                self.progress.set(0.9)
                self.current_image = result
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
        self.push_undo()
        result = self.gen_fill.generative_fill_no_ai(self.current_image)
        self.current_image = result
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
    
    def save_image(self):
        """Saves the current image."""
        if self.current_image:
            file_path = filedialog.asksaveasfilename(
                title="Save image",
                defaultextension=".png",
                filetypes=[
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                try:
                    self.current_image.save(file_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save image: {e}")
        else:
            messagebox.showwarning("Warning", "No image to save!")
    
    def reset_image(self):
        """Resets the image to its original state and resets adjustment sliders."""
        if self.original_image:
            self.push_undo()
            self.current_image = self.original_image.copy()
            # Also resets sliders if they exist
            if hasattr(self, '_reset_sliders_ref') and callable(self._reset_sliders_ref):
                self._reset_sliders_ref()
            self.display_image()
            self.update_info("Image has been reset to original state.")
            self.update_undo_redo_buttons()
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def update_undo_redo_buttons(self):
        """Enables/disables Undo/Redo buttons and updates modification progress."""
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
        # Progres modificări
        if hasattr(self, 'edit_progress_label'):
            total = len(undo_stack) + 1 + len(redo_stack) if (undo_stack or redo_stack) else 1
            current = len(undo_stack) + 1 if (undo_stack or redo_stack) else 1
            if total > 1:
                self.edit_progress_label.configure(text=f"{current}/{total}")
            else:
                self.edit_progress_label.configure(text="")

    def run(self):
        """Start the application."""
        self.root.mainloop()

    def rotate_image(self):
        """Rotește imaginea cu 90° la dreapta și salvează pentru undo."""
        if self.current_image:
            self.push_undo()
            self.current_image = self.current_image.rotate(-90, expand=True)
            self.display_image()
            self.update_info("Image rotated 90° to the right.")
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def mirror_image(self):
        """Reflectă imaginea pe orizontală (mirror) și salvează pentru undo."""
        if self.current_image:
            self.push_undo()
            self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.display_image()
            self.update_info("Image mirrored horizontally.")
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def flip_vertical_image(self):
        """Reflectă imaginea pe verticală (flip vertical) și salvează pentru undo."""
        if self.current_image:
            self.push_undo()
            self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
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
                self.push_undo()
                self.current_image = self.current_image.crop((rx1, ry1, rx2, ry2))
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
                messagebox.showinfo("Success", f"Image exported as {fmt}!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export image: {e}")
