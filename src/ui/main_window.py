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
    def __init__(self):
        # Configurează tema pentru customtkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Creează root cu suport drag and drop nativ
        self.root = ctk.CTk()
        self.root.title("AI Photo Editor")
        self.root.geometry("1200x800")
        
        # Variabile de stare
        self.current_image = None
        self.original_image = None
        self.image_path = None
        
        # Inițializează modelele AI
        self.init_ai_models()
        
        # Creează interfața
        self.create_widgets()
        
        # Configurează drag and drop
        self.setup_drag_drop()
        
    def init_ai_models(self):
        """Inițializează modelele AI."""
        try:
            self.upscaler = ImageUpscaler()
            self.bg_remover = BackgroundRemover()
            self.gen_fill = GenerativeFill()
            self.img_recognition = ImageRecognition()
            self.image_processor = ImageProcessor()
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-au putut încărca modelele AI: {e}")
    
    def create_widgets(self):
        """Creează elementele UI."""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Toolbar
        self.create_toolbar(main_frame)
        
        # Area de lucru
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Panel stâng - controale
        self.create_control_panel(content_frame)
        
        # Panel centru - imagine
        self.create_image_panel(content_frame)
        
        # Panel dreapta - informații
        self.create_info_panel(content_frame)
    
    def create_toolbar(self, parent):
        """Creează toolbar-ul cu butoane principale."""
        toolbar = ctk.CTkFrame(parent)
        toolbar.pack(fill="x", pady=(0, 10))
        
        # Buton pentru încărcare imagine
        load_btn = ctk.CTkButton(
            toolbar, 
            text="Încarcă Imagine",
            command=self.load_image,
            width=120
        )
        load_btn.pack(side="left", padx=5, pady=5)
        
        # Buton pentru salvare
        save_btn = ctk.CTkButton(
            toolbar,
            text="Salvează",
            command=self.save_image,
            width=100
        )
        save_btn.pack(side="left", padx=5, pady=5)
        
        # Buton pentru reset
        reset_btn = ctk.CTkButton(
            toolbar,
            text="Reset",
            command=self.reset_image,
            width=80
        )
        reset_btn.pack(side="left", padx=5, pady=5)
    
    def create_control_panel(self, parent):
        """Creează panelul de controale AI."""
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Titlu
        title = ctk.CTkLabel(control_frame, text="Operații AI", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Buton Upscale
        upscale_btn = ctk.CTkButton(
            control_frame,
            text="Upscale Imagine",
            command=self.upscale_image,
            width=150
        )
        upscale_btn.pack(pady=5)
        
        # Buton Remove Background
        bg_remove_btn = ctk.CTkButton(
            control_frame,
            text="Elimină Fundal",
            command=self.remove_background,
            width=150
        )
        bg_remove_btn.pack(pady=5)
        
        # Buton Generative Fill
        gen_fill_btn = ctk.CTkButton(
            control_frame,
            text="Generative Fill",
            command=self.generative_fill,
            width=150
        )
        gen_fill_btn.pack(pady=5)
        
        # Buton Image Recognition
        recognize_btn = ctk.CTkButton(
            control_frame,
            text="Recunoaște Imagine",
            command=self.recognize_image,
            width=150
        )
        recognize_btn.pack(pady=5)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(control_frame)
        self.progress.pack(pady=20, padx=10, fill="x")
        self.progress.set(0)
    
    def create_image_panel(self, parent):
        """Creează panelul pentru afișarea imaginii."""
        self.image_frame = ctk.CTkFrame(parent)
        self.image_frame.pack(side="left", fill="both", expand=True)
        
        # Label pentru imagine cu suport drag and drop nativ
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="Trage o imagine aici sau apasă 'Încarcă Imagine'",
            font=("Arial", 14),
            height=400
        )
        self.image_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Configurează drop zone cu styling vizual
        self.image_label.bind("<Enter>", self.on_hover_enter)
        self.image_label.bind("<Leave>", self.on_hover_leave)
        
        # Adaugă text explicativ pentru drag and drop
        self.drop_instructions = ctk.CTkLabel(
            self.image_frame,
            text="📁 Poți copia calea unei imagini din Windows Explorer\nși o poți lipi aici cu Ctrl+V",
            font=("Arial", 10),
            text_color="gray"
        )
        self.drop_instructions.pack(pady=(0, 10))
    
    def create_info_panel(self, parent):
        """Creează panelul de informații."""
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(side="right", fill="y", padx=(10, 0))
        
        # Titlu
        title = ctk.CTkLabel(info_frame, text="Informații", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Text widget pentru afișarea informațiilor
        self.info_text = ctk.CTkTextbox(info_frame, width=250, height=400)
        self.info_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.update_info("Încarcă o imagine pentru a vedea detaliile.")
    
    def setup_drag_drop(self):
        """Configurează funcționalitatea alternativă pentru încărcare imagine."""
        try:
            # Configurează keyboard shortcut pentru paste
            self.root.bind('<Control-v>', self.paste_image_path)
            self.root.focus_set()  # Permite focus pentru keyboard events
            
            # Adaugă buton pentru încărcare rapidă din clipboard
            self.add_quick_load_button()
            
        except Exception as e:
            print(f"Setup alternativ nu este disponibil: {e}")
    
    def paste_image_path(self, event):
        """Handler pentru Ctrl+V - încarcă imagine din clipboard path."""
        try:
            # Încearcă să obțină path din clipboard
            clipboard_content = self.root.clipboard_get()
            
            # Verifică dacă e un path valid către o imagine
            if self.is_valid_image_file(clipboard_content):
                self.load_image_from_path(clipboard_content)
            else:
                # Încearcă să detecteze dacă e un path Windows
                if '\\' in clipboard_content or '/' in clipboard_content:
                    # Curăță path-ul
                    clean_path = clipboard_content.strip('"').strip("'")
                    if self.is_valid_image_file(clean_path):
                        self.load_image_from_path(clean_path)
                    else:
                        self.update_info("⚠️ Path-ul din clipboard nu pare să fie o imagine validă")
                else:
                    self.update_info("💡 Copiază path-ul unei imagini și apasă Ctrl+V")
                    
        except tk.TclError:
            self.update_info("📋 Clipboard-ul nu conține text")
        except Exception as e:
            self.update_info(f"❌ Eroare la citirea clipboard: {e}")
    
    def add_quick_load_button(self):
        """Adaugă buton pentru încărcare rapidă."""
        # Găsește toolbar-ul și adaugă buton
        for widget in self.root.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                main_frame = widget
                break
        
        # Adaugă buton pentru clipboard în toolbar
        try:
            toolbar_widgets = main_frame.winfo_children()[0]  # Primul frame e toolbar-ul
            
            paste_btn = ctk.CTkButton(
                toolbar_widgets,
                text="Paste Path (Ctrl+V)",
                command=lambda: self.paste_image_path(None),
                width=120
            )
            paste_btn.pack(side="left", padx=5, pady=5)
        except:
            pass  # Dacă nu poate găsi toolbar-ul, continuă fără buton
    
    def on_hover_enter(self, event):
        """Handler pentru când mouse-ul intră în zona de imagine."""
        if not self.current_image:
            self.image_label.configure(text="🖼️ Apasă butonul 'Încarcă Imagine' sau folosește Ctrl+V")
    
    def on_hover_leave(self, event):
        """Handler pentru când mouse-ul iese din zona de imagine."""
        if not self.current_image:
            self.image_label.configure(text="Trage o imagine aici sau apasă 'Încarcă Imagine'")
    
    def is_valid_image_file(self, file_path):
        """Verifică dacă fișierul este o imagine validă."""
        try:
            if not file_path or not isinstance(file_path, str):
                return False
                
            # Verifică dacă path-ul există
            path_obj = Path(file_path)
            if not path_obj.exists() or not path_obj.is_file():
                return False
                
            valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
            file_extension = path_obj.suffix.lower()
            return file_extension in valid_extensions
        except:
            return False
    
    def load_image_from_path(self, file_path):
        """Încarcă imaginea din calea specificată."""
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            self.current_image = self.original_image.copy()
            self.display_image()
            self.update_image_info()
            
            # Feedback pozitiv
            self.update_info(f"✅ Imagine încărcată cu succes!\n\n{self.get_image_info_text()}")
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-a putut încărca imaginea: {e}")
    
    def get_image_info_text(self):
        """Generează textul cu informații despre imagine."""
        if self.current_image and self.image_path:
            return f"""Fișier: {Path(self.image_path).name}
Dimensiuni: {self.current_image.width} x {self.current_image.height}
Format: {self.current_image.format}
Mod: {self.current_image.mode}
Mărime: {os.path.getsize(self.image_path) / (1024*1024):.2f} MB"""
        return ""
    
    def load_image(self):
        """Încarcă o imagine din fișier."""
        file_path = filedialog.askopenfilename(
            title="Selectează o imagine",
            filetypes=[
                ("Toate imaginile", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Toate fișierele", "*.*")
            ]
        )
        
        if file_path:
            self.load_image_from_path(file_path)
    
    def display_image(self):
        """Afișează imaginea în interfață."""
        if self.current_image:
            # Redimensionează imaginea pentru afișare
            display_image = self.image_processor.resize_for_display(
                self.current_image, 
                max_width=600, 
                max_height=500
            )
            
            # Convertește pentru tkinter
            photo = ImageTk.PhotoImage(display_image)
            
            # Actualizează label-ul
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Păstrează referința
    
    def update_image_info(self):
        """Actualizează informațiile despre imagine."""
        if self.current_image:
            info_text = self.get_image_info_text()
            self.update_info(info_text)
    
    def update_info(self, text):
        """Actualizează panelul de informații."""
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", text)
    
    def run_ai_operation(self, operation_func, operation_name):
        """Rulează o operație AI în background."""
        def worker():
            try:
                self.progress.set(0.1)
                self.update_info(f"Se execută {operation_name}...")
                
                result = operation_func(self.current_image)
                
                self.progress.set(0.9)
                self.current_image = result
                self.display_image()
                self.progress.set(1.0)
                
                self.update_info(f"{operation_name} completat cu succes!")
                
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la {operation_name}: {e}")
            finally:
                self.progress.set(0)
        
        if self.current_image:
            threading.Thread(target=worker, daemon=True).start()
        else:
            messagebox.showwarning("Atenție", "Încarcă mai întâi o imagine!")
    
    def upscale_image(self):
        """Mărește imaginea folosind AI."""
        self.run_ai_operation(self.upscaler.upscale, "Upscale")
    
    def remove_background(self):
        """Elimină fundalul din imagine."""
        self.run_ai_operation(self.bg_remover.remove_background, "Eliminare fundal")
    
    def generative_fill(self):
        """Aplică generative fill."""
        self.run_ai_operation(self.gen_fill.fill, "Generative Fill")
    
    def recognize_image(self):
        """Recunoaște conținutul imaginii."""
        def recognize():
            if self.current_image:
                try:
                    self.progress.set(0.5)
                    description = self.img_recognition.recognize(self.current_image)
                    self.update_info(f"Recunoaștere imagine:\n\n{description}")
                    self.progress.set(1.0)
                except Exception as e:
                    messagebox.showerror("Eroare", f"Eroare la recunoaștere: {e}")
                finally:
                    self.progress.set(0)
            else:
                messagebox.showwarning("Atenție", "Încarcă mai întâi o imagine!")
        
        threading.Thread(target=recognize, daemon=True).start()
    
    def save_image(self):
        """Salvează imaginea curentă."""
        if self.current_image:
            file_path = filedialog.asksaveasfilename(
                title="Salvează imaginea",
                defaultextension=".png",
                filetypes=[
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg"),
                    ("Toate fișierele", "*.*")
                ]
            )
            
            if file_path:
                try:
                    self.current_image.save(file_path)
                    messagebox.showinfo("Succes", "Imaginea a fost salvată cu succes!")
                except Exception as e:
                    messagebox.showerror("Eroare", f"Nu s-a putut salva imaginea: {e}")
        else:
            messagebox.showwarning("Atenție", "Nu există imagine de salvat!")
    
    def reset_image(self):
        """Resetează imaginea la starea originală."""
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.display_image()
            self.update_info("Imaginea a fost resetată la starea originală.")
        else:
            messagebox.showwarning("Atenție", "Nu există imagine încărcată!")
    
    def run(self):
        """Pornește aplicația."""
        self.root.mainloop()
