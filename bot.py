import discord
from discord.ext import commands
import sqlite3
from config import settings, morg
import random as rn

client = commands.Bot( command_prefix = settings['PPREFIX'], help_command=None)
connection = sqlite3.connect('tasks_server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
    print( 'Bot connected' )
    cursor.execute('CREATE TABLE IF NOT EXISTS tasks( Id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'id_serv INT,'
                   'roles INT,'
                   'contents TEXT,'
                   'task TEXT);')
    connection.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS sosud('
                   'id_serv INT,'
                   'channel INT,'
                   'contents TEXT);')
    connection.commit()
    print( 'Connect database' )

@client.command( pass_context = True )
async def task(ctx, roles: discord.Role = None):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['task']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['task']}';").fetchone()[0]:
            if cursor.execute(f"SELECT * FROM tasks WHERE id_serv = {ctx.guild.id};").fetchone() is None:
                await ctx.send(f"**{ctx.author.mention}**, at the moment, no tasks")
            else:
                if roles is None:
                    tasks = cursor.execute(f"SELECT roles, contents, task FROM tasks WHERE id_serv = {ctx.guild.id};").fetchall()
                    rand_int = rn.randint(0, len(tasks)-1)
                    await  ctx.author.send(f"""This task is intended for the {ctx.guild.get_role(tasks[rand_int][0])} roles.
                                                        Task name: {tasks[rand_int][1]}
                                                        You must do everything that is indicated below:
                                                        {tasks[rand_int][2]}""")
                else:
                    if cursor.execute(f"SELECT * FROM tasks WHERE roles = {roles.id} AND id_serv = {ctx.guild.id};").fetchone() is None:
                        await ctx.send(f"**{ctx.author.mention}**, at the moment, no tasks")
                    else:
                        tasks = cursor.execute(f"SELECT roles, contents, task FROM tasks WHERE roles = {roles.id} AND id_serv = {ctx.guild.id};").fetchall()
                        rand_int = rn.randint(0, len(tasks)-1)
                        await  ctx.author.send(f"""This task is intended for the {ctx.guild.get_role(tasks[rand_int][0])} roles.
                                    Task name: {tasks[rand_int][1]}
                                    You must do everything that is indicated below:
                                    {tasks[rand_int][2]}""")
    else:
        await ctx.send(f"**{ctx.author.mention}**, the settings are not defined by the administrator, you cannot use these commands")


@client.command( pass_context = True )
async def add(ctx, roles: discord.Role = None, contents:str = None, *taskt: str):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone()[0]:
            if roles is None:
                await ctx.send(f"**{ctx.author.mention}**, specify the role for which the task is intended")
            else:
                if contents is None:
                    await ctx.send(f"**{ctx.author.mention}**, write the name of the task")
                else:
                    tasker = ""
                    for tk in taskt:
                        tasker += tk + ' '
                    if tasker == "":
                        await ctx.send(f"**{ctx.author.mention}**, write a task")
                    else:
                        task_in = (ctx.guild.id, roles.id, contents, tasker)

                        cursor.execute("INSERT INTO tasks(id_serv, roles, contents, task) VALUES(?, ?, ?, ?);", task_in)
                        connection.commit()
                        await ctx.send(f'the {contents} task for the {roles.mention} role was recorded')
    else:
        await ctx.send(f"**{ctx.author.mention}**, the settings are not defined by the administrator, you cannot use these commands")


@client.command( pass_context = True )
async def remove_one_task(ctx, roles_or_task: str = None):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone()[0]:
            if roles_or_task is None:
                await ctx.send(f"**{ctx.author}**, the role to delete all tasks of this role")
            else:
                mrg = roles_or_task
                cursor.execute(f"DELETE FROM tasks WHERE contents = '{mrg}' AND id_serv = {ctx.guild.id};")
                connection.commit()
                await ctx.send(f"the task with the name {roles_or_task} was deleted")
    else:
        await ctx.send(f"**{ctx.author.mention}**, the settings are not defined by the administrator, you cannot use these commands")

@client.command( pass_context = True )
async def remove_role_tasks(ctx, roles_or_task: discord.Role = None):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone()[0]:
            if roles_or_task is None:
                await ctx.send(f"**{ctx.author}**, the role to delete all tasks of this role")
            else:
                mrg = roles_or_task.id
                cursor.execute(f"DELETE FROM tasks WHERE roles = {mrg} AND id_serv = {ctx.guild.id};")
                connection.commit()
                await ctx.send(f"the tasks for the {roles_or_task.mention} roles have been deleted")
    else:
        await ctx.send(f"**{ctx.author.mention}**, the settings are not defined by the administrator, you cannot use these commands")

@client.command( pass_context = True )
async def status(ctx):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone()[0]:

            embed = discord.Embed(title='Tasks for role')
            if cursor.execute(f"SELECT * FROM tasks WHERE id_serv = {ctx.guild.id};").fetchone() is None:
                embed.add_field(
                    name=f"NONE",
                    value=f"sorry, didn't find it",
                    inline=False
                )
            else:
                for row in cursor.execute(
                        f"SELECT roles, contents, task FROM tasks WHERE id_serv = {ctx.guild.id};"):
                    if ctx.guild.get_role(row[0]) != None:
                        embed.add_field(
                            name=f"Contets: {row[1]}\nFor role: {ctx.guild.get_role(row[0])}",
                            value=f"Task: {row[2]}",
                            inline=False
                        )
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"**{ctx.author.mention}**, the settings are not defined by the administrator, you cannot use these commands")

@client.command( pass_context = True )
async def status_role(ctx, roles_or_task: discord.Role = None):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone()[0]:

            embed = discord.Embed(title='Tasks for role')
            if cursor.execute(f"SELECT * FROM tasks WHERE id_serv = {ctx.guild.id};").fetchone() is None:
                embed.add_field(
                    name=f"NONE",
                    value=f"sorry, didn't find it",
                    inline=False
                )

            if roles_or_task is None:
                for row in cursor.execute(f"SELECT roles, contents, task FROM tasks WHERE id_serv = {ctx.guild.id};"):
                    if ctx.guild.get_role(row[0]) != None:
                        embed.add_field(
                            name=f"Contets: {row[1]}\nFor role: {ctx.guild.get_role(row[0])}",
                            value=f"Task: {row[2]}",
                            inline=False
                        )
            else:
                mrg = roles_or_task.id
                if cursor.execute(f"SELECT * FROM tasks WHERE roles = {mrg} AND id_serv = {ctx.guild.id};").fetchall() == []:
                    embed.add_field(
                        name=f"NONE",
                        value=f"sorry, didn't find it",
                        inline=False
                    )
                else:
                    for row in cursor.execute(f"SELECT roles, contents, task FROM tasks WHERE roles = {mrg} AND id_serv = {ctx.guild.id};"):
                        if ctx.guild.get_role(row[0]) != None:
                            embed.add_field(
                                name=f"Contets: {row[1]}\nFor role: {ctx.guild.get_role(row[0])}",
                                value=f"Task: {row[2]}",
                                inline=False
                            )
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"**{ctx.author.mention}**, the settings are not defined by the administrator, you cannot use these commands")

@client.command( pass_context = True )
async def status_task(ctx, roles_or_task: str = None):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone()[0]:

            embed = discord.Embed(title='Tasks for role')
            if cursor.execute(f"SELECT * FROM tasks WHERE id_serv = {ctx.guild.id};").fetchone() is None:
                embed.add_field(
                    name=f"NONE",
                    value=f"sorry, didn't find it",
                    inline=False
                )

            if roles_or_task is None:
                for row in cursor.execute(f"SELECT roles, contents, task FROM tasks WHERE id_serv = {ctx.guild.id};"):
                    if ctx.guild.get_role(row[0]) != None:
                        embed.add_field(
                            name=f"Contets: {row[1]}\nFor role: {ctx.guild.get_role(row[0])}",
                            value=f"Task: {row[2]}",
                            inline=False
                        )
            else:
                mrg = roles_or_task
                if cursor.execute(f"SELECT * FROM tasks WHERE contents = '{mrg}' AND id_serv = {ctx.guild.id};").fetchall() == []:
                    embed.add_field(
                        name=f"NONE",
                        value=f"sorry, didn't find it 3",
                        inline=False
                    )
                else:
                    for row in cursor.execute(f"SELECT roles, contents, task FROM tasks WHERE contents = '{mrg}' AND id_serv = {ctx.guild.id};"):
                        if ctx.guild.get_role(row[0]) != None:
                            embed.add_field(
                                name=f"Contets: {row[1]}\nFor role: {ctx.guild.get_role(row[0])}",
                                value=f"Task: {row[2]}",
                                inline=False
                            )
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"**{ctx.author.mention}**, the settings are not defined by the administrator, you cannot use these commands")

@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def add_channel_setting(ctx):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        cursor.execute(f"UPDATE sosud SET channel = {ctx.message.channel.id} WHERE id = {ctx.guild.id} AND contents = '{morg['setting']}';")
        connection.commit()
    else:
        cursor.execute(f"INSERT INTO sosud VALUES ({ctx.guild.id}, {ctx.message.channel.id}, '{morg['setting']}');")
        connection.commit()

@client.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def add_channel_task(ctx):
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['task']}';").fetchone() is not None:
        cursor.execute(f"UPDATE sosud SET channel = {ctx.message.channel.id} WHERE id = {ctx.guild.id} AND contents = '{morg['task']}';")
        connection.commit()
    else:
        cursor.execute(f"INSERT INTO sosud VALUES ({ctx.guild.id}, {ctx.message.channel.id}, '{morg['task']}');")
        connection.commit()

@client.command()
async def help(ctx):
    embed = discord.Embed(title="commands and what they do")
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is None:
        embed.add_field(
            name=f"configuration channels for working with jobs are not defined",
            value=f"""this setting can only be made by the server administrator, if you are, 
            then see below, otherwise you will not need this information.
            
            use the command {settings['PPREFIX']}add_channel_setting to set the channel""",
            inline=False)
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['task']}';").fetchone() is None:
        embed.add_field(
            name=f"no channels defined for tasks",
            value=f"""this setting can only be made by the server administrator, if you are, 
            then see below, otherwise you will not need this information.
            
            use the command {settings['PPREFIX']}add_channel_task to set the channel""",
            inline=False)
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute(f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['setting']}';").fetchone()[0]:
            embed.add_field(
                name=f"command {settings['PPREFIX']}add",
                value=f"""The team !add allows you to add tasks for subscribers.
    in order for the command to work correctly, you must specify the command !add,
    the role for which we create the task, the name of the task in one word and the task itself, here is an example: {settings['PPREFIX']}add @role My_Chair don't otuch my chair.
    after this command, the My_Chair task for the @role roles will be added to the database""",
                inline=False)
            embed.add_field(
                name=f"command {settings['PPREFIX']}remove",
                value=f"""This command deletes all tasks for a specific role or a single task from the database. 
                In order for the task to be deleted along with the command, you need to specify the role or the name of the task.
                for example, like this:
                {settings['PPREFIX']}remove_one_task My_Chair
                {settings['PPREFIX']}remove_role_tasks @role""",
                inline=False)
            embed.add_field(
                name=f"command {settings['PPREFIX']}status",
                value=f"""This command shows which tasks are in the database.
                usage example: {settings['PPREFIX']}status
                {settings['PPREFIX']}status_role @role
                {settings['PPREFIX']}status_task My_Chair""",
                inline=False)
    if cursor.execute(f"SELECT * FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['task']}';").fetchone() is not None:
        if ctx.message.channel.id == cursor.execute( f"SELECT channel FROM sosud WHERE id_serv = {ctx.guild.id} AND contents = '{morg['task']}';").fetchone()[0]:
            embed.add_field(
                name=f"command {settings['PPREFIX']}task",
                value=f"""This command gives the user a task that was created by authorized people and sends the task in a private message. 
                It can also issue a task with a specific role, for this, write down the role after the command, for example: {settings['PPREFIX']}task @role""",
                inline=False
            )
    await ctx.send(embed=embed)

# Connect
client.run( settings['TOKEN'] )