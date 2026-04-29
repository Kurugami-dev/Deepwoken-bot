# ===== ZEILE 1-50: IMPORTS & CONFIG =====
# Das sind die "Werkzeuge" die der Bot nutzt
import discord
from discord.ext import commands
import pymongo
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

# Konfiguration laden
load_dotenv()  # Liest .env Datei
TOKEN = os.getenv("DISCORD_TOKEN")  # Liest Token aus .env
MONGO_URL = os.getenv("MONGO_URL")  # Liest Datenbank URL
EVENT_CHANNEL_ID = int(os.getenv("EVENT_CHANNEL_ID"))


# ===== ZEILE 51-100: MONGODB VERBINDUNG =====
# Hier verbinden wir uns zur Datenbank

client = MongoClient(MONGO_URL)
db = client["deepwoken"]  # Datenbank Tabelle
events_collection = db["events"]  # Collection für Events

def add_event(event_name):
    """Speichert ein Event zu MongoDB"""
    berlin_tz = pytz.timezone("Europe/Berlin")
    now = datetime.now(berlin_tz)
    
    entry = {
        "timestamp": now.isoformat(),  # Zeit als Text
        "event_name": event_name,      # Z.B. "Interluminary Parasol"
        "hour": now.hour,              # Z.B. 14
        "minute": now.minute           # Z.B. 30
    }
    
    events_collection.insert_one(entry)  # Speichern!


# ===== ZEILE 101-200: PATTERN ERKENNUNG =====
# Der "Gehirn" des Bots

def get_event_transitions():
    """Findet: Was folgt nach welchem Event?"""
    data = list(events_collection.find())
    transitions = {}
    
    for i in range(len(data) - 1):
        current = data[i]["event_name"]
        next_event = data[i + 1]["event_name"]
        key = f"{current} → {next_event}"
        transitions[key] = transitions.get(key, 0) + 1
    
    return transitions

def predict_next_event():
    """Macht eine Vorhersage für den nächsten Event"""
    # Kombiniert 4 Faktoren:
    # 1. Was folgte bisher nach diesem Event?
    # 2. Was passiert um diese Uhrzeit normalerweise?
    # 3. Welcher Event ist am häufigsten?
    # 4. Welcher Tag der Woche ist es?
    
    # → Berechnet einen "Score" für jeden Event
    # → Gibt den mit höchstem Score zurück


# ===== ZEILE 201-300: DISCORD COMMANDS =====
# Was der Bot als Slash-Commands kann

@bot.tree.command(name="predict", description="Vorhersage für nächsten Boss")
async def predict(interaction: discord.Interaction):
    """User tippt /predict → Bot zeigt Vorhersage"""
    prediction = predict_next_event()
    
    embed = discord.Embed(
        title="🔮 Boss Vorhersage",
        description=f"Nächster Boss: {prediction['event']} ({prediction['confidence']}%)"
    )
    
    await interaction.response.send_message(embed=embed)


# ===== ZEILE 301-400: GITEA WEBHOOK SERVER =====
# Das ist DAS WICHTIGSTE für dich!

from fastapi import FastAPI, Request
import hmac
import hashlib

app = FastAPI()

@app.post("/webhook/gitea")
async def webhook_handler(request: Request):
    """
    Wenn du einen Commit pushst:
    1. Gitea sendet HTTP POST zu dieser URL
    2. Wir verifizieren das Secret
    3. Wir suchen nach Event-Namen im Commit
    4. Wir speichern das Event
    """
    
    # 1. SIGNATURE VERIFIZIEREN
    signature = request.headers.get("X-Gitea-Signature")
    body = await request.body()
    
    expected_sig = hmac.new(
        os.getenv("GITEA_WEBHOOK_SECRET").encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected_sig:
        return {"error": "Invalid signature"}  # Webhook war falsch!
    
    # 2. PAYLOAD PARSEN
    payload = await request.json()
    
    # 3. COMMIT MESSAGE LESEN
    if "commits" in payload:
        for commit in payload["commits"]:
            message = commit["message"].upper()
            
            # 4. EVENT SUCHEN
            if "INTERLUMINARY PARASOL" in message:
                add_event("Interluminary Parasol")
                return {"status": "Event gespeichert!"}
            
            elif "CARNIVAL OF HEARTS" in message:
                add_event("Carnival of Hearts")
                return {"status": "Event gespeichert!"}
            
            elif "BATTLE ROYALE" in message:
                add_event("Battle Royale")
                return {"status": "Event gespeichert!"}
    
    return {"status": "Kein Event gefunden"}


# ===== ZEILE 401-500: BOT START =====
# Der Bot startet

@bot.event
async def on_ready():
    print(f"✓ Bot eingeloggt als {bot.user}")
    await bot.tree.sync()

# Starte den Bot
bot.run(TOKEN)