import discord
from discord.ext import commands
from discord import app_commands
import json
import re

class BestemmieCounter:
    def __init__(self):
        self.data_file = "data/bestemmie.json"
        self.load_data()
        self.bestemmie_pattern = re.compile(r'\b(dio|madonna|gesù|cristo|porco)\w*\b', re.IGNORECASE)
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def count_bestemmie(self, message):
        user_id = str(message.author.id)
        if user_id not in self.data:
            self.data[user_id] = 0
        
        bestemmie = len(self.bestemmie_pattern.findall(message.content))
        self.data[user_id] += bestemmie
        self.save_data()
        return bestemmie

class Bestemmie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = BestemmieCounter()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        count = self.counter.count_bestemmie(message)
        if count > 0:
            print(f"Bestemmie rilevate: {count} da {message.author}")

    @app_commands.command(name="bestemmie", description="Mostra la classifica delle bestemmie")
    async def bestemmie(self, interaction: discord.Interaction):
        sorted_bestemmie = sorted(self.counter.data.items(), key=lambda x: x[1], reverse=True)[:10]
        
        embed = discord.Embed(title="😈 Classifica Bestemmie", color=discord.Color.red())
        for i, (user_id, count) in enumerate(sorted_bestemmie, 1):
            user = self.bot.get_user(int(user_id))
            username = user.name if user else "Utente Sconosciuto"
            embed.add_field(
                name=f"{i}. {username}",
                value=f"⚫ {count} bestemmie",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Bestemmie(bot))
