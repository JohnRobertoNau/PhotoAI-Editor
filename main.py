import sys
import os
from pathlib import Path

# Adaugă directorul src la Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.main_window import PhotoEditorApp

def main():
    """Punctul de intrare principal al aplicației."""
    try:
        app = PhotoEditorApp()
        app.run()
    except Exception as e:
        print(f"Eroare la pornirea aplicației: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
