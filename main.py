import os
import discord
from discord.ext import commands
from supabase import create_client, Client
import random
from flask import Flask
from threading import Thread

# --- SERVER CIVETTA PER KOYEB ---
app = Flask('')
@app.route('/')
def home():
    return "L E G E N D S is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8000)

# --- CONFIGURAZIONE CORE L E G E N D S ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TOKEN = os.getenv("DISCORD_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class LegendsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = LegendsBot()

@bot.event
async def on_ready():
    print(f"L E G E N D S ONLINE: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    # Sistema economia semplice
    res = supabase.table("economy").select("*").eq("user_id", message.author.id).execute()
    amount = random.randint(3, 9)
    if not res.data:
        supabase.table("economy").insert({"user_id": message.author.id, "wallet": amount}).execute()
    else:
        new_wallet = res.data[0]['wallet'] + amount
        supabase.table("economy").update({"wallet": new_wallet}).eq("user_id", message.author.id).execute()

@bot.tree.command(name="wallet", description="Vedi il saldo")
async def wallet(interaction: discord.Interaction):
    res = supabase.table("economy").select("wallet").eq("user_id", interaction.user.id).execute()
    balance = res.data[0]['wallet'] if res.data else 0
    await interaction.response.send_message(f"💰 Saldo: **{balance}** 🪙")

if __name__ == "__main__":
    # Avvia il server web in un thread separato
    Thread(target=run_web).start()
    # Avvia il bot
    bot.run(TOKEN)
