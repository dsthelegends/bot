import os
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client
import asyncio
import random

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

# --- SISTEMA ECONOMIA ---
async def update_economy(user_id, amount):
    res = supabase.table("economy").select("*").eq("user_id", user_id).execute()
    if not res.data:
        supabase.table("economy").insert({"user_id": user_id, "wallet": amount, "messages_count": 1}).execute()
    else:
        new_wallet = res.data[0]['wallet'] + amount
        new_count = res.data[0]['messages_count'] + 1
        supabase.table("economy").update({"wallet": new_wallet, "messages_count": new_count}).eq("user_id", user_id).execute()

# --- EVENTI ---
@bot.event
async def on_ready():
    print(f"L E G E N D S ONLINE: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    await update_economy(message.author.id, random.randint(3, 9))
    await bot.process_commands(message)

# --- COMANDI UTENTE ---
@bot.tree.command(name="wallet", description="Visualizza il saldo")
async def wallet(interaction: discord.Interaction):
    res = supabase.table("economy").select("wallet").eq("user_id", interaction.user.id).execute()
    balance = res.data[0]['wallet'] if res.data else 0
    await interaction.response.send_message(f"💰 Saldo attuale: **{balance}** 🪙")

# --- PANNELLO ADMIN ---
class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Stato Database", style=discord.ButtonStyle.green)
    async def status(self, interaction: discord.Interaction, button: discord.ui.Button):
        res = supabase.table("economy").select("*", count="exact").execute()
        await interaction.response.send_message(f"✅ DB Online. Utenti: **{res.count}**", ephemeral=True)

@bot.tree.command(name="admin-panel", description="Dashboard L E G E N D S")
async def admin(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Accesso negato.", ephemeral=True)
    await interaction.response.send_message("⚡ **L E G E N D S  CONTROL**", view=AdminView(), ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)