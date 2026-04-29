#!/bin/bash

# 🎮 Deepwoken Bot Setup Script

echo "🚀 Deepwoken World Event Tracker Bot - Setup"
echo "=============================================="

# Python Version prüfen
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nicht gefunden! Bitte installieren: https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION gefunden"

# Virtual Environment erstellen
if [ ! -d "venv" ]; then
    echo "📦 Erstelle Virtual Environment..."
    python3 -m venv venv
    echo "✓ Virtual Environment erstellt"
fi

# Aktivieren
echo "🔧 Aktiviere Virtual Environment..."
source venv/bin/activate

# Dependencies installieren
echo "📥 Installiere Dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✅ Setup erfolgreich!"
echo ""
echo "📋 Nächste Schritte:"
echo "1. .env Datei erstellen: cp .env.example .env"
echo "2. .env bearbeiten: nano .env"
echo "3. MongoDB starten: docker-compose up -d mongodb"
echo "4. Bot starten: python bot.py"
echo ""
echo "📚 Weitere Infos: cat SETUP_GUIDE.md"
echo ""
