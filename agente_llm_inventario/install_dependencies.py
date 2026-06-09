import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(PROJECT_ROOT, "requirements.txt")


def run_command(command):
    print(f"Ejecutando: {' '.join(command)}")
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"El comando falló con código {result.returncode}: {' '.join(command)}")


def main():
    python_exe = sys.executable
    print("Instalando dependencias con el intérprete activo:", python_exe)
    run_command([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([python_exe, "-m", "pip", "install", "wheel"])
    run_command([python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
    print("Instalación completada. Ahora puedes ejecutar: python run_agent.py")


if __name__ == "__main__":
    main()
