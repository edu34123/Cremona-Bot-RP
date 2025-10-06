import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        
        self.persistent_views_added = False

    async def setup_hook(self):
        # Carica tutti i cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ {filename} caricato")
                except Exception as e:
                    print(f"❌ Errore {filename}: {e}")
        
        # Sync comandi globali
        await self.tree.sync()
        print("✅ Comandi slash sincronizzati")

bot = Bot()

@bot.event
async def on_ready():
    print(f"✅ {bot.user} è online!")
    await bot.change_presence(activity=discord.Game("🚨 Cremona RP"))

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ Token non trovato!")
        exit(1)
    bot.run(token)
