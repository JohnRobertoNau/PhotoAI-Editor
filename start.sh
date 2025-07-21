#!/bin/bash

# Script pentru a porni aplicația AI Photo Editor în WSL

echo "🎨 AI Photo Editor - Starting in WSL..."

# Verifică dacă suntem în directorul corect
if [ ! -f "main.py" ]; then
    echo "❌ Nu sunt în directorul corect. Navighez la proiect..."
    cd /mnt/c/Projects/ai-editor || {
        echo "❌ Nu pot găsi directorul proiectului. Asigură-te că ești în /mnt/c/Projects/ai-editor"
        exit 1
    }
fi

# Verifică dacă environment-ul virtual există
if [ ! -d "venv" ]; then
    echo "❌ Environment-ul virtual nu există. Rulează mai întâi setup.sh"
    echo "bash setup.sh"
    exit 1
fi

# Activează environment-ul virtual
echo "🔧 Activez environment-ul virtual..."
source venv/bin/activate

# Verifică dependențele
echo "📋 Verific dependențele..."
python -c "import PIL, cv2, numpy, customtkinter" 2>/dev/null || {
    echo "❌ Unele dependențe lipsesc. Instalez dependențele de bază..."
    pip install Pillow opencv-python numpy customtkinter scikit-learn
}

# Exportă DISPLAY pentru WSL2 (dacă folosești X11)
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0.0
fi

# Alternativ pentru WSLg (Windows 11)
# export DISPLAY=:0

echo "🚀 Pornesc aplicația..."
python main.py

echo "👋 Aplicația s-a închis."
