import discord
from discord.ext import commands
from discord import app_commands

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_channel_id = 1386324752787832892  # Cambia con ID canale
        self.role_id = 1386585069161812099  # Cambia con ID ruolo
        self.status_code = "vnn2aasc"

    @app_commands.command(name="statuson", description="Attiva lo status del server")
    @app_commands.default_permissions(administrator=True)
    async def statuson(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        channel = self.bot.get_channel(self.status_channel_id)
        
        embed = discord.Embed(
            title="🟢 SERVER ATTIVO",
            description="Il server Cremona RP è ora **ATTIVO**!",
            color=discord.Color.green()
        )
        embed.add_field(name="📋 Codice", value=f"`{self.status_code}`", inline=False)
        embed.add_field(name="📊 Stato", value="🟢 Online", inline=True)
        embed.add_field(name="👥 Staff Attivi", value="In servizio", inline=True)
        
        if channel:
            await channel.send(f"{role.mention if role else ''}", embed=embed)
        
        await interaction.response.send_message("✅ Status attivato!", ephemeral=True)

    @app_commands.command(name="statusoff", description="Disattiva lo status del server")
    @app_commands.default_permissions(administrator=True)
    async def statusoff(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        channel = self.bot.get_channel(self.status_channel_id)
        
        embed = discord.Embed(
            title="🔴 SERVER DISATTIVATO",
            description="Il server Cremona RP è ora **DISATTIVATO**!",
            color=discord.Color.red()
        )
        embed.add_field(name="📋 Codice", value=f"`{self.status_code}`", inline=False)
        embed.add_field(name="📊 Stato", value="🔴 Offline", inline=True)
        embed.add_field(name="👥 Staff Attivi", value="Non in servizio", inline=True)
        
        if channel:
            await channel.send(f"{role.mention if role else ''}", embed=embed)
        
        await interaction.response.send_message("✅ Status disattivato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Status(bot))
