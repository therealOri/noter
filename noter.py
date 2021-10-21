import discord
from discord import Client, Intents
from discord_slash import SlashCommand
import sqlite3
import os
from dotenv import load_dotenv
import datetime
import colorama
from colorama import Fore

load_dotenv()
TOKEN = os.getenv("TOKEN")

noter = Client(intents=Intents.default())
slash = SlashCommand(noter, sync_commands=True)
botver = 'Noter v0.1'

guild_ids = [GUILD_ID_HERE] # This is so you don't have to wait an hour after startup to use the slash commands in your guild. In other guilds, you'll have to wait an hour.




@noter.event
async def on_ready():
    print(Fore.WHITE + "[" + Fore.GREEN + '+' + Fore.WHITE + "]" + Fore.GREEN + f" connection established and logged in as: {noter.user.name} with ID: {noter.user.id}")




@slash.slash(name='Help', description='Shows you all of the bots commands.', guild_ids=guild_ids)
async def help(ctx):
    
    helpembed = discord.Embed(title="Commands", description='A helpful menu for all the commands this bot can do! | Made by Ori#6338', colour=0x941db4, timestamp=datetime.datetime.utcnow())
    helpembed.set_thumbnail(url='https://cdn.discordapp.com/avatars/897025741412249620/dc92ef3c578cddeb9d7f1373f73d4e6c.png?size=80')
    helpembed.add_field(name="▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", value='\u200b', inline=False)
    helpembed.add_field(name="/ping", value = "Ping Pong. (Pings the bot)", inline=False)
    helpembed.add_field(name="/db make", value = "Makes the database for the notes and usernames and IDs.", inline=False)
    helpembed.add_field(name="/note add `userID` `username` `note`", value = "Adds a user, their ID and a note to the database.", inline=True)
    helpembed.add_field(name="/note rmv `userID`", value = "Remove users from database. Along with notes and data.", inline=True)
    helpembed.add_field(name="/note fetch `userID`", value = "Gets username, ID and note from database.", inline=True)
    helpembed.add_field(name="\u200b", value='▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬', inline=False)
    helpembed.set_footer(text=f"{botver} | code made by Ori#6338", icon_url='https://cdn.discordapp.com/attachments/850592305420697620/850595192641683476/orio.png')
    await ctx.send(embed=helpembed)


@slash.slash(name="Ping", description="Standard ping command to check latency.", guild_ids=guild_ids)
async def ping(ctx):
    pembed = discord.Embed(title="Pong!", description=f"My connection speed is {round(noter.latency * 1000)}ms", color=discord.Color.random(), timestamp=datetime.datetime.utcnow())
    pembed.set_footer(text=f"{botver} by Ori#6338", icon_url='https://cdn.discordapp.com/attachments/850592305420697620/850595192641683476/orio.png')
    await ctx.send('Ping Pong!', hidden=True)
    await ctx.send(embed=pembed)




# Makes the database for the notes and usernames and IDs.
@slash.subcommand(base='db', name='make', description='Command to make the database for user notes.', guild_ids=guild_ids)
async def make(ctx):
    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    c.execute(f'''CREATE TABLE user_notes (user_ids text, usernames text, notes text)''')
    database.commit()
    database.close()
    await ctx.send('Database has been created!', hidden=True)



# Adds a user and a note to the database.
@slash.subcommand(base='note', name='add', description='Adds a user id with a note to the database.', guild_ids=guild_ids)
async def add(ctx, user_id: str, user_name: str, note: str):
    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    c.execute(f"INSERT INTO user_notes VALUES ('{user_id}', '{user_name}', '{note}')")
    database.commit()
    database.close()
    await ctx.send('User and note successfully added!', hidden=True)




# Remove users from database. Along with notes.
@slash.subcommand(base='note', name='rmv', description='Removes a user and their note from the database.', guild_ids=guild_ids)
async def rmv(ctx, user_id: str):
    if not user_id.isdigit():
        embed = discord.Embed(title="**OOPS**", description="You must provide a user ID to add!", colour=0xe0cd00, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"{botver} by Ori#6338", icon_url='https://cdn.discordapp.com/attachments/850592305420697620/850595192641683476/orio.png')
        await ctx.send(embed=embed, delete_after=7)
    else:
        database = sqlite3.connect('user_notes.db')
        c = database.cursor()
        c.execute(f"DELETE FROM user_notes WHERE user_ids LIKE '{user_id}'")
        database.commit()
        database.close()
        await ctx.send('User and note successfully removed!', hidden=True)



# Get users and notes from database.
@slash.subcommand(base='note', name='fetch', description='Adds a user id with a note to the database.', guild_ids=guild_ids)
async def fetch(ctx, user_id: str):
    database = sqlite3.connect('user_notes.db')
    c = database.cursor()
    c.execute(f"SELECT user_ids FROM user_notes WHERE user_ids = {user_id}")
    user = c.fetchone()
    if not user:
        embed = discord.Embed(title="**❌ Error ❌**", description=f"No user with ID of `{user_id}` can be found in the database.", colour=0xff0000, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"{botver} by Ori#6338", icon_url='https://cdn.discordapp.com/attachments/850592305420697620/850595192641683476/orio.png')
        await ctx.send(embed=embed)
    else:
        # All of these will be changed depending on what you have set in your database using the "/db make" command.
        c.execute(f"SELECT user_ids FROM user_notes WHERE user_ids = {user_id}")
        u_id = c.fetchone()
        c.execute(f"SELECT usernames FROM user_notes WHERE user_ids = {user_id}")
        name = c.fetchone()
        c.execute(f"SELECT notes FROM user_notes WHERE user_ids = {user_id}")
        note = c.fetchone()
        c.close()
        embed = discord.Embed(title="__**User-Note Fetched!**__", colour=0x941db4, timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/897025741412249620/dc92ef3c578cddeb9d7f1373f73d4e6c.png?size=80')
        embed.add_field(name='User_id: ', value=f'`{u_id[0]}`', inline=True)
        embed.add_field(name='Username: ', value=f'`{name[0]}`', inline=True)
        embed.add_field(name='Note: ', value=f'`{note[0]}`', inline=False)
        embed.set_footer(text=f"{botver} by Ori#6338", icon_url='https://cdn.discordapp.com/attachments/850592305420697620/850595192641683476/orio.png')
        await ctx.send(embed=embed)




noter.run(TOKEN)