#!/usr/bin/env python3
"""
Script pentru repararea problemelor de compatibilitate cu Real-ESRGAN
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Rulează o comandă și afișează progresul."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def fix_realesrgan():
    """Repară problemele de compatibilitate cu Real-ESRGAN."""
    print("🚀 Reparare compatibilitate Real-ESRGAN...")
    
    # Dezinstalează versiunile problematice
    commands = [
        ("pip uninstall -y realesrgan basicsr", "Dezinstalare versiuni problematice"),
        ("pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2", "Instalare PyTorch compatibil"),
        ("pip install --no-cache-dir basicsr==1.4.2", "Instalare BasicSR"),
        ("pip install --no-cache-dir realesrgan", "Instalare Real-ESRGAN"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
    
    print(f"\n📊 Rezultat: {success_count}/{len(commands)} comenzi executate cu succes")
    
    # Test final
    print("\n🧪 Test final...")
    test_cmd = 'python3 -c "from realesrgan import RealESRGANer; print(\'Real-ESRGAN funcționează!\')"'
    if run_command(test_cmd, "Test import Real-ESRGAN"):
        print("\n🎉 Real-ESRGAN reparat cu succes!")
        return True
    else:
        print("\n😞 Real-ESRGAN încă nu funcționează. Aplicația va folosi fallback-ul.")
        return False

if __name__ == "__main__":
    print("🛠️  Script de reparare Real-ESRGAN")
    print("=" * 50)
    
    try:
        success = fix_realesrgan()
        if success:
            print("\n✨ Poți rula acum: python3 main.py")
        else:
            print("\n💡 Aplicația va funcționa oricum cu metodele simple de upscaling.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Script întrerupt de utilizator.")
    except Exception as e:
        print(f"\n❌ Eroare neașteptată: {e}")
        print("💡 Aplicația va funcționa oricum cu metodele simple.")
