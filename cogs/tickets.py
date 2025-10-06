import discord
from discord.ext import commands
from discord import app_commands

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎫 Crea Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Crea canale ticket privato
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        category = discord.utils.get(interaction.guild.categories, name="TICKETS")
        if not category:
            category = await interaction.guild.create_category("TICKETS")
        
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        embed = discord.Embed(
            title="🎫 Ticket di Supporto",
            description=f"Grazie {interaction.user.mention}! Lo staff ti aiuterà a breve.\nDescrivi il tuo problema qui sotto.",
            color=discord.Color.blue()
        )
        
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket creato: {channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_channel_id = 1386328375806660609  # Cambia con ID canale tickets

    @app_commands.command(name="setup_ticket", description="Setup sistema ticket")
    @app_commands.default_permissions(administrator=True)
    async def setup_ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Supporto Cremona RP",
            description="Clicca il pulsante qui sotto per creare un ticket di supporto con lo staff.",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(Ticket(bot))
