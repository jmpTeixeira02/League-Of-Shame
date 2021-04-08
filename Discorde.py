#encoding: utf-8

import os
import discord
import logging
import asyncio
from discord.ext import commands, tasks

import DB
import League

logging.basicConfig(level=logging.INFO)

Bot = commands.Bot(command_prefix = '$', case_insensitive=True)

Discord_Api = os.environ["Discord_Api"]

SOPAS = 152057225316270081
FELIX = 249609103737880576

@Bot.command(name='load_default')
async def load(ctx):
    League.loading()
    await ctx.send("Default users were added to shame!")

@Bot.command(name='add_shame', help='Adds a summoner to shame! ("Summoner_Name", Discord_ID, Server_ID)')
async def add(ctx, *arg):
    #summoner_name, discord_id, server_id
    if len(arg) < 3:
        await ctx.send("Wrong command. Use help to learn how to use it!")
        return False
    summoner_name = arg[0]
    discord_id = arg[1]
    server_id = arg[2]
    if (not DB.Insert_Into_Database(summoner_name, 0, discord_id, server_id)):
        message = "Summoner " + "'" + summoner_name + "'" + " is already in the database!"
        await ctx.send(message)
    else:

        message = "Summoner " + "'" + summoner_name + "'" + " has been associated with <@" + discord_id + ">"
        await ctx.send(message)

@Bot.command(name='remove_shame', help='Removes a summoner')
async def rem(ctx, summoner_name):
    if (summoner_name == ""):
        await ctx.send("Wrong command. Use help to learn how to use it!")
        return False
    if (DB.Remove_From_Database(summoner_name)):
        message = "Summoner " + "'" + summoner_name + "'" + " has been removed from the database!"
        await ctx.send(message)
    else:
        await ctx.send("User is not registered")

@Bot.command(name='registered_shame', help='Shows current summoners to shame')
async def update(ctx):
    Registered_Summoners = "\n\t\t"
    Summoners = DB.Summoner_Info()
    for x in range(len(Summoners)):
        Registered_Summoners += Summoners[x][0] + " <@" + str(Summoners[x][2]) + ">" + " on "
        if (Summoners[x][3] == SOPAS):
            Registered_Summoners += "SOPAS\n\t\t"
        elif (Summoners[x][3] == FELIX):
            Registered_Summoners += "FELIX\n\t\t"
        else:
            Registered_Summoners += "UNKNOWN\n\t\t"
    message = "The registered summoners are: " + Registered_Summoners
    await ctx.send(message)

@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Game("Looking for noobs!"))
    await verify.start()

async def sendburn(channel,msg,Summoners):
    if msg == "NOT":
        return
    print("Burn found with!")
    message = "<@" + str(Summoners[2]) + "> " + msg
    print(message)
    await channel.send(message)


@tasks.loop(minutes=3.5)
async def verify():
    Summoners = DB.Summoner_Info()
    print("Starting a new loop...")
    for x in range(len(Summoners)): 
        await asyncio.sleep(2)
        #Get the Channel ID
        channel = Bot.get_channel(set_channel(Summoners[x][3]))

        shame_game = League.Final(Summoners[x])
        await sendburn(channel,shame_game,Summoners[x])

        await asyncio.sleep(2)

        shame_rank = League.Get_rank(Summoners[x])
        await sendburn(channel,shame_rank,Summoners[x])
    print("Loop finished...")


def set_channel(Server_ID):
    if Server_ID == SOPAS:
        return 156753051720351744 # A-Team
    elif Server_ID == FELIX:
        return 770365512051720253 # League Faggits Felix
    else:
        return 585563121259905214 # Teste

Bot.run(Discord_Api)