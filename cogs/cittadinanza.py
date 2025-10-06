import discord
from discord.ext import commands
from discord import app_commands

class CittadinanzaModal(discord.ui.Modal, title="Richiesta Cittadinanza"):
    nome = discord.ui.TextInput(label="Nome (RP)", placeholder="Inserisci il tuo nome", required=True)
    cognome = discord.ui.TextInput(label="Cognome (RP)", placeholder="Inserisci il tuo cognome", required=True)
    eta = discord.ui.TextInput(label="Età (RP)", placeholder="Inserisci la tua età", required=True)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Cambia nickname mantenendo [test] se presente
        current_nick = interaction.user.display_name
        if current_nick.startswith("[test]"):
            new_nick = f"[test] {self.nome} {self.cognome}"
        else:
            new_nick = f"{self.nome} {self.cognome}"
        
        try:
            await interaction.user.edit(nick=new_nick)
        except:
            pass  # Non ha permessi per cambiare nickname
        
        embed = discord.Embed(
            title="🪪 Richiesta Cittadinanza",
            description=f"**Richiedente:** {interaction.user.mention}\n**Nome:** {self.nome}\n**Cognome:** {self.cognome}\n**Età:** {self.eta}",
            color=discord.Color.blue()
        )
        
        channel = self.bot.get_channel(1386328375806660609)  # Cambia con ID canale cittadinanza
        if channel:
            await channel.send(embed=embed, view=AccettaCittadinanzaView())
        
        await interaction.response.send_message("✅ Richiesta inviata allo staff!", ephemeral=True)

class CittadinanzaView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="🪪 Richiedi Cittadinanza", style=discord.ButtonStyle.blurple, custom_id="cittadinanza_req")
    async def richiedi_cittadinanza(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CittadinanzaModal())

class AccettaCittadinanzaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Accetta", style=discord.ButtonStyle.green, custom_id="accetta_citt")
    async def accetta_cittadinanza(self, interaction: discord.Interaction, button: discord.ui.Button):
        ruolo_cittadino = interaction.guild.get_role(1386411670162640967)  # Cambia con ID ruolo cittadino
        if ruolo_cittadino:
            # Trova l'utente dall'embed
            embed = interaction.message.embeds[0]
            user_mention = embed.description.split("**Richiedente:** ")[1].split("\n")[0]
            user_id = int(user_mention.replace("<@", "").replace(">", ""))
            
            member = interaction.guild.get_member(user_id)
            if member:
                await member.add_roles(ruolo_cittadino)
                await interaction.response.send_message(f"✅ Cittadinanza concessa a {member.mention}!")
            else:
                await interaction.response.send_message("❌ Utente non trovato!")
        else:
            await interaction.response.send_message("❌ Ruolo cittadino non trovato!")

class Cittadinanza(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_cittadinanza", description="Setup sistema cittadinanza")
    @app_commands.default_permissions(administrator=True)
    async def setup_cittadinanza(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🪪 Cittadinanza Cremona RP",
            description="Clicca il pulsante qui sotto per richiedere la cittadinanza.\nDovrai inserire nome, cognome e età del tuo personaggio.",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=CittadinanzaView(self.bot))

async def setup(bot):
    await bot.add_cog(Cittadinanza(bot))
