####################################################################
#                                                                  #
#    Credit: therealOri  |  https://github.com/therealOri          #
#                                                                  #
####################################################################

####################################################################################
#                                                                                  #
#                            Imports & definitions                                 #
#                                                                                  #
####################################################################################
import asyncio
import discord
import os
import datetime
from libs import rnd
import tomllib
import time
import logging
import sqlite3
import subprocess
from beaupy.spinners import *




#Load our config for main
with open('config.toml', 'rb') as fileObj:
    config = tomllib.load(fileObj) #dictionary/json




__authors__ = '@therealOri'
token = config["TOKEN"]
bot_logo = config["bot_logo"]
author_logo = None
staff_role_id = config["staff_role_id"]


hex_red=0xFF0000
hex_green=0x0AC700
hex_yellow=0xFFF000 # I also like -> 0xf4c50b

# +++++++++++ Imports and definitions +++++++++++ #














####################################################################################
#                                                                                  #
#                             Normal Functions                                     #
#                                                                                  #
####################################################################################
def clear():
    os.system("clear||cls")



def random_hex_color():
    hex_digits = '0123456789abcdef'
    hex_digits = rnd.shuffle(hex_digits)
    color_code = ''
    nums = rnd.randint(0, len(hex_digits)-1, 6)
    for _ in nums:
        color_code += hex_digits[_]
    value =  int(f'0x{color_code}', 16)
    return value



def create_table(db_conn, table_name):
    c = db_conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            "row"	INTEGER,
            "user_id"	TEXT,
            "user_name"	TEXT,
            "note"	TEXT,
            PRIMARY KEY("row")
        );
    """)
    db_conn.commit()
# +++++++++++ Normal Functions +++++++++++ #













####################################################################################
#                                                                                  #
#                   Async Functions, buttons, modals, etc.                         #
#                                                                                  #
####################################################################################
async def status():
    while True:
        status_messages = ['my internals', '/help for help', 'your navigation history', 'myself walking on the grass', 'Global Global Global', 'base all your 64', 'your security camera footage', 'myself walking on the moon', 'your browser search history']
        smsg = rnd.choice(status_messages)
        activity = discord.Streaming(type=1, url='https://www.youtube.com/watch?v=4xDzrJKXOOY', name=smsg)
        await ntr.change_presence(status=discord.Status.online, activity=activity)
        await asyncio.sleep(60) #Seconds





class NoteUpdateModal(discord.ui.Modal):
    def __init__(self, user_id: str, current_note: str) -> None:
        super().__init__(title=f"Update Note for User {user_id}")
        self.user_id = user_id
        self.current_note = current_note

        self.add_item(discord.ui.InputText(label="Current Note", value=current_note, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="New Note", style=discord.InputTextStyle.long))

    # for some reason we NEED to use discord.Interaction here instead.
    async def callback(self, interaction: discord.Interaction) -> None:
        database = sqlite3.connect('user_notes.db')
        c = database.cursor()

        guild_id = interaction.guild.id
        table_name = f"guild_{guild_id}"

        new_note = self.children[1].value #index 1 is the 2nd input box

        c.execute(f"UPDATE {table_name} SET note = ? WHERE user_id = ?", (new_note, self.user_id))
        database.commit()
        database.close()

        await interaction.response.send_message(f"Note updated for user with ID `{self.user_id}`!", ephemeral=True, delete_after=25)






class dl_button(discord.ui.View):
    @discord.ui.button(label="Download!", style=discord.ButtonStyle.green, emoji="⬇️")
    async def button_callback(self, button, interaction):
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "user_db_notes.7z")
        d_file = discord.File(file_path)
        await interaction.response.send_message("Here is your notes archive! - Expires in 1min", file=d_file, delete_after=60)

# +++++++++++ Async Functions, buttons, modals, etc. +++++++++++ #












####################################################################################
#                                                                                  #
#                                Client Setup                                      #
#                                                                                  #
####################################################################################
intents = discord.Intents.default()
ntr = discord.Bot(intents=intents)

# +++++++++++ Client Setup +++++++++++ #










####################################################################################
#                                                                                  #
#                                   Events                                         #
#                                                                                  #
####################################################################################
startup_spinner = Spinner(ARC, "Starting up....")
startup_spinner.start()
@ntr.event
async def on_ready():
    global author_logo
    me = await ntr.fetch_user(254148960510279683)
    author_logo = me.avatar
    ntr.loop.create_task(status())

    startup_spinner.stop()
    clear()
    print(f'Logged in as {ntr.user} (ID: {ntr.user.id})')
    print('------')

# +++++++++++ Events +++++++++++ #













####################################################################################
#                                                                                  #
#                             Regular Commands                                     #
#                                                                                  #
####################################################################################
@ntr.slash_command(name='help', description='Shows you what commands you can use.')
async def help(ctx: discord.ApplicationContext):
    rnd_hex = random_hex_color()
    embed = discord.Embed(title='Commands  |  Help\n-=-=-=-=-=-=-=-=-=-=-=-=-=-', colour=rnd_hex, timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=bot_logo)
    embed.add_field(name='\u200B\n/notes add <user_id> <note>', value="Makes a note for a specified user.", inline=True)
    embed.add_field(name='\u200B\n/notes delete <user_id>', value="Removes a note made for a user.", inline=True)
    embed.add_field(name='\u200B\n/notes update <user_id>', value="Updates a note for the specified user.", inline=True)
    embed.add_field(name='\u200B\n/notes fetch <user_id>', value="Fetches a note made for a specified user and some extra info.", inline=True)
    embed.add_field(name='\u200B\n/notes fetch_all (password)', value="Packages up and allows you to download a 7zip archive of all of the notes for the server.", inline=False)
    embed.add_field(name="\u200B\n", value="\u200B\n-=-=-=-=-=-=-=-=-=-=-=-=-=-", inline=False)
    embed.set_footer(text=__authors__, icon_url=author_logo)
    await ctx.send_response(embed=embed, ephemeral=True)




@ntr.slash_command(name='ping', description='Test to see if the bot is responsive.')
async def ping(ctx: discord.ApplicationContext):
    await ctx.send_response(f"⏱️ Pong! ⏱️\nConnection speed is {round(ntr.latency * 1000)}ms", ephemeral=True)





# Note commands
notes = ntr.create_group("notes", "Note commands for managing notes!")
@notes.command(name='add', description='Adds a note about a user.')
async def add(ctx: discord.ApplicationContext, user_id: str, note: str):
    role = ctx.guild.get_role(staff_role_id)
    if not role in ctx.user.roles:
        await ctx.send_response("You don't have permission to use this command.", ephemeral=True, delete_after=10)
    else:
        database = sqlite3.connect('user_notes.db')
        c = database.cursor()
        guild_id = ctx.guild.id
        table_name = f"guild_{guild_id}"


        create_table(database, table_name)  # will create a new table with the guild ID if it doesn't exist already.
        c.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", (user_id,))
        existing_row = c.fetchone()

        if existing_row:
            await ctx.send_response(f"A note for the user with ID: `{user_id}` already exists in the database. Please use `/notes update` instead.", ephemeral=True, delete_after=10)
            database.close()
            return

        user = await ntr.fetch_user(int(user_id))
        user_name = f"@{user.name}"

        # User ID doesn't exist, so insert a new row
        row = [user_id, user_name, note]
        c.execute(f"INSERT INTO {table_name} (user_id, user_name, note) VALUES (?, ?, ?)", row)
        database.commit()
        await ctx.send_response(f"Note added for: {user_name}!", ephemeral=True, delete_after=10)
        database.close()











@notes.command(name='delete', description="Deletes a user note.")
async def delete(ctx: discord.ApplicationContext, user_id: str):
    role = ctx.guild.get_role(staff_role_id)
    if not role in ctx.user.roles:
        await ctx.send_response("You don't have permission to use this command.", ephemeral=True, delete_after=10)
    else:
        database = sqlite3.connect('user_notes.db')
        c = database.cursor()
        guild_id = ctx.guild.id
        table_name = f"guild_{guild_id}"

        create_table(database, table_name)
        c.execute(f"SELECT note FROM {table_name} WHERE user_id = ?", (user_id,))
        existing_row = c.fetchone()

        if existing_row:
            c.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user_id,))
            database.commit()
            await ctx.send_response(f"Deleted note for user with ID: `{user_id}`.", ephemeral=True, delete_after=10)
        else:
            await ctx.send_response(f"No note found for the user with ID {user_id}.", ephemeral=True, delete_after=10)
        database.close()





@notes.command(name='update_note', description="Updates a user's note")
async def update_note(ctx: discord.ApplicationContext, user_id: str):
    role = ctx.guild.get_role(staff_role_id)
    if not role in ctx.user.roles:
        await ctx.send_response("You don't have permission to use this command.", ephemeral=True, delete_after=10)
    else:
        database = sqlite3.connect('user_notes.db')
        c = database.cursor()
        guild_id = ctx.guild.id
        table_name = f"guild_{guild_id}"

        create_table(database, table_name)
        c.execute(f"SELECT note FROM {table_name} WHERE user_id = ?", (user_id,))
        existing_row = c.fetchone()

        if existing_row:
            current_note = existing_row[0]
            modal = NoteUpdateModal(user_id, current_note)
            await ctx.send_modal(modal)
        else:
            await ctx.send_response(f"No note found for the user with ID {user_id}.", ephemeral=True)
        database.close()





@notes.command(name='fetch', description="Fetches a note about a given user.")
async def fetch(ctx: discord.ApplicationContext, user_id: str):
    role = ctx.guild.get_role(staff_role_id)
    if not role in ctx.user.roles:
        await ctx.send_response("You don't have permission to use this command.", ephemeral=True, delete_after=10)
    else:
        database = sqlite3.connect('user_notes.db')
        c = database.cursor()
        guild_id = ctx.guild.id
        table_name = f"guild_{guild_id}"

        create_table(database, table_name)
        c.execute(f"SELECT note FROM {table_name} WHERE user_id = ?", (user_id,))
        existing_row = c.fetchone()

        if existing_row:
            current_note = existing_row[0]
            member = ctx.guild.get_member(int(user_id))
            role_names = [f'<@&{role.id}>' if not role.name.startswith('@') else role.name for role in member.roles]
            rnd_hex = random_hex_color()
            note_embed = discord.Embed(title='User Fetched!', description=f'Note for @{member.name}', colour=rnd_hex, timestamp=datetime.datetime.now(datetime.timezone.utc))
            note_embed.set_thumbnail(url=member.avatar) # default_avatar can also be used.
            note_embed.add_field(name='\u200B\nID', value=f"{member.id}", inline=True)
            note_embed.add_field(name='\u200B\nGlobal Name', value=f"{member.global_name}", inline=True)
            note_embed.add_field(name="\u200B\nJoined the server", value=f"{member.joined_at.strftime('%Y-%m-%d | %I:%M%p')}", inline=True)
            note_embed.add_field(name='\u200B\nRoles', value=f"{role_names}", inline=True)
            note_embed.add_field(name='\u200B\nNickname', value=f"{member.nick}", inline=True)
            note_embed.add_field(name='\u200B\nURL', value=f"{member.jump_url}", inline=True)
            note_embed.add_field(name='Note', value=f"{current_note}\u200B\n", inline=False)
            note_embed.set_footer(text=__authors__, icon_url=author_logo)
            await ctx.send_response(embed=note_embed, ephemeral=True)
        else:
            await ctx.send_response(f"No note found for the user with ID `{user_id}`.", ephemeral=True, delete_after=10)
        database.close()






@notes.command(name='fetch_all', description='Fetches all user notes.')
async def fetch_all(ctx: discord.ApplicationContext, password: str = None):
    role = ctx.guild.get_role(staff_role_id)
    if not role in ctx.user.roles:
        await ctx.send_response("You don't have permission to use this command.", ephemeral=True, delete_after=10)
    else:
        database = sqlite3.connect('user_notes.db')
        c = database.cursor()
        guild_id = ctx.guild.id
        table_name = f"guild_{guild_id}"


        create_table(database, table_name)
        c.execute(f"SELECT * FROM {table_name}")
        rows = c.fetchall()
        database.close()

        if rows:
            items = [str(row) for row in rows]
            with open('output.txt', 'w') as f:
                f.write('\n'.join(items))

            if not password:
                subprocess.check_call(['7z', 'a', 'user_db_notes.7z', 'output.txt'], stdout=subprocess.DEVNULL)
            else:
                subprocess.check_call(['7z', 'a', '-p' + password, 'user_db_notes.7z', 'output.txt'], stdout=subprocess.DEVNULL)

            os.remove("output.txt")
            await ctx.send_response("DB logs here - Expires in 1min", view=dl_button(), delete_after=60)
        else:
            await ctx.send_response("Database is empty - No notes available to fetch.", ephemeral=True, delete_after=10)

# +++++++++++ Regular Commands +++++++++++ #


















if __name__ == '__main__':
    clear()
    ntr.run(token, reconnect=True)
