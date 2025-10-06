import discord
from discord.ext import commands
from discord import app_commands
import json

class CountingSystem:
    def __init__(self):
        self.data_file = "data/counting.json"
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"current_number": 0, "last_user": None, "channel_id": None}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.system = CountingSystem()
        self.counting_channel_id = 1386321343569592552  # Cambia con ID canale counting

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.counting_channel_id or message.author.bot:
            return
        
        try:
            user_number = eval(message.content)  # Permette operazioni matematiche
            expected_number = self.system.data["current_number"] + 1
            
            if user_number == expected_number and message.author.id != self.system.data["last_user"]:
                self.system.data["current_number"] = user_number
                self.system.data["last_user"] = message.author.id
                self.system.save_data()
                
                await message.add_reaction("✅")
            else:
                await message.add_reaction("❌")
                await message.reply(f"❌ Numero sbagliato! Il prossimo numero era **{expected_number}**. Ricominciamo da 1!")
                self.system.data["current_number"] = 0
                self.system.data["last_user"] = None
                self.system.save_data()
                
        except:
            await message.add_reaction("❌")
            await message.reply("❌ Inserisci un numero valido!")

    @app_commands.command(name="counting_stats", description="Statistiche counting")
    async def counting_stats(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔢 Statistiche Counting", color=discord.Color.blue())
        embed.add_field(name="Numero Corrente", value=self.system.data["current_number"], inline=True)
        
        if self.system.data["last_user"]:
            last_user = self.bot.get_user(self.system.data["last_user"])
            embed.add_field(name="Ultimo Utente", value=last_user.mention if last_user else "Sconosciuto", inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Counting(bot))
