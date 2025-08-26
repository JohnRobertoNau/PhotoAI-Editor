#!/usr/bin/env python3
"""
Build script for AI Photo Editor
This script handles the PyInstaller build process and post-build fixes
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def copy_customtkinter_themes():
    """Copy CustomTkinter theme files to the distribution"""
    try:
        import customtkinter
        ctk_path = Path(customtkinter.__file__).parent
        
        # For onefile build
        dist_path = Path("dist/AI-Photo-Editor")
        if dist_path.exists():
            theme_dest = dist_path.parent / "customtkinter"
            if ctk_path.exists():
                shutil.copytree(ctk_path, theme_dest, dirs_exist_ok=True)
                print("✅ CustomTkinter themes copied for onefile build")
        
        # For onedir build
        dist_dir = Path("dist/AI-Photo-Editor")
        if dist_dir.is_dir():
            theme_dest = dist_dir / "customtkinter"
            if ctk_path.exists():
                shutil.copytree(ctk_path, theme_dest, dirs_exist_ok=True)
                print("✅ CustomTkinter themes copied for onedir build")
                
    except ImportError:
        print("⚠️ CustomTkinter not found, skipping theme copy")
    except Exception as e:
        print(f"⚠️ Failed to copy CustomTkinter themes: {e}")

def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    print("✅ Cleanup completed")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building AI Photo Editor executable...")
    
    # Check if spec file exists
    spec_file = "ai-editor.spec"
    if not os.path.exists(spec_file):
        print(f"❌ Spec file {spec_file} not found!")
        return False
    
    # Run PyInstaller
    cmd = f"pyinstaller {spec_file}"
    return run_command(cmd, "PyInstaller build")

def test_executable():
    """Test if the executable can be run"""
    print("\n🧪 Testing executable...")
    
    # Check if executable exists
    exe_path = None
    if os.path.exists("dist/AI-Photo-Editor.exe"):
        exe_path = "dist/AI-Photo-Editor.exe"
    elif os.path.exists("dist/AI-Photo-Editor/AI-Photo-Editor.exe"):
        exe_path = "dist/AI-Photo-Editor/AI-Photo-Editor.exe"
    
    if exe_path:
        print(f"✅ Executable found at: {exe_path}")
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"📦 File size: {file_size:.1f} MB")
        return True
    else:
        print("❌ Executable not found!")
        return False

def main():
    """Main build process"""
    print("🚀 AI Photo Editor Build Script")
    print("=" * 40)
    
    # Step 1: Clean previous builds
    clean_build()
    
    # Step 2: Build executable
    if not build_executable():
        print("\n❌ Build failed!")
        sys.exit(1)
    
    # Step 3: Copy theme files
    copy_customtkinter_themes()
    
    # Step 4: Test executable
    if test_executable():
        print("\n🎉 Build completed successfully!")
        print("\nYou can find your executable in the 'dist' folder.")
        print("To create a smaller, faster-loading build, edit the spec file")
        print("and uncomment the COLLECT section for directory distribution.")
    else:
        print("\n⚠️ Build completed but executable test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
