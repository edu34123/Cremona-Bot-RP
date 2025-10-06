import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import time
from datetime import datetime, timedelta

class ShiftSystem:
    def __init__(self):
        self.shifts_file = "data/shifts.json"
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.shifts_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"active_shifts": {}, "leaderboard": {}}
    
    def save_data(self):
        with open(self.shifts_file, 'w') as f:
            json.dump(self.data, f, indent=4)

class Shift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.system = ShiftSystem()
        self.active_views = {}

    @app_commands.command(name="shift", description="Gestisci il tuo turno")
    @app_commands.choices(mode=[
        app_commands.Choice(name="inizia", value="start"),
        app_commands.Choice(name="pausa", value="pause"),
        app_commands.Choice(name="fine", value="end"),
        app_commands.Choice(name="classifica", value="leaderboard")
    ])
    async def shift(self, interaction: discord.Interaction, mode: app_commands.Choice[str]):
        user_id = str(interaction.user.id)
        
        if mode.value == "start":
            if user_id in self.system.data["active_shifts"]:
                await interaction.response.send_message("❌ Hai già un turno attivo!", ephemeral=True)
                return
            
            self.system.data["active_shifts"][user_id] = {
                "start_time": time.time(),
                "paused": False,
                "total_paused": 0,
                "pauses": []
            }
            self.system.save_data()
            
            view = ShiftView(self.bot, user_id)
            self.active_views[user_id] = view
            
            embed = discord.Embed(
                title="🔄 Turno Iniziato",
                description=f"**Operatore:** {interaction.user.mention}\n**Ora inizio:** <t:{int(time.time())}:T>",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        elif mode.value == "leaderboard":
            leaderboard = self.system.data.get("leaderboard", {})
            sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1].get("total_time", 0), reverse=True)[:10]
            
            embed = discord.Embed(title="🏆 Classifica Turni", color=discord.Color.gold())
            for i, (user_id, data) in enumerate(sorted_lb, 1):
                user = self.bot.get_user(int(user_id))
                username = user.name if user else "Utente Sconosciuto"
                total_hours = data.get("total_time", 0) / 3600
                embed.add_field(
                    name=f"{i}. {username}",
                    value=f"⏱️ {total_hours:.1f} ore",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)

class ShiftView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
    
    @discord.ui.button(label="⏸️ Pausa", style=discord.ButtonStyle.blurple)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Non puoi controllare questo turno!", ephemeral=True)
            return
        
        # Logica pausa
        await interaction.response.send_message("⏸️ Turno in pausa!", ephemeral=True)
    
    @discord.ui.button(label="⏹️ Termina", style=discord.ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Non puoi controllare questo turno!", ephemeral=True)
            return
        
        # Logica fine turno
        await interaction.response.send_message("⏹️ Turno terminato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Shift(bot))
