# 🧠 AI Photo Editor

Un editor foto inteligent cu capabilități AI pentru procesarea avansată a imaginilor.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![AI](https://img.shields.io/badge/AI-Enabled-orange.svg)

## ✨ Funcții Principale

- 🔍 **Upscaling AI** - Mărirea imaginilor cu Real-ESRGAN
- 🎭 **Eliminarea Fundalului** - Folosind U2NET și rembg
- 🎨 **Generative Fill** - Completarea imaginilor cu Stable Diffusion
- 👁️ **Recunoașterea Imaginilor** - Descrieri cu BLIP și clasificare cu CLIP
- 🖥️ **UI Modern** - Interfață întunecată cu CustomTkinter

## 🤖 Modele AI Folosite

### Sisteme Avansate (se descarcă automat):
- **Real-ESRGAN** - Pentru upscaling profesional
- **U2NET** - Pentru eliminarea fundalului
- **Stable Diffusion Inpainting** - Pentru generative fill
- **BLIP** - Pentru descrierea imaginilor
- **CLIP** - Pentru clasificarea imaginilor

### Fallback-uri Inteligente:
- **LANCZOS + Sharpening** - Pentru upscaling simplu
- **Detecție pe colțuri** - Pentru eliminarea fundalului
- **OpenCV Inpainting** - Pentru completarea imaginilor
- **Analiză statistică** - Pentru recunoașterea de bază

## 🚀 Start rapid în WSL

### 1. Pregătire WSL
```bash
# În WSL (Ubuntu recomandat)
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv python3-tk -y
```

### 2. Configurare proiect
```bash
# Navighează la proiect
cd /mnt/c/Projects/ai-editor

# Rulează setup-ul automat
bash setup.sh
```

### 3. Pornire aplicație
```bash
# Pornește aplicația
bash start.sh
```

## 📝 Instalare detaliată

### Windows cu WSL2 (Recomandat)

1. **Instalează WSL2 și Ubuntu**:
   ```powershell
   wsl --install -d Ubuntu
   ```

2. **În WSL, pregătește sistemul**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip python3-venv python3-dev python3-tk -y
   sudo apt install libopencv-dev python3-opencv build-essential -y
   ```

3. **Configurează proiectul**:
   ```bash
   cd /mnt/c/Projects/ai-editor
   chmod +x setup.sh start.sh
   bash setup.sh
   ```

4. **Pornește aplicația**:
   ```bash
   bash start.sh
   ```

### Linux nativ

```bash
# Clonează repository-ul
git clone <your-repo-url>
cd ai-editor

# Rulează setup-ul
bash setup.sh

# Pornește aplicația
bash start.sh
```

### Windows nativ (alternativ)

```powershell
# Creează environment virtual
python -m venv venv
venv\Scripts\activate

# Instalează dependențele
pip install -r requirements.txt

# Pornește aplicația
python main.py
```

## 🔧 Configurare funcții AI avansate

Pentru a activa funcțiile AI complete:

1. **Editează `requirements.txt`** și decomentează:
   ```
   transformers>=4.30.0
   diffusers>=0.18.0
   rembg>=2.0.0
   ```

2. **Instalează dependențele AI**:
   ```bash
   source venv/bin/activate
   pip install transformers diffusers rembg
   ```

3. **Notă**: Prima rulare va descărca modele AI (câteva GB, necesită internet).

## 📁 Structura proiectului

```
ai-editor/
├── main.py                 # Aplicația principală
├── requirements.txt        # Dependențe Python
├── setup.sh               # Script instalare WSL
├── start.sh               # Script pornire WSL
├── WSL_SETUP.md           # Ghid detaliat WSL
├── src/
│   ├── ui/                # Interfața grafică
│   │   └── main_window.py
│   ├── models/            # Modelele AI
│   │   ├── upscaler.py
│   │   ├── background_remover.py
│   │   ├── generative_fill.py
│   │   └── image_recognition.py
│   └── utils/             # Utilități
│       ├── image_processor.py
│       └── model_manager.py
└── README.md
```

## 🎮 Utilizare

1. **Încarcă o imagine**: Click pe "Încarcă Imagine"
2. **Aplică operații**: Folosește butoanele din panelul stâng
3. **Vizualizează rezultatul**: Imaginea se actualizează în centru
4. **Salvează**: Click pe "Salvează" pentru a exporta rezultatul

## 🔍 Debugging

### Probleme comune în WSL:

1. **GUI nu se deschide**:
   ```bash
   # Pentru WSL2 cu WSLg (Windows 11)
   export DISPLAY=:0
   
   # Pentru WSL2 cu X11 (Windows 10)
   export DISPLAY=:0.0
   ```

2. **Eroare tkinter**:
   ```bash
   sudo apt install python3-tk
   ```

3. **Eroare OpenCV**:
   ```bash
   sudo apt install libopencv-dev python3-opencv
   ```

### Testare dependențe:

```bash
# Test dependențe de bază
python3 -c "import PIL, cv2, numpy, customtkinter; print('✅ OK')"

# Test GUI
python3 -c "import tkinter; print('✅ GUI OK')"
```

## 🎯 Moduri de funcționare

**Mod de bază**: Funcționează cu dependențele minime, oferă:
- Operații de bază pe imagini
- Filtre și ajustări
- Analiză simplă

**Mod avansat**: Cu modele AI complete, oferă:
- Upscaling AI
- Eliminare fundal AI
- Generative fill
- Recunoaștere avansată

Aplicația detectează automat ce dependențe sunt disponibile și se adaptează.

## 🤝 Contribuții

Contribuțiile sunt binevenite! Pentru modificări majore:

1. Fork repository-ul
2. Creează o branch pentru feature
3. Commit modificările
4. Push și creează Pull Request

## 📄 Licența

MIT License
