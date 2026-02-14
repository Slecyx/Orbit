#!/bin/bash

# Orbit Installation Script
# This script installs Orbit and its dependencies

set -e

echo "🛰️  Orbit Installation Script"
echo "=============================="
echo ""

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "❌ Cannot detect distribution"
    exit 1
fi

echo "📋 Detected distribution: $DISTRO"
echo ""

# Install system dependencies based on distro
echo "📦 Installing system dependencies..."
case $DISTRO in
    ubuntu|debian|pop|linuxmint)
        sudo apt update
        sudo apt install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7
        ;;
    fedora)
        sudo dnf install -y python3 python3-gobject gtk4 libadwaita python3-notify2
        ;;
    arch|manjaro)
        sudo pacman -S --noconfirm python python-gobject gtk4 libadwaita python-notify2
        ;;
    *)
        echo "⚠️  Unsupported distribution: $DISTRO"
        echo "Please install dependencies manually:"
        echo "  - Python 3.8+"
        echo "  - python3-gi"
        echo "  - GTK 4"
        echo "  - libadwaita"
        echo "  - python3-notify2"
        exit 1
        ;;
esac

echo "✅ System dependencies installed"
echo ""

# Install Python dependencies
if [ -f requirements.txt ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install --user -r requirements.txt
    echo "✅ Python dependencies installed"
    echo ""
fi

# Create desktop entry
echo "🖥️  Creating desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/orbit.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Orbit
Comment=Universal Package Manager for Linux
Exec=python3 $(pwd)/main.py
Icon=system-software-install
Terminal=false
Type=Application
Categories=System;PackageManager;
Keywords=package;manager;apt;flatpak;snap;appimage;
EOF

echo "✅ Desktop entry created"
echo ""

# Make main.py executable
chmod +x main.py

echo "✅ Installation complete!"
echo ""
echo "🚀 You can now run Orbit by:"
echo "   1. Running: python3 main.py"
echo "   2. Searching for 'Orbit' in your application menu"
echo ""
echo "📚 For more information, see README.md"
