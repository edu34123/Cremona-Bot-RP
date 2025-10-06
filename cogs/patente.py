import discord
from discord.ext import commands
from discord import app_commands

class PatenteModal(discord.ui.Modal, title="Richiesta Patente"):
    eta_rp = discord.ui.TextInput(label="Età (RP)", placeholder="Quanti anni ha il tuo personaggio?", required=True)
    esperienza_guida = discord.ui.TextInput(
        label="Esperienza di guida", 
        placeholder="Hai esperienza di guida?",
        style=discord.TextStyle.paragraph,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            eta = int(self.eta_rp.value)
            if eta < 18:
                await interaction.response.send_message("❌ Devi avere almeno 18 anni per la patente!", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ Inserisci un'età valida!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🚗 Richiesta Patente",
            description=f"**Richiedente:** {interaction.user.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="Età (RP)", value=self.eta_rp, inline=True)
        embed.add_field(name="Esperienza Guida", value=self.esperienza_guida, inline=False)
        
        channel = self.bot.get_channel(1386328375806660609)  # Cambia con ID canale
        if channel:
            await channel.send(embed=embed, view=AccettaPatenteView())
        
        await interaction.response.send_message("✅ Richiesta patente inviata!", ephemeral=True)

class PatenteView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="🚗 Richiedi Patente", style=discord.ButtonStyle.blurple, custom_id="patente_req")
    async def richiedi_patente(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PatenteModal())

class AccettaPatenteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Approva", style=discord.ButtonStyle.green, custom_id="approva_patente")
    async def approva_patente(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        user_mention = embed.description.split("**Richiedente:** ")[1].split("\n")[0]
        user_id = int(user_mention.replace("<@", "").replace(">", ""))
        
        member = interaction.guild.get_member(user_id)
        if member:
            ruolo_patente = interaction.guild.get_role(1386667617896366121)  # Cambia con ID ruolo patente
            if ruolo_patente:
                await member.add_roles(ruolo_patente)
                await interaction.response.send_message(f"✅ Patente approvata per {member.mention}!")
            else:
                await interaction.response.send_message("❌ Ruolo patente non trovato!")
        else:
            await interaction.response.send_message("❌ Utente non trovato!")

class Patente(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_patente", description="Setup sistema patente")
    @app_commands.default_permissions(administrator=True)
    async def setup_patente(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚗 Patente di Guida",
            description="Richiedi qui la patente di guida per il tuo personaggio.",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, view=PatenteView(self.bot))

async def setup(bot):
    await bot.add_cog(Patente(bot))
