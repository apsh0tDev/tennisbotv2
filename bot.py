#Discord imports and enviroment
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from schedule import get_schedule
from live import get_live_events

#Project imports
import constants

#----Init----
# all enviroment variables and init
load_dotenv()

# branch variable, each branch has a different token, change to "DEV" or "PROD"
current_branch = "DEV"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Dynamic token getter
def get_token():
    DISCORD_API = ''
    if current_branch == "DEV":
        DISCORD_API = os.getenv("TOKEN_DEV")
    elif current_branch == "PROD":
        DISCORD_API = os.getenv("TOKEN_PROD")
    return DISCORD_API

#----- Tasks and Bot Events -----
@bot.event
async def on_ready():
    print("Bot running")

#---- Commands -----
@bot.command()
async def commands(ctx):
   message = constants.commands_message
   await ctx.send(message)

@bot.command()
async def schedule(ctx):
    #Uses the get_schedule function caller.py
    #This gets all events from "matches" table that have a PreMatch status, this table fills with BetMGM Data
    response = await get_schedule()
    if response == None:
         await ctx.send("No events scheduled.")
    else:
        await ctx.send(embed=response)

@bot.command()
async def live(ctx):
    await ctx.send("Getting live...")
    response = await get_live_events()
    print(response)

#--- Start the bot ---
def startBot():
    bot.run(get_token())