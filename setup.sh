#!/bin/bash

echo "🚀 Inițializarea mediului AI Photo Editor..."

# Verifică dacă Python este instalat
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nu este găsit. Te rog instalează Python3 mai întâi."
    exit 1
fi

echo "✅ Python găsit: $(python3 --version)"

# Creează environment virtual dacă nu există
if [ ! -d "venv" ]; then
    echo "📦 Creez environment virtual..."
    python3 -m venv venv
    echo "✅ Environment virtual creat"
else
    echo "✅ Environment virtual există deja"
fi

# Activează environment-ul virtual
echo "🔧 Activez environment-ul virtual..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Actualizez pip..."
pip install --upgrade pip

# Instalează dependențele de bază mai întâi
echo "📚 Instalez dependențele de bază..."
pip install wheel setuptools

# Instalează dependențele principale
echo "🎨 Instalez dependențele pentru editorul foto..."
pip install Pillow>=10.0.0
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
pip install customtkinter>=5.2.0
pip install scikit-learn>=1.3.0
pip install requests>=2.31.0
pip install tqdm>=4.65.0

echo "🤖 Instalez dependențele AI (poate dura câteva minute)..."

# Instalează PyTorch (CPU version pentru început)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Instalează dependențele pentru AI (optional, pentru funcții avansate)
echo "🧠 Instalez modele AI avansate (opțional)..."
pip install transformers>=4.30.0 || echo "⚠️ Nu s-au putut instala transformers (opțional)"
pip install diffusers>=0.18.0 || echo "⚠️ Nu s-au putut instala diffusers (opțional)" 
pip install rembg>=2.0.0 || echo "⚠️ Nu s-au putut instala rembg (opțional)"

echo ""
echo "🎉 Mediul a fost configurat cu succes!"
echo ""
echo "Pentru a folosi aplicația:"
echo "1. Activează environment-ul: source venv/bin/activate"
echo "2. Rulează aplicația: python main.py"
echo ""
echo "Note:"
echo "- Unele funcții AI avansate pot necesita modele suplimentare"
echo "- Pentru GPU support, reinstalează PyTorch cu CUDA"
echo "- Dacă ai probleme cu dependențele AI, aplicația va folosi funcții de bază"
