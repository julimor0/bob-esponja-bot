08.12 4:26 p. m.
Main.py
import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bob Esponja conectado como {bot.user}")

@bot.command()
async def hola(ctx):
    await ctx.send("¡Estoy listo! ")

TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
