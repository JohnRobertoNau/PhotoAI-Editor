# AI Photo Editor

An intelligent photo editor with AI capabilities for advanced image processing.

## Main Features

-  **AI Upscaling** - Image enlargement with Real-ESRGAN
-  **Background Removal** - Using U2NET and rembg
-  **Generative Fill** - Image completion with Stable Diffusion
-  **Image Recognition** - Descriptions with BLIP and classification with CLIP
-  **Modern UI** - Dark interface with CustomTkinter

## AI Models Used

### Advanced Systems (downloaded automatically):
- **Real-ESRGAN** - For professional upscaling
- **U2NET** - For background removal
- **Stable Diffusion Inpainting** - For generative fill
- **BLIP** - For image description
- **CLIP** - For image classification

### Smart Fallbacks:
- **LANCZOS + Sharpening** - For simple upscaling
- **Corner Detection** - For background removal
- **OpenCV Inpainting** - For image completion
- **Statistical Analysis** - For basic recognition

## Quick Start in WSL

### 1. Prepare WSL
```bash
# In WSL (Ubuntu recommended)
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv python3-tk -y
```

### 2. Project Setup
```bash
# Navigate to the project
cd /mnt/c/Projects/ai-editor

# Run the automatic setup
bash setup.sh
```

### 3. Start the Application
```bash
# Start the application
bash start.sh
```

## Detailed Installation

### Windows with WSL2 (Recommended)

1. **Install WSL2 and Ubuntu**:
   ```powershell
   wsl --install -d Ubuntu
   ```

2. **Prepare the system in WSL**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip python3-venv python3-dev python3-tk -y
   sudo apt install libopencv-dev python3-opencv build-essential -y
   ```

3. **Configure the project**:
   ```bash
   cd /mnt/c/Projects/ai-editor
   chmod +x setup.sh start.sh
   bash setup.sh
   ```

4. **Start the application**:
   ```bash
   bash start.sh
   ```

### Native Linux

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-editor

# Run the setup
bash setup.sh

# Start the application
bash start.sh
```

### Native Windows (alternative)

```powershell
# Create a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python main.py
```

## Advanced AI Features Setup

To enable full AI features:

1. **Edit `requirements.txt`** and uncomment:
   ```
   transformers>=4.30.0
   diffusers>=0.18.0
   rembg>=2.0.0
   ```

2. **Install AI dependencies**:
   ```bash
   source venv/bin/activate
   pip install transformers diffusers rembg
   ```

3. **Note**: The first run will download AI models (several GB, requires internet).

## Main Window & Intelligent Operations

The core of the application is the modern graphical interface, implemented in `src/ui/main_window.py`. This file manages the user experience, including:
- Image loading, display, and export
- Undo/redo functionality
- Interactive cropping, zoom, pan, and basic editing
- Integration of all AI-powered features
- Control panel with buttons for intelligent operations

### Intelligent Operations Modules

The following files in `src/models/` provide advanced AI capabilities:
- `background_remover.py`: Removes image backgrounds using AI (U2NET, rembg) or fallback methods
- `generative_fill.py`: Fills or completes image regions using Stable Diffusion or OpenCV inpainting
- `image_recognition.py`: Describes and classifies images using BLIP and CLIP, with basic analysis fallback
- `upscaler.py`: Enlarges images using Real-ESRGAN or simple interpolation

These modules are seamlessly integrated into the main window, allowing users to apply intelligent edits with a single click.

## Project Structure

```
ai-editor/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── setup.sh               # WSL install script
├── start.sh               # WSL launch script
├── WSL_SETUP.md           # Detailed WSL guide
├── src/
│   ├── ui/                # Graphical interface
│   │   └── main_window.py # Main window and UI logic
│   ├── models/            # AI models and intelligent operations
│   │   ├── upscaler.py
│   │   ├── background_remover.py
│   │   ├── generative_fill.py
│   │   └── image_recognition.py
│   └── utils/             # Utilities
│       ├── image_processor.py
│       └── model_manager.py
└── README.md
```

## Usage

1. **Load an image**: Click "Load Image"
2. **Apply operations**: Use the buttons in the left panel
3. **View the result**: The image updates in the center
4. **Save**: Click "Save" to export the result

## Debugging

### Common issues in WSL:

1. **GUI does not open**:
   ```bash
   # For WSL2 with WSLg (Windows 11)
   export DISPLAY=:0
   
   # For WSL2 with X11 (Windows 10)
   export DISPLAY=:0.0
   ```

2. **Tkinter error**:
   ```bash
   sudo apt install python3-tk
   ```

3. **OpenCV error**:
   ```bash
   sudo apt install libopencv-dev python3-opencv
   ```

### Dependency testing:

```bash
# Basic dependency test
python3 -c "import PIL, cv2, numpy, customtkinter; print('OK')"

# GUI test
python3 -c "import tkinter; print('GUI OK')"
```

## Modes of Operation

**Basic mode**: Works with minimal dependencies, offers:
- Basic image operations
- Filters and adjustments
- Simple analysis

**Advanced mode**: With full AI models, offers:
- AI upscaling
- AI background removal
- Generative fill
- Advanced recognition

The application automatically detects available dependencies and adapts.

## How to use it
- Enter venv: source venv/bin/activate
- Run main: python3 main.py
