#!/bin/bash
echo "============================================="
echo "   K5FREE V3 - RADHE Edition Setup & Run"
echo "============================================="

echo "[1/4] Updating Termux packages..."
pkg update -y && pkg upgrade -y

echo "[2/4] Installing Python, Git, and build tools..."
pkg install python git clang libffi openssl -y

echo "[3/4] Installing Python requirements..."
pip install --upgrade pip
pip install telethon pyrogram tgcrypto colorama requests phonenumbers tabulate

echo "[4/4] Starting K5FREE V3..."
python k5free.py
