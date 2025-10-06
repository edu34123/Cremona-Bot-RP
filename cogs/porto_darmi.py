import discord
from discord.ext import commands
from discord import app_commands

class PortoArmiModal(discord.ui.Modal, title="Richiesta Porto d'Armi"):
    motivazione = discord.ui.TextInput(
        label="Motivazione", 
        placeholder="Perché hai bisogno del porto d'armi?",
        style=discord.TextStyle.paragraph,
        required=True
    )
    esperienza = discord.ui.TextInput(
        label="Esperienza con le armi",
        placeholder="Hai esperienza precedente?",
        style=discord.TextStyle.paragraph,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔫 Richiesta Porto d'Armi",
            description=f"**Richiedente:** {interaction.user.mention}",
            color=discord.Color.orange()
        )
        embed.add_field(name="Motivazione", value=self.motivazione, inline=False)
        embed.add_field(name="Esperienza", value=self.esperienza, inline=False)
        
        channel = self.bot.get_channel(1386328375806660609)  # Cambia con ID canale
        if channel:
            await channel.send(embed=embed, view=AccettaPortoArmiView())
        
        await interaction.response.send_message("✅ Richiesta porto d'armi inviata!", ephemeral=True)

class PortoArmiView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="🔫 Richiedi Porto d'Armi", style=discord.ButtonStyle.blurple, custom_id="porto_armi_req")
    async def richiedi_porto_armi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PortoArmiModal())

class AccettaPortoArmiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Approva", style=discord.ButtonStyle.green, custom_id="approva_porto")
    async def approva_porto(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        user_mention = embed.description.split("**Richiedente:** ")[1].split("\n")[0]
        user_id = int(user_mention.replace("<@", "").replace(">", ""))
        
        member = interaction.guild.get_member(user_id)
        if member:
            ruolo_porto = interaction.guild.get_role(1389994482430119957)  # Cambia con ID ruolo porto armi
            if ruolo_porto:
                await member.add_roles(ruolo_porto)
                await interaction.response.send_message(f"✅ Porto d'armi approvato per {member.mention}!")
            else:
                await interaction.response.send_message("❌ Ruolo porto d'armi non trovato!")
        else:
            await interaction.response.send_message("❌ Utente non trovato!")

class PortoArmi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_porto_armi", description="Setup sistema porto d'armi")
    @app_commands.default_permissions(administrator=True)
    async def setup_porto_armi(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔫 Porto d'Armi Cremona RP",
            description="Richiedi qui il porto d'armi per il tuo personaggio.",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed, view=PortoArmiView(self.bot))

async def setup(bot):
    await bot.add_cog(PortoArmi(bot))
