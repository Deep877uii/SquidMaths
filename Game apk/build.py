import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def check_requirements():
    """Check if all required files and directories exist."""
    required_files = [
        'web_app.py',
        'launcher.py',
        'quizbuilder.py',
        'config.py',
        'templates/game.html',
        'templates/dashboard.html',
        'static/assets/background.jpg',
        'static/assets/player.png',
        'icon.ico'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"- {file}")
        return False
    return True

def create_spec_file():
    """Create a PyInstaller spec file."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add data files
data_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('questions.json', '.'),
    ('users.csv', '.'),
    ('config.py', '.'),
    ('icon.ico', '.')
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='QuizGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
"""
    with open('QuizGame.spec', 'w') as f:
        f.write(spec_content)

def build_executable():
    """Build the executable for the current platform."""
    os_name = platform.system().lower()
    
    # Create spec file
    create_spec_file()
    
    print(f"Building for {os_name}...")
    try:
        # Build using PyInstaller
        subprocess.run([
            sys.executable, 
            '-m', 
            'PyInstaller',
            'QuizGame.spec',
            '--clean'
        ], check=True)
        
        # Create distribution directory
        dist_dir = f'dist/QuizGame-{os_name}'
        os.makedirs(dist_dir, exist_ok=True)
        
        # Copy executable and dependencies
        if os_name == 'windows':
            shutil.copy('dist/QuizGame.exe', f'{dist_dir}/QuizGame.exe')
            # Create Windows shortcut
            create_windows_shortcut(dist_dir)
        else:
            shutil.copy('dist/QuizGame', f'{dist_dir}/QuizGame')
            # Make executable for Unix-like systems
            os.chmod(f'{dist_dir}/QuizGame', 0o755)
        
        # Copy additional files
        shutil.copytree('templates', f'{dist_dir}/templates', dirs_exist_ok=True)
        shutil.copytree('static', f'{dist_dir}/static', dirs_exist_ok=True)
        
        # Create empty data files if they don't exist
        Path(f'{dist_dir}/users.csv').touch()
        if not os.path.exists('questions.json'):
            create_default_questions(f'{dist_dir}/questions.json')
        else:
            shutil.copy('questions.json', f'{dist_dir}/questions.json')
        
        print(f"\nBuild completed successfully!")
        print(f"Executable can be found in: {os.path.abspath(dist_dir)}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        return False

def create_windows_shortcut(dist_dir):
    """Create Windows shortcut for the application."""
    if platform.system().lower() == 'windows':
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "QuizGame.lnk")
            target = os.path.join(os.path.abspath(dist_dir), "QuizGame.exe")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = os.path.abspath(dist_dir)
            shortcut.IconLocation = os.path.join(os.path.abspath(dist_dir), "icon.ico")
            shortcut.save()
            
            print("Desktop shortcut created successfully!")
        except Exception as e:
            print(f"Warning: Could not create desktop shortcut: {e}")

def create_default_questions(filepath):
    """Create a default questions.json file."""
    default_questions = {
        "title": "Math Quiz",
        "Time": "60",
        "Difficulty": "2",
        "MinQuestion": "3",
        "questions": [
            {
                "text": "What is 2 + 2?",
                "answer": "4",
                "difficulty": 1
            }
        ]
    }
    with open(filepath, 'w') as f:
        import json
        json.dump(default_questions, f, indent=4)

def main():
    print("=== QuizGame Builder ===")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        return False
    
    # Check requirements
    if not check_requirements():
        print("\nPlease ensure all required files are present and try again.")
        return False
    
    # Build executable
    if not build_executable():
        print("\nBuild failed. Please check the error messages above.")
        return False
    
    print("\nBuild process completed successfully!")
    return True

if __name__ == "__main__":
    main() 