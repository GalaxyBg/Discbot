import discord
from discord import app_commands
import json
import os

# Global variables for thread solutions and solution counts
thread_solutions = {}
solution_counts = {}

# Function to save data
def save_data():
    with open('solution_data.json', 'w') as f:
        json.dump({
            'thread_solutions': thread_solutions,
            'solution_counts': solution_counts
        }, f, indent=4)

# Function to load data
def load_data():
    if os.path.isfile('solution_data.json'):
        with open('solution_data.json', 'r') as f:
            data = json.load(f)
            return data.get('thread_solutions', {}), data.get('solution_counts', {})
    return {}, {}

solution_roles = {
    1: "[1+] Initiate",
    3: "[3+] Adept",
    5: "[5+] Chief",
    10: "[10+] Mentor",
    15: "[15+] Guru",
    20: "[20+] Seasoned",
    25: "[25+] Elite",
    50: "[50+] Supreme",
    75: "[75+] Pinnacle",
    100: "[100+] Zenith"
}

# Solution command
@app_commands.command(
    name="solution",
    description="Mark a message as the solution to the thread",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.describe(username="The user who provided the solution")
async def solution_command(interaction: discord.Interaction, username: discord.Member):
    if not isinstance(interaction.channel, discord.Thread) or interaction.channel.parent.name != "studio-help":
        await interaction.response.send_message("This command can only be used within a thread of the 'studio-help' forum channel.", ephemeral=True)
        return

    if interaction.user.id != interaction.channel.owner_id:
        await interaction.response.send_message("You can only mark a solution in a thread you created.", ephemeral=True)
        return

    if interaction.user.id == username.id:
        await interaction.response.send_message("You cannot mark your own message as the solution.", ephemeral=True)
        return

    user_has_interacted = False
    async for message in interaction.channel.history(limit=200):
        if message.author.id == username.id:
            user_has_interacted = True
            break

    if not user_has_interacted:
        await interaction.response.send_message("The user must have interacted in this thread to receive the solution.", ephemeral=True)
        return

    thread_id = str(interaction.channel.id)
    user_id = str(username.id)

    if thread_id in thread_solutions:
        await interaction.response.send_message("A solution has already been marked in this thread.", ephemeral=True)
        return

    thread_solutions[thread_id] = True
    solution_counts[user_id] = solution_counts.get(user_id, 0) + 1

    save_data()

    new_role_name = solution_roles.get(solution_counts[user_id])
    if new_role_name:
        current_roles = [role for role in username.roles if role.name in solution_roles.values()]
        for role in current_roles:
            await username.remove_roles(role)

        new_role = discord.utils.get(interaction.guild.roles, name=new_role_name)
        if new_role:
            await username.add_roles(new_role)
            role_message = f" and have been assigned the role {new_role_name}"
        else:
            role_message = ""
    else:
        role_message = "."

    await interaction.response.send_message(f"{username.mention} has been marked as providing the solution! They now have {solution_counts[user_id]} solutions{role_message}.", ephemeral=False)

# Solutions command
@app_commands.command(
    name="solutions",
    description="Display the number of solutions a user has",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.describe(username="The user to check the solution count for")
async def solutions_command(interaction: discord.Interaction, username: discord.Member):
    user_id = str(username.id)
    count = solution_counts.get(user_id, 0)
    await interaction.response.send_message(f"{username.display_name} has {count} solutions.", ephemeral=False)
