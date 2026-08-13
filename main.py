import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Bob Esponja está vivo!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

Thread(target=run).start()
import discord
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
