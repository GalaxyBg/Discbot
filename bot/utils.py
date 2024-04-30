import json
import os
import asyncio

def save_data():
    with open('solution_data.json', 'w') as f:
        json.dump({
            'thread_solutions': thread_solutions,#global variable
            'solution_counts': solution_counts#global variable
        }, f, indent=4)

def load_data():
    if os.path.isfile('solution_data.json'):
        with open('solution_data.json', 'r') as f:
            data = json.load(f)
            return data.get('thread_solutions', {}), data.get('solution_counts', {})
    return {}, {}

def save_posts_data():
    with open('posts_data.json', 'w') as f:
        json.dump(posts, f, indent=4)#global variable

def load_posts_data():
    if os.path.isfile('posts_data.json'):
        with open('posts_data.json', 'r') as f:
            loaded_posts = json.load(f)
            return loaded_posts
    return {}

async def update_member_count(guild, voice_channel):
    while True:
        await asyncio.sleep(600)
        if voice_channel not in guild.channels:
            print("Member count channel has been deleted. Stopping update task.")
            break
        non_bot_members = sum(1 for member in guild.members if not member.bot)
        await voice_channel.edit(name=f"Members: {non_bot_members}")
