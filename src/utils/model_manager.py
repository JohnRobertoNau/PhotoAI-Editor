import os
import torch
import requests
from pathlib import Path
import hashlib

class ModelManager:
    """Clasă pentru gestionarea modelelor AI (descărcare, cache, etc.)."""
    
    def __init__(self):
        self.models_dir = Path.home() / ".ai_photo_editor" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Dicționar cu informații despre modele
        self.model_info = {
            "upscaler": {
                "name": "Real-ESRGAN",
                "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                "filename": "RealESRGAN_x4plus.pth",
                "size": "67MB"
            },
            "background_remover": {
                "name": "U2-Net",
                "url": "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx",
                "filename": "u2net.onnx",
                "size": "176MB"
            }
        }
    
    def download_model(self, model_name, progress_callback=None):
        """
        Descarcă un model dacă nu există local.
        
        Args:
            model_name (str): Numele modelului
            progress_callback (callable): Funcție pentru actualizarea progresului
        
        Returns:
            str: Calea către modelul descărcat sau None dacă a eșuat
        """
        try:
            if model_name not in self.model_info:
                raise ValueError(f"Model necunoscut: {model_name}")
            
            model_data = self.model_info[model_name]
            model_path = self.models_dir / model_data["filename"]
            
            # Verifică dacă modelul există deja
            if model_path.exists():
                print(f"Modelul {model_name} există deja la: {model_path}")
                return str(model_path)
            
            print(f"Descărcare model {model_name} ({model_data['size']})...")
            
            # Descarcă modelul
            response = requests.get(model_data["url"], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = downloaded / total_size
                            progress_callback(progress)
            
            print(f"Modelul {model_name} descărcat cu succes la: {model_path}")
            return str(model_path)
            
        except Exception as e:
            print(f"Eroare la descărcarea modelului {model_name}: {e}")
            return None
    
    def get_model_path(self, model_name):
        """
        Returnează calea către un model local.
        
        Args:
            model_name (str): Numele modelului
        
        Returns:
            str: Calea către model sau None dacă nu există
        """
        try:
            if model_name not in self.model_info:
                return None
            
            model_data = self.model_info[model_name]
            model_path = self.models_dir / model_data["filename"]
            
            if model_path.exists():
                return str(model_path)
            
            return None
            
        except Exception as e:
            print(f"Eroare la obținerea căii modelului {model_name}: {e}")
            return None
    
    def list_available_models(self):
        """
        Returnează lista modelelor disponibile.
        
        Returns:
            list: Lista numele modelelor disponibile
        """
        return list(self.model_info.keys())
    
    def list_downloaded_models(self):
        """
        Returnează lista modelelor descărcate local.
        
        Returns:
            list: Lista numelor modelelor descărcate
        """
        downloaded = []
        for model_name in self.model_info.keys():
            if self.get_model_path(model_name):
                downloaded.append(model_name)
        return downloaded
    
    def delete_model(self, model_name):
        """
        Șterge un model de pe disc.
        
        Args:
            model_name (str): Numele modelului de șters
        
        Returns:
            bool: True dacă s-a șters cu succes, False altfel
        """
        try:
            model_path = self.get_model_path(model_name)
            if model_path:
                os.remove(model_path)
                print(f"Modelul {model_name} a fost șters.")
                return True
            else:
                print(f"Modelul {model_name} nu există local.")
                return False
                
        except Exception as e:
            print(f"Eroare la ștergerea modelului {model_name}: {e}")
            return False
    
    def get_model_info(self, model_name):
        """
        Returnează informații despre un model.
        
        Args:
            model_name (str): Numele modelului
        
        Returns:
            dict: Informații despre model
        """
        if model_name in self.model_info:
            info = self.model_info[model_name].copy()
            info["is_downloaded"] = self.get_model_path(model_name) is not None
            return info
        return None
    
    def verify_model_integrity(self, model_name):
        """
        Verifică integritatea unui model descărcat.
        
        Args:
            model_name (str): Numele modelului
        
        Returns:
            bool: True dacă modelul e integru, False altfel
        """
        try:
            model_path = self.get_model_path(model_name)
            if not model_path:
                return False
            
            # Pentru simplicitate, verificăm doar dacă fișierul există și nu e gol
            # În viitor se pot adăuga checksum-uri
            file_size = os.path.getsize(model_path)
            return file_size > 0
            
        except Exception as e:
            print(f"Eroare la verificarea integrității modelului {model_name}: {e}")
            return False
    
    def check_pytorch_device(self):
        """
        Verifică ce dispozitive sunt disponibile pentru PyTorch.
        
        Returns:
            dict: Informații despre dispozitivele disponibile
        """
        info = {
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "recommended_device": "cuda" if torch.cuda.is_available() else "cpu"
        }
        
        if torch.cuda.is_available():
            info["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        
        return info
    
    def cleanup_cache(self):
        """
        Curăță cache-ul de modele (șterge fișierele temporare).
        """
        try:
            temp_files = list(self.models_dir.glob("*.tmp"))
            for temp_file in temp_files:
                os.remove(temp_file)
                print(f"Șters fișier temporar: {temp_file}")
            
            print("Cache-ul a fost curățat.")
            
        except Exception as e:
            print(f"Eroare la curățarea cache-ului: {e}")
    
    def get_storage_usage(self):
        """
        Calculează spațiul folosit de modele.
        
        Returns:
            dict: Informații despre spațiul folosit
        """
        try:
            total_size = 0
            model_sizes = {}
            
            for model_name in self.model_info.keys():
                model_path = self.get_model_path(model_name)
                if model_path:
                    size = os.path.getsize(model_path)
                    model_sizes[model_name] = size
                    total_size += size
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "model_sizes": model_sizes,
                "models_dir": str(self.models_dir)
            }
            
        except Exception as e:
            print(f"Eroare la calcularea spațiului folosit: {e}")
            return {"total_size_bytes": 0, "total_size_mb": 0, "model_sizes": {}}
