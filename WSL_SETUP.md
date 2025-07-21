# Ghid de configurare WSL pentru AI Photo Editor

## 📋 Pași pentru configurarea mediului în WSL

### 1. Pregătire WSL

Asigură-te că ai WSL2 instalat și o distribuție Linux (Ubuntu recomandată):

```bash
# Verifică versiunea WSL
wsl --version

# Dacă nu ai Ubuntu, instalează-l
wsl --install -d Ubuntu
```

### 2. Actualizare sistem și instalare Python

În WSL, rulează:

```bash
# Actualizează pachetele
sudo apt update && sudo apt upgrade -y

# Instalează Python și dependențele
sudo apt install python3 python3-pip python3-venv python3-dev -y

# Instalează dependențele pentru OpenCV
sudo apt install libopencv-dev python3-opencv -y

# Instalează dependențele pentru tkinter
sudo apt install python3-tk -y

# Pentru AI (opțional)
sudo apt install build-essential -y
```

### 3. Configurare proiect

```bash
# Navighează la directorul proiectului
cd /mnt/c/Projects/ai-editor

# Dă permisiuni de execuție script-urilor
chmod +x setup.sh start.sh

# Rulează setup-ul
bash setup.sh
```

### 4. Configurare GUI pentru WSL

#### Opțiunea A: WSLg (Windows 11 - Recomandat)
WSLg vine preinstalat în Windows 11. Nu necesită configurare suplimentară.

#### Opțiunea B: X11 Server (Windows 10)

1. Instalează VcXsrv sau Xming pe Windows
2. Pornește X Server cu setările:
   - Display number: 0
   - Start no client
   - Disable access control

3. În WSL, adaugă în `~/.bashrc`:
```bash
export DISPLAY=:0.0
```

#### Opțiunea C: Fără GUI (doar versiunea console)
Poți modifica aplicația să ruleze fără interfață grafică.

### 5. Testare

```bash
# Testează instalarea Python
python3 --version

# Testează importurile de bază
python3 -c "import PIL, cv2, numpy; print('✅ Dependențele de bază sunt OK')"

# Testează GUI
python3 -c "import tkinter; print('✅ GUI disponibil')"

# Pornește aplicația
bash start.sh
```

### 🔧 Debugging

#### Probleme comune:

1. **Eroare tkinter**: 
   ```bash
   sudo apt install python3-tk
   ```

2. **Eroare OpenCV**:
   ```bash
   sudo apt install libopencv-dev python3-opencv
   pip install opencv-python
   ```

3. **GUI nu se deschide**:
   - Verifică DISPLAY: `echo $DISPLAY`
   - Pentru WSL2: `export DISPLAY=:0.0`
   - Pentru WSLg: `export DISPLAY=:0`

4. **Eroare la import customtkinter**:
   ```bash
   pip install customtkinter
   ```

### 📚 Funcții disponibile

**Funcții de bază** (disponibile fără modele AI):
- Încărcare/salvare imagini
- Redimensionare și rotire
- Filtre de bază (blur, sharpen, sepia)
- Ajustări (luminozitate, contrast, saturație)
- Analiză de bază a imaginii

**Funcții avansate** (necesită modele AI):
- Upscaling inteligent
- Eliminare fundal cu AI
- Generative fill
- Recunoaștere avansată imagine

### 🚀 Pentru a activa funcțiile AI avansate:

1. Decomentează în `requirements.txt`:
   ```
   transformers>=4.30.0
   diffusers>=0.18.0
   rembg>=2.0.0
   ```

2. Instalează:
   ```bash
   pip install transformers diffusers rembg
   ```

3. Prima rulare va descărca modele (poate dura mult și necesită internet).

### 💡 Tips

- Pentru performanță mai bună, folosește GPU dacă ai CUDA disponibil
- Modelele AI necesită mult spațiu (GB) și RAM
- Pentru dezvoltare, folosește funcțiile de bază mai întâi
- Poți folosi aplicația și fără funcții AI - va detecta automat ce e disponibil
