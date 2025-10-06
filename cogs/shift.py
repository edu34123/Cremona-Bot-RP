import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import time
from datetime import datetime, timedelta
import os

class ShiftSystem:
    def __init__(self):
        self.data_dir = "data"
        self.shifts_file = f"{self.data_dir}/shifts.json"
        self.ensure_data_dir()
        self.load_data()
    
    def ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_data(self):
        try:
            with open(self.shifts_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"active_shifts": {}, "leaderboard": {}}
    
    def save_data(self):
        with open(self.shifts_file, 'w') as f:
            json.dump(self.data, f, indent=4)

class ShiftView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.system = ShiftSystem()
    
    @discord.ui.button(label="⏸️ Pausa", style=discord.ButtonStyle.blurple, custom_id="pause_shift")
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Non puoi controllare questo turno!", ephemeral=True)
            return
        
        user_data = self.system.data["active_shifts"].get(self.user_id)
        if not user_data:
            await interaction.response.send_message("❌ Turno non trovato!", ephemeral=True)
            return
        
        if user_data["paused"]:
            # Riprendi turno
            user_data["paused"] = False
            pause_duration = time.time() - user_data["pauses"][-1]["start"]
            user_data["total_paused"] += pause_duration
            user_data["pauses"][-1]["end"] = time.time()
            user_data["pauses"][-1]["duration"] = pause_duration
            
            button.label = "⏸️ Pausa"
            button.style = discord.ButtonStyle.blurple
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("▶️ Turno ripreso!", ephemeral=True)
        else:
            # Metti in pausa
            user_data["paused"] = True
            user_data["pauses"].append({"start": time.time(), "end": None, "duration": 0})
            
            button.label = "▶️ Riprendi"
            button.style = discord.ButtonStyle.green
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("⏸️ Turno in pausa!", ephemeral=True)
        
        self.system.save_data()
    
    @discord.ui.button(label="⏹️ Termina", style=discord.ButtonStyle.red, custom_id="end_shift")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Non puoi controllare questo turno!", ephemeral=True)
            return
        
        user_data = self.system.data["active_shifts"].get(self.user_id)
        if not user_data:
            await interaction.response.send_message("❌ Turno non trovato!", ephemeral=True)
            return
        
        # Calcola durata turno
        end_time = time.time()
        total_duration = end_time - user_data["start_time"] - user_data["total_paused"]
        
        # Aggiorna leaderboard
        if self.user_id not in self.system.data["leaderboard"]:
            self.system.data["leaderboard"][self.user_id] = {"total_time": 0, "shifts_count": 0}
        
        self.system.data["leaderboard"][self.user_id]["total_time"] += total_duration
        self.system.data["leaderboard"][self.user_id]["shifts_count"] += 1
        
        # Rimuovi turno attivo
        del self.system.data["active_shifts"][self.user_id]
        self.system.save_data()
        
        # Crea embed riepilogo
        hours = total_duration / 3600
        embed = discord.Embed(
            title="⏹️ Turno Terminato",
            description=f"**Operatore:** {interaction.user.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="⏱️ Durata totale", value=f"{hours:.2f} ore", inline=True)
        embed.add_field(name="⏸️ Tempo in pausa", value=f"{user_data['total_paused']/3600:.2f} ore", inline=True)
        embed.add_field(name="📊 Turni effettivi", value=f"{user_data['total_paused']/3600:.2f} ore", inline=True)
        embed.add_field(name="🕐 Inizio", value=f"<t:{int(user_data['start_time'])}:T>", inline=True)
        embed.add_field(name="🕐 Fine", value=f"<t:{int(end_time)}:T>", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.followup.send("✅ Turno terminato con successo!", ephemeral=True)

class Shift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.system = ShiftSystem()

    @app_commands.command(name="shift", description="Gestisci il tuo turno di lavoro")
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
            
            # Inizia nuovo turno
            self.system.data["active_shifts"][user_id] = {
                "start_time": time.time(),
                "paused": False,
                "total_paused": 0,
                "pauses": []
            }
            self.system.save_data()
            
            # Crea embed e view
            embed = discord.Embed(
                title="🔄 Turno Iniziato",
                description=f"**Operatore:** {interaction.user.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="🕐 Ora inizio", value=f"<t:{int(time.time())}:T>", inline=True)
            embed.add_field(name="📊 Stato", value="🟢 Attivo", inline=True)
            embed.add_field(name="⏸️ Pause", value="0", inline=True)
            
            view = ShiftView(self.bot, user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        elif mode.value == "leaderboard":
            leaderboard = self.system.data.get("leaderboard", {})
            if not leaderboard:
                await interaction.response.send_message("📊 Nessun turno registrato ancora!", ephemeral=True)
                return
            
            sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1].get("total_time", 0), reverse=True)[:10]
            
            embed = discord.Embed(title="🏆 Classifica Turni", color=discord.Color.gold())
            for i, (user_id, data) in enumerate(sorted_lb, 1):
                user = self.bot.get_user(int(user_id))
                username = user.name if user else "Utente Sconosciuto"
                total_hours = data.get("total_time", 0) / 3600
                shifts_count = data.get("shifts_count", 0)
                
                embed.add_field(
                    name=f"{i}. {username}",
                    value=f"⏱️ {total_hours:.1f} ore ({shifts_count} turni)",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        else:
            await interaction.response.send_message("ℹ️ Usa `/shift inizia` per iniziare un turno!", ephemeral=True)

    @app_commands.command(name="shift_staff", description="Gestisci i turni staff (Admin)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(mode=[
        app_commands.Choice(name="lista", value="list"),
        app_commands.Choice(name="forza_fine", value="force_end")
    ])
    async def shift_staff(self, interaction: discord.Interaction, mode: app_commands.Choice[str], user: discord.Member = None):
        if mode.value == "list":
            active_shifts = self.system.data.get("active_shifts", {})
            if not active_shifts:
                await interaction.response.send_message("📊 Nessun turno attivo al momento!", ephemeral=True)
                return
            
            embed = discord.Embed(title="📋 Turni Attivi", color=discord.Color.blue())
            for user_id, shift_data in active_shifts.items():
                user_obj = self.bot.get_user(int(user_id))
                username = user_obj.name if user_obj else "Utente Sconosciuto"
                duration = (time.time() - shift_data["start_time"] - shift_data["total_paused"]) / 3600
                status = "⏸️ In pausa" if shift_data["paused"] else "🟢 Attivo"
                
                embed.add_field(
                    name=username,
                    value=f"{status} - {duration:.1f} ore",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif mode.value == "force_end" and user:
            user_id = str(user.id)
            if user_id in self.system.data["active_shifts"]:
                del self.system.data["active_shifts"][user_id]
                self.system.save_data()
                await interaction.response.send_message(f"✅ Turno di {user.mention} terminato forzatamente!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Questo utente non ha un turno attivo!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Shift(bot))
