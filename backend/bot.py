import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
import os 

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1396862969085694032

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Respondendo perguntas"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.channel.id == CHANNEL_ID and bot.user.mentioned_in(message):
        response = requests.post("http://localhost:8000/ask", json={"query": message.content})
        await message.reply(response.json().get("response"), mention_author=True)

if __name__ == '__main__':
    bot.run(TOKEN)
