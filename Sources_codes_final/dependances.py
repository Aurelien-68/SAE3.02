import sys
import subprocess
import shutil
import platform


def banner():
    gradient = [27, 33, 39, 45, 51, 87, 123, 159, 195, 231]
    logo = [
        "███████████████╗  ████████╗ ██╗  ██╗ ██████╗ ███╗   ██╗",
        "╚══██╔════██╔══╝  ╚══██╔══╝ ██║  ██║██╔═══██╗████╗  ██║",
        "   ██║    ██║        ██║    ███████║██║   ██║██╔██╗ ██║",
        "   ██║     ██║       ██║    ██╔══██║██║   ██║██║╚██╗██║",
        "   ██║      ██║      ██║    ██║  ██║╚██████╔╝██║ ╚████║",
        "   ╚═╝      ╚═╝      ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝",
        "            Python Dependency Installer              ",
    ]

    for line in logo:
        print("".join(
            f"\033[38;5;{gradient[i % len(gradient)]}m{ch}"
            for i, ch in enumerate(line)
        ) + "\033[0m")

    print("\n\033[1;37m>> Installation automatique des dépendances\n\033[0m")


def run(cmd):
    print(f"\033[38;5;208m$ {' '.join(cmd)}\033[0m")
    subprocess.run(cmd, check=True)


# ---------- LINUX ----------
def install_linux():
    print("\033[1;32m[+] OS détecté : Linux (APT + pip forcé)\033[0m\n")

    run(["sudo", "apt", "update"])

    # Paquets système
    run([
        "sudo", "apt", "install", "-y",
        "python3-pyqt5",
        "python3-pip"
    ])

    # MySQL connector via pip (PEP 668 contourné)
    run([
        sys.executable, "-m", "pip",
        "install",
        "--break-system-packages",
        "mysql-connector-python"
    ])




# ---------- WINDOWS ----------
def install_windows():
    print("\033[1;32m[+] OS détecté : Windows (pip)\033[0m\n")
    pip = [sys.executable, "-m", "pip"]
    run(pip + ["install", "--upgrade", "pip"])
    run(pip + ["install", "PyQt5", "mysql-connector-python"])


# ---------- macOS ----------
def install_macos():
    print("\033[1;32m[+] OS détecté : macOS (Homebrew)\033[0m\n")

    if not shutil.which("brew"):
        print(" Homebrew n’est pas installé.")
        print("-> https://brew.sh")
        sys.exit(1)

    run(["brew", "update"])
    run(["brew", "install", "pyqt"])
    run(["brew", "install", "mysql-connector-python"])


def install_dependencies():
    banner()
    system = platform.system()

    if system == "Linux":
        install_linux()
    elif system == "Windows":
        install_windows()
    elif system == "Darwin":
        install_macos()
    else:
        print(f"❌ OS non supporté : {system}")
        sys.exit(1)

    print("\n\033[1;32m[✓] Dépendances installées avec succès.\033[0m")


if __name__ == "__main__":
    install_dependencies()
