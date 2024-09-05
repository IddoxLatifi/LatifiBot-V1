import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import app_commands
import asyncio
import random
import datetime
import logging
from typing import Optional
from datetime import timedelta
from dotenv import load_dotenv
import os

# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Dictionary zum Zwischenspeichern von Einladungslinks für verschiedene Server
invite_cache = {}

# Dictionary, um zu verfolgen, welche Benutzer bereits ein Ticket haben
user_tickets = {}
ticket_owners = {}

# Umgebungsvariablen lesen
TOKEN = os.getenv('TOKEN')
if TOKEN is None:
    raise ValueError("TOKEN ist nicht in der .env-Datei definiert oder leer")

STATUS_NAME = os.getenv('STATUS_NAME')
STATUS_GAME = os.getenv('STATUS_GAME')
STATUS_LISTENING = os.getenv('STATUS_LISTENING')
YT_STREAM_NAME = os.getenv('YT_STREAM_NAME')
YT_STREAM_URL = os.getenv('YT_STREAM_URL')
YT_STREAM_URL2 = os.getenv('YT_STREAM_URL2')
BANNER_URL = os.getenv('BANNER_URL')
FOOTER_URL = os.getenv('FOOTER_URL')
FOOTER_TEXT = os.getenv('FOOTER_TEXT')
THUMBNAIL_URL = os.getenv('THUMBNAIL_URL')
GUILD_ID = int(os.getenv('GUILD_ID'))
REACT_EMOJI = os.getenv('REACT_EMOJI')

# Spiele für die "Play"-Liste
PLAYLIST = {
    "tetris": os.getenv('PLAYLIST_TETRIS'),
    "pokemon": os.getenv('PLAYLIST_POKEMON'),
    "gta5": os.getenv('PLAYLIST_GTA5'),
    "rust": os.getenv('PLAYLIST_RUST'),
    "gta6": os.getenv('PLAYLIST_GTA6'),
    "minecraft": os.getenv('PLAYLIST_MINECRAFT'),
    "pc check": os.getenv('PLAYLIST_PC_CHECK'),
}

# Definiere den Support-Server und den Entwickler
SUPPORT_SERVER_INVITE = "https://discord.gg/latifimods"
DEVELOPER_NAME = "@apt_start_latifi"

# Definiere die Intents, die der Bot benötigt
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Lade die Erweiterungen (Cogs)
async def load_extensions():
    await bot.load_extension("emoji_reaction")

# Erstelle ein Bot-Objekt mit den definierten Intents
bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(seconds=30)
async def status_rotator():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("Guild nicht gefunden. Stelle sicher, dass die GUILD_ID korrekt ist.")
        return

    members = [member for member in guild.members if not member.bot]
    if members:
        member = random.choice(members)
        statuses = [
            discord.Game(name=f"{STATUS_NAME} | {member.display_name}"),
            discord.Streaming(name=f"{YT_STREAM_NAME} | {member.display_name}", url=YT_STREAM_URL),
            discord.Activity(type=discord.ActivityType.listening, name=f"{STATUS_LISTENING}"),
            discord.Activity(type=discord.ActivityType.playing, name=f"{STATUS_GAME}"),
        ]
        await bot.change_presence(activity=random.choice(statuses))
    else:
        await bot.change_presence(activity=discord.Game(name=STATUS_NAME))


# ANSI-Escape-Codes für Farben
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
PURPLE = "\033[35m"



# Event, das beim Start des Bots ausgelöst wird
@bot.event
async def on_ready():
    print(f'{GREEN}{bot.user} hat sich erfolgreich eingeloggt!{RESET}')
    print(f'{PURPLE}Entwickler: {DEVELOPER_NAME}{RESET}')
    print(f'{PURPLE}Für Unterstützung: {SUPPORT_SERVER_INVITE}{RESET}')
    print(f'{RED}Es werden keine .logs erstellt. Bitte beachten! Dieser Bot dient lediglich der Unterhaltung.{RESET}')
    print(f'{GREEN} Lange rede kurzer sinn, der Bot is Online! <3 {RESET}')
    await load_extensions()
    try:
        # Synchronisiere die Slash-Commands mit Discord
        synced = await bot.tree.sync()
        print(f"Slash-Commands synchronisiert: {len(synced)} Befehle")
    except Exception as e:
        print(f"Fehler beim Synchronisieren der Slash-Commands: {e}")


    # Lade die EmojiReaction Cog
    @bot.event
    async def on_ready():
        await bot.load_extension('emoji_reaction')

   # Starte den Status-Rotator
    status_rotator.start()


@bot.tree.command(name="info", description="Zeigt Informationen über einen Benutzer auf dem Server an")
@app_commands.describe(user="Der Benutzer, über den Informationen angezeigt werden sollen")
async def info_command(interaction: discord.Interaction, user: discord.User):
    member = interaction.guild.get_member(user.id)

    if member is None:
        await interaction.response.send_message("Benutzer nicht gefunden.")
        return

    # Generiere eine komplett zufällige IP-Adresse (IPv4)
    random_ip = f"{random.randint(79, 198)}.{random.randint(180, 220)}.{random.randint(0, 99)}.{random.randint(20, 120)}"

    embed = discord.Embed(title=f"Informationen über {member}", color=discord.Color.blue())
    embed.add_field(name="Benutzername", value=member.display_name, inline=True)
    embed.add_field(name="Benutzer-ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=str(member.status).capitalize(), inline=True)
    embed.add_field(name="Höchste Rolle", value=member.top_role.mention, inline=True)
    embed.add_field(name="Join-Date", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Account erstellt am", value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Bot", value="Ja" if member.bot else "Nein", inline=True)
    embed.add_field(name="IP-Adresse", value=random_ip, inline=True)

    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    else:
        embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")

    await interaction.response.send_message(embed=embed)

# Definiere den Befehl /commands
@bot.tree.command(name="commands", description="Zeigt eine Liste aller verfügbaren Befehle an")
async def commands_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Verfügbare Befehle",
        description="Hier ist eine Liste aller verfügbaren Befehle und ihre Beschreibungen:",
        color=discord.Color.purple()
    )

    commands_info = {

        "/commands": "Zeigt dir alle Commands",
        "/info": "Zeigt Informationen über einen Benutzer an.",
        "/gay": "Gibt einem Benutzer eine zufällige Einstufung von 0-100%.",
        "/play": "Lässt den Bot ein Spiel spielen.",
        "/send_embed": "Sendet eine benutzerdefinierte Embed-Nachricht.",
        "/clear_user": "Löscht alle Nachrichten eines Benutzers in jedem Kanal der Gilde.",
        "/giveaway": "Startet ein Giveaway im angegebenen Kanal.",
        "/ticket": "Erstellt ein Ticket. Es kann maximal 1 Ticket pro User genutzt werden!"
        "Auto-React on Messages"
    }

    for command, description in commands_info.items():
        embed.add_field(name=command, value=description, inline=False)

    embed.set_footer(text="Created by @apt_start_latifi💥", icon_url="https://cdn.discordapp.com/attachments/1269747286334902354/1280200923527778356/LM_Pfp_Nitro.gif?ex=66da8345&is=66d931c5&hm=b1c737380a66a65e813f30d88c752e8893c4b7eae23d2ca0ef83d70150f302ed&")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1269747286334902354/1280375295915855955/LatifiMods_Spacer.gif?ex=66da7cea&is=66d92b6a&hm=ea35a409c56514e86853c35f3236b8cee64d0e51b1e3af5b72a3bca16b67a047&")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="giveaway", description="Starte ein Giveaway")
@app_commands.describe(
    channel="Der Kanal, in dem das Giveaway stattfinden soll",
    prize="Der Preis des Giveaways",
    duration="Die Dauer des Giveaways (z.B. 1h, 30m)",
    winners="Die Anzahl der Gewinner"
)
async def start_giveaway(interaction: discord.Interaction, channel: discord.TextChannel, prize: str, duration: str,
                         winners: int):
    """Starte ein Giveaway im angegebenen Kanal."""

    # Berechne die Dauer in Sekunden
    time_units = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400
    }

    total_seconds = 0
    duration_parts = []
    for part in duration:
        if part.isdigit():
            duration_parts.append(part)
        else:
            unit = time_units.get(part.lower())
            if unit:
                total_seconds += int("".join(duration_parts)) * unit
                duration_parts = []

    end_time = datetime.datetime.now(datetime.timezone.utc) + timedelta(seconds=total_seconds)

    embed = discord.Embed(
        title="🎉 Giveaway! 🎉",
        description=f"**Preis:** {prize}\n**Endet:** <t:{int(end_time.timestamp())}:R>\n**Anzahl der Gewinner:** {winners}\n**Teilnehmer:** 0",
        color=discord.Color.purple()
    )
    embed.set_footer(text="Reagiere mit 🎉, um teilzunehmen!", icon_url=FOOTER_URL)
    embed.set_image(url=BANNER_URL)

    giveaway_message = await channel.send(embed=embed)
    await giveaway_message.add_reaction("🎉")

    await interaction.response.send_message(f"Giveaway gestartet in {channel.mention}!", ephemeral=True)

    await asyncio.sleep(total_seconds)

    # Beende das Giveaway und ermittele die Gewinner
    new_message = await channel.fetch_message(giveaway_message.id)
    users = [user async for user in new_message.reactions[0].users() if not user.bot]

    if len(users) == 0:
        await channel.send("Keiner hat am Giveaway teilgenommen. Kein Gewinner wurde ausgewählt.")
        return

    winners_list = random.sample(users, min(len(users), winners))
    winners_mentions = ", ".join([winner.mention for winner in winners_list])

    embed = discord.Embed(
        title="🎉 Giveaway Beendet! 🎉",
        description=f"**Preis:** {prize}\n**Gewinner:** {winners_mentions}\n**Details:** Herzlichen Glückwunsch! Du hast **{prize}** gewonnen!",
        color=discord.Color.green()
    )
    embed.set_footer(text="Herzlichen Glückwunsch an die Gewinner!", icon_url=FOOTER_URL)
    embed.set_image(url=BANNER_URL)

    await channel.send(embed=embed)

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    """Wird ausgelöst, wenn eine Reaktion hinzugefügt wird."""
    if user.bot:
        return

    if reaction.emoji == "🎉":
        # Holen der Nachricht, auf die reagiert wurde
        message = await reaction.message.channel.fetch_message(reaction.message.id)

        # Holen der Reaktionen von Benutzern
        users = [u async for u in reaction.users() if not u.bot]
        participant_count = len(users)

        # Falls das Embed vorhanden ist, aktualisiere die Teilnehmeranzahl
        if message.embeds:
            embed = message.embeds[0]

            # Teile die Beschreibung in Teile
            description_parts = embed.description.split("**Teilnehmer:**")
            if len(description_parts) > 1:
                # Aktualisiere den Teilnehmerbereich
                description_parts[1] = f"**Teilnehmer:** {participant_count}"
                new_description = description_parts[0] + description_parts[1]
                embed.description = new_description

                # Aktualisiere das Embed mit den neuen Teilnehmerinformationen
                await message.edit(embed=embed)

@bot.tree.command(name="clear_user", description="Löscht alle Nachrichten eines Benutzers in jedem Kanal der Gilde")
async def clear_user(interaction: discord.Interaction):
    """Löscht alle Nachrichten eines Benutzers in jedem Kanal der Gilde."""

    # Erstelle ein Embed zur Auswahl des Nutzers
    embed = discord.Embed(
        title="Wähle einen Benutzer aus, dessen Nachrichten gelöscht werden sollen",
        description="Bitte wähle den Benutzer aus, dessen Nachrichten gelöscht werden sollen:",
        color=discord.Color.purple()
    )

    # Erstelle eine Liste von Optionen (Benutzern) zum Auswählen
    options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in
               interaction.guild.members if not member.bot]

    # Füge eine Auswahlbox für Benutzer hinzu
    select = discord.ui.Select(placeholder="Wähle einen Benutzer...", options=options)

    # Event-Handler für die Auswahlbox
    async def select_callback(interaction: discord.Interaction):
        user_id = int(select.values[0])
        user = interaction.guild.get_member(user_id)

        if user:
            # Lösche alle Nachrichten des ausgewählten Nutzers in jedem Kanal
            for channel in interaction.guild.text_channels:
                async for message in channel.history(limit=100):
                    if message.author.id == user.id:
                        await message.delete()
            await interaction.response.send_message(f"Alle Nachrichten von {user.mention} wurden gelöscht.",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Benutzer nicht gefunden.", ephemeral=True)

    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)

    # Sende das Embed mit der Auswahlbox
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="gay", description="Gibt einem Benutzer eine zufällige Einstufung von 0-100%")
async def gay_command(interaction: discord.Interaction, user: Optional[discord.User] = None):
    # Falls kein Benutzer angegeben ist, verwende den Befehlsersteller
    if user is None:
        user = interaction.user

    # Zufällige Einstufung von 0 bis 100
    percentage = random.randint(0, 100)

    # Erstellen der eingebetteten Nachricht
    embed = discord.Embed(
        title="Gay Detector!",
        description=f"{user.mention} ist {percentage}% Gay! 🏳️‍🌈",
        color=discord.Color.purple()
    )

    # Banner oben hinzufügen
    embed.set_image(url=BANNER_URL)

    # Footer mit Bild hinzufügen
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_URL)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticket", description="Erstelle ein Ticket für dein Anliegen")
@app_commands.describe(anliegen="Beschreibe dein Anliegen")
async def ticket_command(interaction: discord.Interaction, anliegen: str):
    """Erstelle ein Ticket mit dem angegebenen Anliegen."""

    user = interaction.user
    guild = interaction.guild
    category = discord.utils.get(guild.categories,
                                 name="Tickets")  # Stelle sicher, dass es eine Kategorie namens "Tickets" gibt

    if not category:
        category = await guild.create_category("Tickets")  # Erstelle die Kategorie, falls sie nicht existiert

    # Überprüfen, ob der Benutzer bereits ein offenes Ticket hat
    existing_ticket = discord.utils.get(guild.text_channels, name=f"ticket-{user.name}")
    if existing_ticket:
        await interaction.response.send_message("Du hast bereits ein offenes Ticket. Bitte schließe es zuerst.",#Änderbar
                                                ephemeral=True)
        return

    # Berechtigungen für den neuen Kanal festlegen
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    # Erstellen des Ticket-Kanals
    ticket_channel = await guild.create_text_channel(f"ticket-{user.name}", category=category, overwrites=overwrites)

    # Nachricht im Ticket-Kanal
    embed = discord.Embed(
        title="Ticket erstellt",#Änderbar!
        description=f"{user.mention}, dein Ticket wurde erstellt. Bitte beschreibe dein Anliegen.",#Änderbar!
        color=discord.Color.purple()
    )                     #Änderbar!
    embed.add_field(name="Anliegen", value=anliegen)
    # Banner oben hinzufügen
    embed.set_image(url=BANNER_URL)

    # Footer mit Bild hinzufügen
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_URL)

    # Schaltfläche zum Schließen des Tickets
    close_button = Button(label="Schließen", style=discord.ButtonStyle.danger)
                                #Änderbar!
    async def close_ticket(interaction: discord.Interaction):
        if interaction.user == interaction.channel.guild.owner or interaction.user == user:
            await interaction.channel.send("Das Ticket wird in 5 Sekunden geschlossen.") ###Änderbar!
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("Nur der Ticket-Besitzer oder ein Admin kann das Ticket schließen.", ###Änderbar!
                                                    ephemeral=True)

    close_button.callback = close_ticket

    view = View()
    view.add_item(close_button)

    await ticket_channel.send(embed=embed, view=view)

    await interaction.response.send_message(f"{user.mention}Ticket erstellt in {ticket_channel.mention}!", ephemeral=True)

@bot.tree.command(name="embed", description="Sende eine benutzerdefinierte Embed-Nachricht")
@app_commands.describe(
    title="Der Titel des Embeds",
    description="Die Hauptnachricht des Embeds",
    color="Die Farbe des Embeds (Hex-Wert oder Farbname)",
    image="Die URL eines Bildes für das Embed",
    thumbnail="Die URL eines Thumbnails für das Embed",
    field_name="Name eines optionalen Feldes",
    field_value="Wert eines optionalen Feldes",
    field_inline="Ob das Feld inline angezeigt wird (true/false)",
    author_name="Der Name des Autors",
    author_icon="Die URL des Icons des Autors",
    author_url="Eine optionale URL für den Autor",
    timestamp="Ob die aktuelle Zeit als Timestamp hinzugefügt wird (true/false)"
)
async def send_embed(
    interaction: discord.Interaction,
    title: str = None,
    description: str = None,
    color: str = "purple",
    image: str = None,
    thumbnail: str = None,
    field_name: str = None,
    field_value: str = None,
    field_inline: bool = False,
    author_name: str = None,
    author_icon: str = None,
    author_url: str = None,
    timestamp: bool = False
):
    # Farbe des Embeds setzen
    try:
        embed_color = discord.Color(int(color.strip("#"), 16)) if color.startswith("#") else getattr(discord.Color, color.lower())()
    except AttributeError:
        embed_color = discord.Color.purple()  # Standardfarbe, falls die Farbe ungültig ist

    # Erstelle den Embed
    embed = discord.Embed(title=title, description=description, color=embed_color)

    # Setze Bild und Thumbnail, falls angegeben
    if image:
        embed.set_image(url=image)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    # Optionales Feld hinzufügen, falls angegeben
    if field_name and field_value:
        embed.add_field(name=field_name, value=field_value, inline=field_inline)

    # Footer aus Umgebungsvariablen verwenden
    if FOOTER_TEXT:
        if FOOTER_URL:
            embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_URL)
        else:
            embed.set_footer(text=FOOTER_TEXT)

    # Author setzen, falls angegeben
    if author_name:
        if author_icon:
            embed.set_author(name=author_name, icon_url=author_icon, url=author_url if author_url else discord.Embed.Empty)
        else:
            embed.set_author(name=author_name)

    # Timestamp hinzufügen, falls ausgewählt
    if timestamp:
        embed.timestamp = discord.utils.utcnow()

    # Sende den Embed
    await interaction.response.send_message(embed=embed)


# Starte den Bot mit dem geladenen Token
if __name__ == '__main__':
    bot.run(TOKEN)




    #####THIS BOT IS A OPEN SOURCE AND STILL UNDER MAINTANCE! ITS NOT SAVE TO USE THIS BOT ON A COMMUNITY-SERVER. PLEASE
    #####LEAS THE README. CREATET BY APT_START_LATIFI
    #####VIEL SPASS MIT DEM BOT UND SEINEN FUNKTIONEN!

