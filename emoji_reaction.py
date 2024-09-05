import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Hole die Channel-IDs und Emojis aus der Umgebungsvariablen
CHANNEL_1_ID = int(os.getenv("CHANNEL_1_ID"))
EMOJI_1 = os.getenv("EMOJI_1")

CHANNEL_2_ID = int(os.getenv("CHANNEL_2_ID"))
EMOJI_2 = os.getenv("EMOJI_2")

CHANNEL_3_ID = int(os.getenv("CHANNEL_3_ID"))
EMOJI_3 = os.getenv("EMOJI_3")

CHANNEL_4_ID = int(os.getenv("CHANNEL_4_ID"))
EMOJI_4 = os.getenv("EMOJI_4")

CHANNEL_5_ID = int(os.getenv("CHANNEL_5_ID"))
EMOJI_5 = os.getenv("EMOJI_5")

# GUILD (serverweiter Emoji, der in allen Channels reagiert)
GUILD_EMOJI = os.getenv("GUILD_EMOJI")

class EmojiReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Reagiere nur auf Nachrichten, die nicht vom Bot selbst gesendet wurden
        if message.author == self.bot.user:
            return

        # Prüfe, ob die Nachricht in einem definierten Channel ist und reagiere mit dem entsprechenden Emoji
        if message.channel.id == CHANNEL_1_ID:
            await message.add_reaction(EMOJI_1)
        elif message.channel.id == CHANNEL_2_ID:
            await message.add_reaction(EMOJI_2)
        elif message.channel.id == CHANNEL_3_ID:
            await message.add_reaction(EMOJI_3)
        elif message.channel.id == CHANNEL_4_ID:
            await message.add_reaction(EMOJI_4)
        elif message.channel.id == CHANNEL_5_ID:
            await message.add_reaction(EMOJI_5)

        # GUILD Emoji: Reagiere in allen Channels dieses Servers mit dem serverweiten Emoji
        if GUILD_EMOJI:
            await message.add_reaction(GUILD_EMOJI)

# Füge den Cog dem Bot hinzu
async def setup(bot):
    await bot.add_cog(EmojiReaction(bot))