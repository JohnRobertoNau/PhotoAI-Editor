#!/bin/bash

# AI Photo Editor Build Script for WSL/Linux
# ==========================================

echo "🚀 AI Photo Editor Build Script (WSL/Linux)"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a virtual environment
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_error "Virtual environment not activated!"
        echo "Please activate your virtual environment first:"
        echo "source venv/bin/activate"
        exit 1
    else
        print_success "Virtual environment detected: $VIRTUAL_ENV"
    fi
}

# Clean previous build artifacts
clean_build() {
    print_status "🧹 Cleaning previous build artifacts..."
    
    # Remove build directories
    rm -rf build dist __pycache__
    
    # Clean .pyc files recursively
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Check dependencies
check_dependencies() {
    print_status "🔍 Checking dependencies..."
    
    # Check if PyInstaller is installed
    if ! python -c "import PyInstaller" 2>/dev/null; then
        print_error "PyInstaller not found!"
        echo "Install it with: pip install pyinstaller"
        exit 1
    fi
    
    # Check if main.py exists
    if [[ ! -f "main.py" ]]; then
        print_error "main.py not found!"
        exit 1
    fi
    
    # Check if spec file exists
    if [[ ! -f "ai-editor.spec" ]]; then
        print_error "ai-editor.spec not found!"
        exit 1
    fi
    
    print_success "All dependencies found"
}

# Build the executable
build_executable() {
        # Download AI models if needed
    if command -v python3 >/dev/null 2>&1; then
        print_section "📦 Preparing AI Models"
        
        if [ -f "bundle_models.py" ]; then
            print_info "Downloading AI models..."
            python3 bundle_models.py
            
            if [ $? -eq 0 ]; then
                print_success "AI models prepared successfully!"
            else
                print_warning "AI model preparation failed, continuing anyway..."
            fi
        else
            print_warning "bundle_models.py not found, skipping model preparation"
        fi
    fi
    
    print_section "🔨 Building with PyInstaller"
    
    # Run PyInstaller
    if python -m PyInstaller ai-editor.spec; then
        print_success "PyInstaller build completed"
        return 0
    else
        print_error "PyInstaller build failed"
        return 1
    fi
}

# Copy CustomTkinter themes if needed
copy_themes() {
    print_status "📁 Checking for CustomTkinter themes..."
    
    python3 << 'EOF'
import sys
import shutil
from pathlib import Path

try:
    import customtkinter
    ctk_path = Path(customtkinter.__file__).parent
    
    # Check for onefile build
    exe_file = Path("dist/AI-Photo-Editor")
    if exe_file.exists() and exe_file.is_file():
        theme_dest = Path("dist/customtkinter")
        if ctk_path.exists():
            shutil.copytree(ctk_path, theme_dest, dirs_exist_ok=True)
            print("✅ CustomTkinter themes copied for onefile build")
    
    # Check for onedir build
    exe_dir = Path("dist/AI-Photo-Editor")
    if exe_dir.exists() and exe_dir.is_dir():
        theme_dest = exe_dir / "customtkinter"
        if ctk_path.exists():
            shutil.copytree(ctk_path, theme_dest, dirs_exist_ok=True)
            print("✅ CustomTkinter themes copied for onedir build")
            
except ImportError:
    print("⚠️ CustomTkinter not found, skipping theme copy")
except Exception as e:
    print(f"⚠️ Failed to copy CustomTkinter themes: {e}")
EOF
}

# Test the executable
test_executable() {
    print_status "🧪 Testing executable..."
    
    # Check for executable
    if [[ -f "dist/AI-Photo-Editor" ]]; then
        exe_path="dist/AI-Photo-Editor"
        print_success "Executable found: $exe_path"
        
        # Check if it's executable
        if [[ -x "$exe_path" ]]; then
            print_success "Executable has proper permissions"
        else
            print_warning "Making executable..."
            chmod +x "$exe_path"
        fi
        
        # Show file size
        size=$(du -h "$exe_path" | cut -f1)
        echo "📦 File size: $size"
        
        return 0
    elif [[ -f "dist/AI-Photo-Editor/AI-Photo-Editor" ]]; then
        exe_path="dist/AI-Photo-Editor/AI-Photo-Editor"
        print_success "Executable found: $exe_path"
        
        # Check if it's executable
        if [[ -x "$exe_path" ]]; then
            print_success "Executable has proper permissions"
        else
            print_warning "Making executable..."
            chmod +x "$exe_path"
        fi
        
        # Show file size
        size=$(du -h "$exe_path" | cut -f1)
        echo "📦 File size: $size"
        
        return 0
    else
        print_error "Executable not found!"
        return 1
    fi
}

# Create Windows-compatible version if needed
create_windows_version() {
    print_status "🪟 Checking for Windows compatibility..."
    
    # If running on WSL, we can create a .exe version for Windows
    if grep -q Microsoft /proc/version 2>/dev/null; then
        print_status "WSL detected - executable will work on Windows"
        
        # Copy to Windows-accessible location if desired
        windows_path="/mnt/c/temp/AI-Photo-Editor"
        if [[ -d "/mnt/c/temp" ]]; then
            print_status "Copying to Windows temp folder..."
            cp -r dist "$windows_path" 2>/dev/null || true
            print_success "Copied to $windows_path"
        fi
    fi
}

# Main build process
main() {
    echo
    
    # Step 1: Check virtual environment
    check_venv
    
    # Step 2: Check dependencies
    check_dependencies
    
    # Step 3: Clean previous builds
    clean_build
    
    # Step 4: Build executable
    if ! build_executable; then
        print_error "Build failed!"
        exit 1
    fi
    
    # Step 5: Copy theme files
    copy_themes
    
    # Step 6: Test executable
    if ! test_executable; then
        print_warning "Build completed but executable test failed!"
        exit 1
    fi
    
    # Step 7: Windows compatibility check
    create_windows_version
    
    echo
    print_success "🎉 Build completed successfully!"
    echo
    echo "📁 You can find your executable in the 'dist' folder."
    echo "💡 To create a smaller, faster-loading build, edit ai-editor.spec"
    echo "   and uncomment the COLLECT section for directory distribution."
    echo
    
    # Show final directory structure
    print_status "📋 Build output:"
    ls -la dist/
}

# Run main function
main
