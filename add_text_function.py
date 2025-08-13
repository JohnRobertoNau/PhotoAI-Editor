def add_text_to_image(self):
    """Permite adăugarea de text pe imagine prin selectarea unei zone cu mouse-ul și introducerea textului cu alegerea culorii."""
    if not self.current_image:
        messagebox.showwarning("Warning", "No image loaded!")
        return
    
    text_win = tk.Toplevel(self.root)
    text_win.title("Add Text")
    text_win.geometry("800x650")
    text_win.resizable(False, False)
    
    # Color selection dropdown at top
    color_options = {
        "Alb": "white",
        "Negru": "black",
        "Roșu": "#ef4444",
        "Galben": "#fde047",
        "Albastru": "#3b82f6",
        "Verde": "#22c55e",
        "Portocaliu": "#f97316",
        "Mov": "#a21caf"
    }
    color_var = tk.StringVar(value="Alb")
    color_frame = tk.Frame(text_win)
    color_frame.pack(pady=10)
    tk.Label(color_frame, text="Text color:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
    color_menu = tk.OptionMenu(color_frame, color_var, *color_options.keys())
    color_menu.config(font=("Arial", 10))
    color_menu.pack(side="left")
    
    # Image canvas
    disp_img = self.current_image.copy()
    disp_img.thumbnail((760, 560), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(disp_img)
    canvas = tk.Canvas(text_win, width=tk_img.width(), height=tk_img.height(), cursor="cross")
    canvas.pack(padx=20, pady=10)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    
    # Variables for text area selection
    rect = None
    start_x = start_y = end_x = end_y = None, None, None, None
    entry_widget = None
    scale_x = self.current_image.width / tk_img.width()
    scale_y = self.current_image.height / tk_img.height()
    
    def on_mouse_down(event):
        nonlocal start_x, start_y, rect, entry_widget, end_x, end_y
        start_x, start_y = event.x, event.y
        end_x, end_y = event.x, event.y
        if rect:
            canvas.delete(rect)
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="#facc15", width=2)
        if entry_widget:
            entry_widget.destroy()
            entry_widget = None
    
    def on_mouse_drag(event):
        nonlocal rect, end_x, end_y
        end_x, end_y = event.x, event.y
        if rect:
            canvas.coords(rect, start_x, start_y, end_x, end_y)
    
    def on_mouse_up(event):
        nonlocal end_x, end_y, entry_widget
        end_x, end_y = event.x, event.y
        x1, y1 = min(start_x, end_x), min(start_y, end_y)
        x2, y2 = max(start_x, end_x), max(start_y, end_y)
        if entry_widget:
            entry_widget.destroy()
        if abs(x2-x1) < 20 or abs(y2-y1) < 20:
            return  # zona prea mică
        entry_widget = tk.Entry(canvas, font=("Arial", 16))
        entry_widget.place(x=x1, y=y1, width=max(60, x2-x1), height=max(30, y2-y1))
        entry_widget.focus_set()
    
    def on_ok():
        nonlocal entry_widget, start_x, start_y, end_x, end_y
        if not entry_widget or start_x is None or start_y is None or end_x is None or end_y is None:
            messagebox.showwarning("Warning", "Select a text area and enter text!")
            return
        text = entry_widget.get()
        if not text.strip():
            messagebox.showwarning("Warning", "Text is empty!")
            return
        
        # Calculate real coordinates on original image
        rx1 = int(min(start_x, end_x) * scale_x)
        ry1 = int(min(start_y, end_y) * scale_y)
        rx2 = int(max(start_x, end_x) * scale_x)
        ry2 = int(max(start_y, end_y) * scale_y)
        
        if abs(rx2-rx1) < 10 or abs(ry2-ry1) < 10:
            messagebox.showwarning("Warning", "Select a larger area for text!")
            return
        
        # Save for undo
        self.push_undo()
        
        # Add text to image
        img = self.current_image.copy()
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Calculate font size based on text box height
        font_size = max(20, int((ry2-ry1) * 0.8))
        font = None
        
        # Try to load a TrueType font
        font_paths = [
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf", 
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, size=font_size)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # Get text color from selection
        text_color = color_options.get(color_var.get(), "white")
        
        # Get text dimensions
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            # Fallback for older Pillow versions
            w, h = draw.textsize(text, font=font)
        
        # Center text in the selected area
        tx = rx1 + max(0, ((rx2-rx1)-w)//2)
        ty = ry1 + max(0, ((ry2-ry1)-h)//2)
        
        # Draw text on image
        draw.text((tx, ty), text, fill=text_color, font=font)
        
        self.current_image = img
        self.display_image()
        self.update_info(f"Text added: '{text}' (color: {color_var.get()})")
        text_win.destroy()
    
    def on_cancel():
        text_win.destroy()
    
    # Bind mouse events
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    
    # Buttons
    btn_frame = tk.Frame(text_win)
    btn_frame.pack(pady=10)
    ok_btn = tk.Button(btn_frame, text="Add Text", width=12, command=on_ok, font=("Arial", 10))
    ok_btn.pack(side="left", padx=5)
    cancel_btn = tk.Button(btn_frame, text="Cancel", width=12, command=on_cancel, font=("Arial", 10))
    cancel_btn.pack(side="left", padx=5)
