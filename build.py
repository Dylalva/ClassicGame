#!/usr/bin/env python3
"""
Script para empaquetar el juego usando PyInstaller
"""

import os
import subprocess
import sys

def build_game():
    """Empaqueta el juego en un ejecutable"""
    print("Iniciando empaquetado del juego...")
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=DonkeyKongClassic",
        "--add-data=assets:assets",
        "--add-data=data:data",
        "--add-data=.env:.env",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("¡Juego empaquetado exitosamente!")
        print("El ejecutable se encuentra en la carpeta 'dist/'")
    except subprocess.CalledProcessError as e:
        print(f"Error al empaquetar: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("PyInstaller no encontrado. Instálalo con: pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    build_game()