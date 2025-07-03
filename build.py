#!/usr/bin/env python3
"""
Script para empaquetar el juego Donkey Kong Classic usando PyInstaller
"""

import os
import subprocess
import sys
import shutil
import platform
from pathlib import Path

def check_requirements():
    """Verifica que todos los requisitos estén instalados"""
    print("Verificando requisitos...")
    
    # Verificar PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("✗ PyInstaller no encontrado")
        print("Instalando PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✓ PyInstaller instalado")
            # Verificar que se puede importar después de la instalación
            import PyInstaller
            print(f"✓ PyInstaller {PyInstaller.__version__} verificado")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error instalando PyInstaller: {e}")
            print("Intenta instalar manualmente: pip install pyinstaller")
            sys.exit(1)
        except ImportError:
            print("✗ PyInstaller instalado pero no se puede importar")
            print("Reinicia el script o instala manualmente: pip install pyinstaller")
            sys.exit(1)
    
    # Verificar archivos críticos
    if os.path.exists("main.py"):
        print("✓ main.py encontrado")
    else:
        print("✗ main.py no encontrado (REQUERIDO)")
        sys.exit(1)
    
    if os.path.exists("src"):
        print("✓ Directorio src/ encontrado")
    else:
        print("✗ Directorio src/ no encontrado (REQUERIDO)")
        sys.exit(1)
    
    # Verificar archivos opcionales
    optional_files = ["requirements.txt", ".env.example", "README.md"]
    for file in optional_files:
        if os.path.exists(file):
            print(f"✓ {file} encontrado")
        else:
            print(f"⚠️  {file} no encontrado (opcional)")

def clean_build():
    """Limpia archivos de builds anteriores"""
    print("Limpiando builds anteriores...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Eliminado {dir_name}/")
    
    # Limpiar archivos .spec
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✓ Eliminado {spec_file}")

def create_numpy_replacement():
    """Crea reemplazo simple de NumPy para evitar conflictos"""
    numpy_replacement = '''# Reemplazo simple de NumPy para PyInstaller
import random
import math

class SimpleArray:
    def __init__(self, data):
        if isinstance(data, (list, tuple)):
            self.data = list(data)
        else:
            self.data = [data]
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __setitem__(self, index, value):
        self.data[index] = value
    
    def __len__(self):
        return len(self.data)
    
    def argmax(self):
        return self.data.index(max(self.data))
    
    def max(self):
        return max(self.data)
    
    def zeros(self, shape):
        if isinstance(shape, int):
            return SimpleArray([0.0] * shape)
        return SimpleArray([[0.0] * shape[1] for _ in range(shape[0])])

def array(data):
    return SimpleArray(data)

def zeros(shape):
    if isinstance(shape, int):
        return SimpleArray([0.0] * shape)
    if isinstance(shape, (list, tuple)) and len(shape) == 2:
        return [[0.0] * shape[1] for _ in range(shape[0])]
    return SimpleArray([0.0] * shape)

def random_choice(choices):
    return random.choice(choices)

def exp(x):
    return math.exp(x)

def maximum(a, b):
    return max(a, b)

# Simular módulo random de numpy
class RandomModule:
    @staticmethod
    def random():
        return random.random()
    
    @staticmethod
    def choice(choices):
        return random.choice(choices)

random = RandomModule()
'''
    
    # Crear directorio src/utils si no existe
    os.makedirs('src/utils', exist_ok=True)
    
    with open('src/utils/numpy_replacement.py', 'w') as f:
        f.write(numpy_replacement)
    print("✓ Reemplazo de NumPy creado")

def create_spec_file():
    """Crea archivo .spec personalizado para PyInstaller"""
    print("Creando archivo de configuración...")
    
    # Crear reemplazo de NumPy
    create_numpy_replacement()
    
    # Verificar qué archivos y directorios existen
    data_files = []
    
    # Verificar directorios
    if os.path.exists('assets'):
        data_files.append("('assets', 'assets')")
        print("✓ assets/ encontrado")
    
    if os.path.exists('data'):
        data_files.append("('data', 'data')")
        print("✓ data/ encontrado")
    else:
        # Crear directorio data vacío
        os.makedirs('data', exist_ok=True)
        data_files.append("('data', 'data')")
        print("✓ data/ creado")
    
    # Verificar archivos opcionales
    optional_files = [
        ('.env.example', '.'),
        ('README.md', '.'),
        ('requirements.txt', '.')
    ]
    
    for file_path, dest in optional_files:
        if os.path.exists(file_path):
            data_files.append(f"('{file_path}', '{dest}')")
            print(f"✓ {file_path} encontrado")
    
    # Crear string de archivos de datos
    data_files_str = ',\n        '.join(data_files) if data_files else ''
    
    # Verificar icono
    icon_line = "None"
    if os.path.exists('assets/icon.ico'):
        icon_line = "'assets/icon.ico'"
    elif os.path.exists('assets/icon.png'):
        icon_line = "'assets/icon.png'"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        {data_files_str}
    ],
    hiddenimports=[
        'pygame',
        'requests',
        'dotenv',
        'json',
        'os',
        'random',
        'math',
        'time',
        'datetime',
        'src',
        'src.game',
        'src.entities',
        'src.managers',
        'src.ai',
        'src.ui',
        'src.utils',
        'src.utils.numpy_replacement'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'numpy'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DonkeyKongClassic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_line},
)
'''
    
    with open("DonkeyKongClassic.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✓ Archivo de configuración creado")

def build_game():
    """Empaqueta el juego usando el archivo .spec"""
    print("Iniciando empaquetado del juego...")
    
    # Verificar que PyInstaller esté disponible como comando
    pyinstaller_cmd = None
    
    # Intentar diferentes formas de ejecutar PyInstaller
    possible_commands = [
        "pyinstaller",
        [sys.executable, "-m", "PyInstaller"],
        [sys.executable, "-m", "pyinstaller"]
    ]
    
    for cmd_option in possible_commands:
        try:
            if isinstance(cmd_option, str):
                test_cmd = [cmd_option, "--version"]
            else:
                test_cmd = cmd_option + ["--version"]
            
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                pyinstaller_cmd = cmd_option
                print(f"✓ PyInstaller encontrado: {result.stdout.strip()}")
                break
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    if pyinstaller_cmd is None:
        print("✗ No se pudo encontrar PyInstaller")
        print("Intenta: pip install pyinstaller")
        return False
    
    # Construir comando final
    if isinstance(pyinstaller_cmd, str):
        final_cmd = [pyinstaller_cmd, "--clean", "--noconfirm", "DonkeyKongClassic.spec"]
    else:
        final_cmd = pyinstaller_cmd + ["--clean", "--noconfirm", "DonkeyKongClassic.spec"]
    
    try:
        print(f"Ejecutando: {' '.join(final_cmd)}")
        result = subprocess.run(final_cmd, check=True, capture_output=True, text=True)
        print("✓ Empaquetado completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error durante el empaquetado:")
        print(f"Código de salida: {e.returncode}")
        if e.stdout:
            print(f"Salida: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError as e:
        print(f"✗ Comando no encontrado: {e}")
        print("Verifica que PyInstaller esté instalado correctamente")
        return False

def post_build_setup():
    """Configuración post-build"""
    print("Configurando archivos post-build...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("✗ Directorio dist/ no encontrado")
        return False
    
    # Crear archivo .env de ejemplo en dist
    if os.path.exists(".env.example"):
        env_example_dist = dist_dir / ".env.example"
        shutil.copy2(".env.example", env_example_dist)
        print("✓ .env.example copiado a dist/")
    else:
        # Crear .env.example básico
        env_content = '''# Firebase Configuration
FIREBASE_API_KEY=your_api_key_here
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_PROJECT_ID=your-project-id

# Game Configuration
DEBUG_MODE=False
'''
        env_example_dist = dist_dir / ".env.example"
        with open(env_example_dist, "w") as f:
            f.write(env_content)
        print("✓ .env.example creado en dist/")
    
    # Crear README para el ejecutable
    readme_content = '''
# Donkey Kong Classic - Ejecutable

## Configuración Inicial

1. Copia .env.example a .env
2. Edita .env con tus credenciales de Firebase
3. Ejecuta DonkeyKongClassic.exe

## Controles
- Flechas/WASD: Movimiento
- Espacio/W: Saltar
- T: Abrir tienda
- F: Lanzar banana
- ESC: Pausar

## Soporte
Para soporte técnico, consulta la documentación completa en el repositorio.
'''
    
    readme_dist = dist_dir / "README.txt"
    with open(readme_dist, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✓ README.txt creado en dist/")
    
    return True

def create_installer():
    """Crea un instalador simple (opcional)"""
    print("Creando script de instalación...")
    
    if platform.system() == "Windows":
        installer_content = '''
@echo off
echo Instalando Donkey Kong Classic...
echo.
echo 1. Copia este ejecutable donde desees
echo 2. Copia .env.example a .env
echo 3. Edita .env con tus credenciales
echo 4. Ejecuta DonkeyKongClassic.exe
echo.
echo Instalacion completada!
pause
'''
        with open("dist/install.bat", "w") as f:
            f.write(installer_content)
        print("✓ install.bat creado")
    
    else:
        installer_content = '''
#!/bin/bash
echo "Instalando Donkey Kong Classic..."
echo ""
echo "1. Copia este ejecutable donde desees"
echo "2. Copia .env.example a .env"
echo "3. Edita .env con tus credenciales"
echo "4. Ejecuta ./DonkeyKongClassic"
echo ""
echo "Instalacion completada!"
'''
        with open("dist/install.sh", "w") as f:
            f.write(installer_content)
        os.chmod("dist/install.sh", 0o755)
        print("✓ install.sh creado")

def print_build_info():
    """Muestra información del build completado"""
    print("\n" + "="*50)
    print("🎮 BUILD COMPLETADO EXITOSAMENTE 🎮")
    print("="*50)
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        exe_name = "DonkeyKongClassic.exe" if platform.system() == "Windows" else "DonkeyKongClassic"
        exe_path = dist_dir / exe_name
        
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📁 Ubicación: {exe_path.absolute()}")
            print(f"📊 Tamaño: {file_size:.1f} MB")
            print(f"💻 Plataforma: {platform.system()} {platform.machine()}")
            
            print("\n📋 Archivos incluidos:")
            for item in dist_dir.iterdir():
                if item.is_file():
                    print(f"   • {item.name}")
            
            print("\n🚀 Para ejecutar:")
            if platform.system() == "Windows":
                print(f"   {exe_path.name}")
            else:
                print(f"   ./{exe_path.name}")
            
            print("\n⚙️  Configuración:")
            print("   1. Copia .env.example a .env")
            print("   2. Edita .env con credenciales Firebase")
            print("   3. Ejecuta el juego")
            
        else:
            print("✗ Ejecutable no encontrado en dist/")
    else:
        print("✗ Directorio dist/ no encontrado")
    
    print("\n" + "="*50)

def main():
    """Función principal del script de build"""
    print("🔨 DONKEY KONG CLASSIC - BUILD SCRIPT")
    print("="*40)
    
    try:
        # Verificar requisitos
        check_requirements()
        
        # Limpiar builds anteriores
        clean_build()
        
        # Crear archivo de configuración
        create_spec_file()
        
        # Empaquetar juego
        if not build_game():
            print("\n✗ Build falló")
            sys.exit(1)
        
        # Configuración post-build
        if not post_build_setup():
            print("\n⚠️  Build completado pero con advertencias")
        
        # Crear instalador
        create_installer()
        
        # Mostrar información del build
        print_build_info()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()