import sys
import subprocess
import shutil

def banner():
    gradient = [27, 33, 39, 45, 51, 87, 123, 159, 195, 231]

    logo = [
        "███████████████╗  ████████╗ ██╗  ██╗ ██████╗ ███╗   ██╗",
        "╚══██╔════██╔══╝  ╚══██╔══╝ ██║  ██║██╔═══██╗████╗  ██║",
        "   ██║    ██║        ██║    ███████║██║   ██║██╔██╗ ██║",
        "   ██║     ██║       ██║    ██╔══██║██║   ██║██║╚██╗██║",
        "   ██║      ██║      ██║    ██║  ██║╚██████╔╝██║ ╚████║",
        "   ╚═╝      ╚═╝      ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝",
        "            πthon Dependency Installer             ",
    ]

    for line in logo:
        print("".join(
            f"\033[38;5;{gradient[i % len(gradient)]}m{ch}"
            for i, ch in enumerate(line)
        ) + "\033[0m")

    print("\n\033[1;37m>> Installation automatique des dépendances\n\033[0m")


def run(cmd, check=True):
    print(f"\033[38;5;208m$ {' '.join(cmd)}\033[0m")
    subprocess.run(cmd, check=check)


def ensure_pip():
    if shutil.which("pip") or shutil.which("pip3"):
        return
    run([sys.executable, "-m", "ensurepip", "--upgrade"])


def install_dependencies():
    banner()
    ensure_pip()

    pip = [sys.executable, "-m", "pip"]
    deps = ["PyQt5", "mysql-connector-python"]

    run(pip + ["install", "--upgrade", "pip", "setuptools", "wheel"], check=False)

    print("\033[1;32m[+] Installation des dépendances requises...\n\033[0m")

    for dep in deps:
        run(pip + ["install", "--upgrade", dep])

    print("\n\033[1;32m[✓] Toutes les dépendances sont installées avec succès.\033[0m")


if __name__ == "__main__":
    install_dependencies()
