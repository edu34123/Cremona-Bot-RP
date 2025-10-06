import discord
from discord.ext import commands
from discord import app_commands

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_channel_id = 1386324500991315978  # ✅ CANALE CORRETTO
        self.role_id = 1386411670162640967  # Ruolo da taggare
        self.status_code = "vnn2aasc"

    @app_commands.command(name="statuson", description="Attiva lo status del server")
    @app_commands.default_permissions(administrator=True)
    async def statuson(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        channel = self.bot.get_channel(self.status_channel_id)
        
        if not channel:
            await interaction.response.send_message("❌ Canale status non trovato!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🟢 SERVER ATTIVO",
            description="Il server Cremona RP è ora **ATTIVO**!",
            color=discord.Color.green()
        )
        embed.add_field(name="📋 Codice", value=f"`{self.status_code}`", inline=False)
        embed.add_field(name="📊 Stato", value="🟢 Online", inline=True)
        embed.add_field(name="👥 Staff Attivi", value="In servizio", inline=True)
        embed.set_footer(text="Cremona RP • Status Server")
        embed.timestamp = discord.utils.utcnow()
        
        await channel.send(f"{role.mention if role else ''}", embed=embed)
        await interaction.response.send_message("✅ Status attivato nel canale corretto!", ephemeral=True)

    @app_commands.command(name="statusoff", description="Disattiva lo status del server")
    @app_commands.default_permissions(administrator=True)
    async def statusoff(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        channel = self.bot.get_channel(self.status_channel_id)
        
        if not channel:
            await interaction.response.send_message("❌ Canale status non trovato!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔴 SERVER DISATTIVATO",
            description="Il server Cremona RP è ora **DISATTIVATO**!",
            color=discord.Color.red()
        )
        embed.add_field(name="📋 Codice", value=f"`{self.status_code}`", inline=False)
        embed.add_field(name="📊 Stato", value="🔴 Offline", inline=True)
        embed.add_field(name="👥 Staff Attivi", value="Non in servizio", inline=True)
        embed.set_footer(text="Cremona RP • Status Server")
        embed.timestamp = discord.utils.utcnow()
        
        await channel.send(f"{role.mention if role else ''}", embed=embed)
        await interaction.response.send_message("✅ Status disattivato nel canale corretto!", ephemeral=True)

    @app_commands.command(name="statusinfo", description="Informazioni sullo status")
    async def statusinfo(self, interaction: discord.Interaction):
        """Mostra informazioni sul sistema di status"""
        embed = discord.Embed(
            title="📊 Sistema Status",
            description="Gestisci lo status del server Cremona RP",
            color=discord.Color.blue()
        )
        embed.add_field(name="Canale Status", value=f"<#{self.status_channel_id}>", inline=True)
        embed.add_field(name="Ruolo Notifiche", value=f"<@&{self.role_id}>", inline=True)
        embed.add_field(name="Codice Server", value=f"`{self.status_code}`", inline=True)
        embed.add_field(name="Comandi", value="`/statuson` - Attiva server\n`/statusoff` - Disattiva server", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Status(bot))
