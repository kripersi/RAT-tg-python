import subprocess
import sys
import os


def install_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

    if not os.path.exists(requirements_path):
        return

    with open(requirements_path, "r", encoding="utf-8") as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith("#"):
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", package, "--quiet"], check=True)
                except subprocess.CalledProcessError:
                    pass


install_requirements()

