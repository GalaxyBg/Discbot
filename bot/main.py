import discord
from discord import app_commands
import os
from commands import (
    help_command, solution_command, solutions_command, post_command,
    delete_command, clear_command, create_embed_command, giveaway_command,
    setup_member_count_command, reroll_command
)
from utils import load_data, load_posts_data, update_member_count

intents = discord.Intents.default()
intents.members = True 
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

@client.event
async def on_ready():
    global thread_solutions, solution_counts
    thread_solutions, solution_counts = load_data()
    global posts
    posts = load_posts_data()
    activity = discord.CustomActivity("/help")
    await client.change_presence(activity=activity)
    print(f"Logged in as {client.user} and ready!")
    await tree.sync(guild=discord.Object(id=1218638760049119242))

    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name.startswith("⭐｜Members:"):
                client.loop.create_task(update_member_count(guild, channel))
                break

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!reroll'):
        await reroll_command(message)

client.run(TOKEN)
