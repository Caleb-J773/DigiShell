import PyInstaller.__main__
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'launcher.py',
    '--name=DigiShell',
    '--onefile',
    '--console',
    '--icon=NONE',
    f'--add-data={os.path.join(project_root, "backend")};backend',
    f'--add-data={os.path.join(project_root, "frontend")};frontend',
    f'--add-data={os.path.join(project_root, "run_tui.py")};.',
    f'--add-data={os.path.join(project_root, "requirements.txt")};.',
    '--hidden-import=fastapi',
    '--hidden-import=uvicorn',
    '--hidden-import=textual',
    '--hidden-import=xmlrpc.client',
    '--collect-all=fastapi',
    '--collect-all=uvicorn',
    '--collect-all=textual',
    '--noconfirm',
])
