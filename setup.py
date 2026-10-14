#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K5FREE V3 - Safe Cross-Platform Setup Script
Safe replacement for outdated setup that used to break Termux
"""
import os
import sys
import subprocess
import platform

print("=" * 60)
print("[+] K5FREE V3 Dependency Installer (Fixed & Safe)")
print(f"[+] Python Version: {sys.version.split()[0]}")
print(f"[+] Operating System: {platform.system()} ({platform.machine()})")
print("=" * 60)

requirements = [
    'telethon>=1.34.0',
    'pyrogram>=2.0.106',
    'tgcrypto>=1.2.5',
    'colorama>=0.4.6',
    'requests>=2.31.0',
    'phonenumbers>=8.13.0',
    'beautifulsoup4>=4.12.0',
    'aiofiles>=23.2.0',
    'tabulate>=0.9.0'
]

def install_packages():
    print("[+] Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
    
    print("[+] Installing required Python packages...")
    for pkg in requirements:
        print(f"  -> Installing {pkg}...")
        res = subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)
        if res.returncode == 0:
            print(f"     [✓] Successfully installed {pkg.split('>=')[0]}")
        else:
            print(f"     [!] Warning: Failed to install {pkg}, skipping...")

    os.makedirs("sessions", exist_ok=True)
    os.makedirs("Problem", exist_ok=True)
    
    if not os.path.exists("Number.csv"):
        with open("Number.csv", "w", encoding="utf-8") as f:
            f.write("phone_number\n")
            
    if not os.path.exists("Contact-Number.csv"):
        with open("Contact-Number.csv", "w", encoding="utf-8") as f:
            f.write("first_name,last_name,phone_number\n")

    print("=" * 60)
    print("[✓] Setup completed successfully!")
    print("[✓] Run the tool with: python k5free.py")
    print("=" * 60)

if __name__ == "__main__":
    install_packages()
