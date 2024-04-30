import subprocess
import sys
import pkg_resources

def install_package(package):
    try:
        dist = pkg_resources.get_distribution(package)
        print('{} ({}) is installed'.format(dist.key, dist.version))
    except pkg_resources.DistributionNotFound:
        print('{} is NOT installed'.format(package))
        subprocess.run([sys.executable, "-m", "pip", "install", package])
        
if __name__ == "__main__":
    install_package("discord.py")

import discord
from discord import app_commands
import asyncio
import os
import json
import random
from datetime import datetime, timedelta, timezone
from discord import Permissions

intents = discord.Intents.default()
intents.members = True 
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

giveaway_counter = 0
giveaways = {}
thread_solutions = {}
solution_counts = {}

# /HELP COMMAND----------------------------------------------
@tree.command(
    name="help",
    description="List all available commands and instructions",
    guild=discord.Object(id=1218638760049119242)
)
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Available Commands",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="/post",
        value="Create a post by using /post.",
        inline=False
    )
    embed.add_field(
        name="/delete",
        value="Delete your post by using /delete.",
        inline=False
    )
    embed.add_field(
        name="/solution",
        value="Give a solution by using /solution.",
        inline=False
    )
    embed.add_field(
        name="/solutions",
        value="View solutions amount by using /solutions.",
        inline=False
    )
    embed.add_field(
        name="Further Assistance",
        value="For further assistance try asking around first. If you still in need help, don't hesitate to open a ticket in <#1230989050559860886>.",  # Blue text for channel link
        inline=False
    )
    embed.add_field(
        name="Tip",
        value="You can get a message ID by enabling Developer Mode in Settings > Advanced. Then simply right-click the message and click on 'Copy Message ID'.",
        inline=False
    )
    await interaction.response.send_message(embed=embed)
    
# /SOLUTION COMMAND----------------------------------------------
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

def save_data():
    with open('solution_data.json', 'w') as f:
        json.dump({
            'thread_solutions': thread_solutions,
            'solution_counts': solution_counts
        }, f, indent=4)

def load_data():
    if os.path.isfile('solution_data.json'):
        with open('solution_data.json', 'r') as f:
            data = json.load(f)
            return data.get('thread_solutions', {}), data.get('solution_counts', {})
    return {}, {}

@tree.command(
    name="solution",
    description="Mark a message as the solution to the thread",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.describe(username="The user who provided the solution")
async def solution(interaction: discord.Interaction, username: discord.Member):
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

# /SOLUTIONS COMMAND----------------------------------------------
@tree.command(
    name="solutions",
    description="Display the number of solutions a user has",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.describe(username="The user to check the solution count for")
async def solutions(interaction: discord.Interaction, username: discord.Member):
    user_id = str(username.id)
    count = solution_counts.get(user_id, 0)
    await interaction.response.send_message(f"{username.display_name} has {count} solutions.", ephemeral=False)

# /POST COMMAND----------------------------------------------
posts = {}

def save_posts_data():
    with open('posts_data.json', 'w') as f:
        json.dump(posts, f, indent=4)

def load_posts_data():
    if os.path.isfile('posts_data.json'):
        with open('posts_data.json', 'r') as f:
            loaded_posts = json.load(f)
            return loaded_posts
    return {}

@tree.command(
    name="post",
    description="Create a post",
    guild=discord.Object(id=1218638760049119242)
)
async def post(interaction: discord.Interaction):
    await interaction.response.send_message("Initiating post creation. This will continue in DMs.", ephemeral=True)

    user = interaction.user
    dm_channel = await user.create_dm()

    def check(m):
        return m.author == user and m.channel == dm_channel

    channel_map = {
        "game-advertising": "🎮｜game-advertising",
        "group-advertising": "👥｜group-advertising",
        "sell-creations": "sell-creations",
        "scripter-hiring": "scripter-hiring",
        "builder-hiring": "builder-hiring",
        "animator-hiring": "animator-hiring",
        "modeler-hiring": "modeler-hiring",
        "graphics-hiring": "graphics-hiring",
        "programmer-hiring": "programmer-hiring",
        "clothing-hiring": "clothing-hiring",
        "ui-hiring": "ui-hiring",
        "vfx-hiring": "vfx-hiring",
        "sound-hiring": "sound-hiring",
        "video-editor-hiring": "video-editor-hiring"
    }

    channel_list = '", "'.join(channel_map.keys())
    prompt_message = f"**Available channels:** \"{channel_list}\"\n\n**Please type the channel name below.** Type 'cancel' to cancel the process."

    await dm_channel.send("✴ ⊶▬▬⊶▬▬⊷▬▬⊷▬▬⊷▬▬⊶▬▬⊷▬▬⊷▬▬⊷▬▬⊶▬▬⊷▬▬⊷▬▬⊷▬▬⊶▬▬⊷▬▬⊷▬▬⊷▬▬⊶▬▬⊷▬▬⊷▬▬⊷▬▬⊷▬▬ ✴\n\nInitiating post creation. To cancel at any point, just type 'cancel'.\n\n**Which channel should the post be in? Type 'list' to see all available channels.**\n\nMaking troll posts or posting in the wrong channel will result in consequences.")

    while True:
        try:
            channel_choice = await client.wait_for('message', check=check, timeout=600)
            if channel_choice.content.lower() == 'cancel':
                await interaction.edit_original_response(content="Process canceled.")
                await dm_channel.send("Process canceled.")
                return
            elif channel_choice.content.lower() == 'list':
                await dm_channel.send(prompt_message)
                continue

            target_channel_name = channel_map.get(channel_choice.content.lower())
            if not target_channel_name:
                await interaction.edit_original_response(content="Invalid channel name. " + prompt_message)
                await dm_channel.send("Invalid channel name. " + prompt_message)
                continue
            break
        except asyncio.TimeoutError:
            timeout_message = "You took too long to respond. Please try the command again if you wish to create a post."
            await dm_channel.send(timeout_message)
            await interaction.edit_original_response(content=timeout_message)
            return

    target_channel = discord.utils.get(interaction.guild.channels, name=target_channel_name)
    if not target_channel:
        await dm_channel.send(f"The channel {target_channel_name} does not exist.")
        await interaction.edit_original_response(content=f"The channel {target_channel_name} does not exist.")
        return

    await dm_channel.send("What is the title of your post?")
    try:
        title = await client.wait_for('message', check=check, timeout=600)
        if title.content.lower() == 'cancel':
            await dm_channel.send("Process canceled.")
            await interaction.edit_original_response(content="Post creation process has been canceled by the user.")
            return
    except asyncio.TimeoutError:
        timeout_message = "You took too long to respond when providing the title. Please try the command again if you wish to create a post."
        await dm_channel.send(timeout_message)
        await interaction.edit_original_response(content=timeout_message)
        return

    await dm_channel.send("What is the description of your post?")
    try:
        description = await client.wait_for('message', check=check, timeout=600)
        if description.content.lower() == 'cancel':
            await dm_channel.send("Process canceled.")
            await interaction.edit_original_response(content="Post creation process has been canceled by the user.")
            return
    except asyncio.TimeoutError:
        timeout_message = "You took too long to respond when providing the description. Please try the command again if you wish to create a post."
        await dm_channel.send(timeout_message)
        await interaction.edit_original_response(content=timeout_message)
        return

    await dm_channel.send("What is the payment amount? Please include the number along with the currency symbol, such as '$', depending on the payment method.")
    try:
        payment = await client.wait_for('message', check=check, timeout=600)
        if payment.content.lower() == 'cancel':
            await dm_channel.send("Process canceled.")
            await interaction.edit_original_response(content="Post creation process has been canceled by the user.")
            return
    except asyncio.TimeoutError:
        timeout_message = "You took too long to respond when providing the payment details. Please try the command again if you wish to create a post."
        await dm_channel.send(timeout_message)
        await interaction.edit_original_response(content=timeout_message)
        return

    await dm_channel.send("Would you like to include an image with your post? Please type 'yes' or 'no'. If you type 'yes', you'll have the option to attach an image in the next message.")
    try:
        image_response = await client.wait_for('message', check=check, timeout=600)
        if image_response.content.lower() == 'cancel':
            await dm_channel.send("Process canceled.")
            await interaction.edit_original_response(content="Post creation process has been canceled by the user.")
            return
    except asyncio.TimeoutError:
        timeout_message = "You took too long to respond when deciding about including an image. Please try the command again if you wish to create a post."
        await dm_channel.send(timeout_message)
        await interaction.edit_original_response(content=timeout_message)
        return

    image_url = None
    if image_response.content.lower() == 'yes':
        await dm_channel.send("Please provide the image URL or attach an image.")
        try:
            image_message = await client.wait_for('message', check=check, timeout=600)
            if image_message.content.lower() == 'cancel':
                await dm_channel.send("Process canceled.")
                await interaction.edit_original_response(content="Post creation process has been canceled by the user.")
                return
            if image_message.attachments:
                image_url = image_message.attachments[0].url
            else:
                image_url = image_message.content
        except asyncio.TimeoutError:
            timeout_message = "You took too long to respond when providing the image URL. Please try the command again if you wish to create a post."
            await dm_channel.send(timeout_message)
            await interaction.edit_original_response(content=timeout_message)
            return

    approval_embed = discord.Embed(title=title.content, description=description.content, color=discord.Color.blue())
    approval_embed.add_field(name="Payment:", value=payment.content, inline=False)
    approval_embed.add_field(name="Contact:", value=user.mention, inline=False)
    approval_embed.add_field(name="Target Channel:", value=target_channel.mention, inline=False)
    approval_embed.add_field(name="**To provide a reason for disapproving the post, please ACTUALLY REPLY to the bot's message after clicking the ❌! Simply typing the reason won't suffice without ACTUALLY REPLYING to the message. Do that by right-clicking the new message > `Reply`**", value="", inline=False)
    if image_url:
        approval_embed.set_image(url=image_url)

    approval_channel = discord.utils.get(interaction.guild.channels, name="approval")
    approval_message = await approval_channel.send(embed=approval_embed)
    await approval_message.add_reaction("✅")
    await approval_message.add_reaction("❌")
    await interaction.edit_original_response(content="Your post is under review and will be approved soon.")
    await dm_channel.send("Your post is under review and will be approved soon.")

    def check_reaction(reaction, user):
        return user != client.user and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == approval_message.id

    reaction, reactor = await client.wait_for('reaction_add', check=check_reaction)
    if str(reaction.emoji) == "✅":
        final_embed = discord.Embed(title=title.content, description=description.content, color=discord.Color.blue())
        final_embed.add_field(name="Payment:", value=payment.content, inline=False)
        final_embed.add_field(name="Contact:", value=user.mention, inline=False)
        final_embed.set_footer(text="If you're considering buying this or taking on the project, we strongly advise utilizing a Middle Man. Simply open a ticket in #📧｜tickets and tag @Middleman")
        

        if image_url:
            final_embed.set_image(url=image_url)
        sent_message = await target_channel.send(content=f"{user.mention}", embed=final_embed)
        posts[str(sent_message.id)] = (target_channel.id, user.id)
        save_posts_data()
        await interaction.edit_original_response(content="Your post has been approved and published.")
        await dm_channel.send("Your post has been approved and published.")
    elif str(reaction.emoji) == "❌":
        await approval_channel.send(f"{reactor.mention} please type the reason for disapproving the post:")

        def check_reason(m):
            return m.author == reactor and m.channel == approval_channel

        try:
            reason_message = await client.wait_for('message', check=check_reason, timeout=600)
            reason = reason_message.content.strip()

            if reason:
                await user.send(f"Your post was not approved for the following reason: {reason}")
                await interaction.edit_original_response(content=f"Your post was not approved for the following reason: {reason}")
            else:
                await user.send("Your post was not approved, but no reason was provided.")
                await interaction.edit_original_response(content="Your post was not approved, but no reason was provided.")
        except asyncio.TimeoutError:
            await user.send("Your post was not approved, but no reason was provided within the allotted time.")
            await interaction.edit_original_response(content="Your post was not approved as no reason was provided within the allotted time.")

# /DELETE COMMAND----------------------------------------------
@tree.command(
    name="delete",
    description="Delete your post",
    guild=discord.Object(id=1218638760049119242)
)
async def delete(interaction: discord.Interaction, message_id: str):
    message_id = str(message_id)

    post_info = posts.get(message_id)
    if post_info:
        if post_info[1] == interaction.user.id:
            channel_id = post_info[0]
            channel = client.get_channel(channel_id)
            if channel:
                message = await channel.fetch_message(message_id)
                if message:
                    logs_channel = discord.utils.get(interaction.guild.channels, name="logs")
                    if logs_channel:
                        deletion_note = f"Post deleted by {interaction.user.id} from {channel.mention}"
                        if message.embeds:
                            await logs_channel.send(content=deletion_note, embed=message.embeds[0])
                        else:
                            await logs_channel.send(content=deletion_note)

                    await message.delete()
                    del posts[message_id]
                    save_posts_data()
                    await interaction.response.send_message("Your post has been deleted.", ephemeral=True)
                else:
                    await interaction.response.send_message("Failed to find the message to delete.", ephemeral=True)
            else:
                await interaction.response.send_message("Failed to find the channel of the post.", ephemeral=True)
        else:
            await interaction.response.send_message("You can only delete your own posts.", ephemeral=True)
    else:
        await interaction.response.send_message("The post does not exist.", ephemeral=True)

# /CLEAR COMMAND----------------------------------------------
@tree.command(
    name="clear",
    description="Clears a specified number of messages from the channel",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(amount="Number of messages to delete")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)

    if amount < 1:
        await interaction.followup.send("Please specify an amount greater than 0.")
        return


    if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
        await interaction.followup.send("I do not have permissions to manage messages in this channel.")
        return

    try:
        deleted_messages = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Successfully deleted {len(deleted_messages)} messages.")
    except discord.Forbidden:
        await interaction.followup.send("I do not have the necessary permissions to delete messages.")
    except discord.HTTPException as e:
        await interaction.followup.send(f"Failed to delete messages due to an error: {e}")

# /CREATE_EMBED COMMAND----------------------------------------------
@tree.command(
    name="create_embed",
    description="Create an embedded message in a specific channel",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.default_permissions(administrator=True)
async def create_embed(interaction: discord.Interaction):
    await interaction.response.send_message("Initiating embed creation. This will continue in DMs.", ephemeral=True)

    user = interaction.user
    dm_channel = await user.create_dm()

    def check(m):
        return m.author == user and m.channel == dm_channel

    await dm_channel.send("Which channel should the embed be in? Please type the channel's name.")
    channel_choice = await interaction.client.wait_for('message', check=check)
    channel_name = channel_choice.content.strip().lower()

    channel_map = {
        "info": "info",
        "general": "🗣｜general",
        "announcements": "📰｜announcements",
        "new-videos": "🔔｜new-videos",
        "giveaways": "🎉｜giveaways",
        "reaction-roles": "📥｜reaction-roles",
        "event": "🎊｜events",
        "sponsored-ads": "💲｜sponsored-ads",
        "staff-chat": "staff-chat",
        "leveling": "👾｜leveling"
    }

    target_channel_name = channel_map.get(channel_name)
    if not target_channel_name:
        await dm_channel.send("Channel not found. Please check the channel name and try again.")
        return

    target_channel = discord.utils.get(interaction.guild.channels, name=target_channel_name)
    if not target_channel:
        await dm_channel.send(f"The channel {target_channel_name} does not exist.")
        return

    await dm_channel.send("What is the title of your embed?")
    title = await interaction.client.wait_for('message', check=check)

    await dm_channel.send("What is the description of your embed? You can include role mentions by typing the role name in brackets, like [Admins].")
    description = await interaction.client.wait_for('message', check=check)

    roles = {role.name: role.id for role in interaction.guild.roles}
    description_text = description.content
    for role_name, role_id in roles.items():
        description_text = description_text.replace(f"[{role_name}]", f"<@&{role_id}>")

    await dm_channel.send("Would you like to include an image with your embed? Please type 'yes' or 'no'.")
    image_response = await interaction.client.wait_for('message', check=check)
    image_url = None
    if image_response.content.lower() == 'yes':
        await dm_channel.send("Please provide the image URL.")
        image_url = await interaction.client.wait_for('message', check=check)
        image_url = image_url.content

    embed = discord.Embed(title=title.content, description=description_text, color=discord.Color.blue())
    if image_url:
        embed.set_image(url=image_url)

    await target_channel.send(embed=embed)
    await dm_channel.send("Embed sent successfully!")

    await interaction.followup.send("Embed creation completed successfully and sent to the channel.", ephemeral=True)

# /GIVEAWAY COMMAND----------------------------------------------
@tree.command(
    name="giveaway",
    description="Start a giveaway with a title, duration, and number of winners",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(title="Title of the giveaway", duration="Duration of the giveaway in seconds", num_winners="Number of winners")
async def giveaway(interaction: discord.Interaction, title: str, duration: int, num_winners: int):
    global giveaway_counter
    if num_winners < 1:
        await interaction.response.send_message("The number of winners must be at least 1.", ephemeral=True)
        return

    giveaway_counter += 1
    giveaway_id = giveaway_counter

    end_time = datetime.now(timezone.utc) + timedelta(seconds=duration)

    embed = discord.Embed(
        title=f"{title}",
        description="React with 🎉 to enter!",
        color=discord.Color.blue()
    )
    embed.timestamp = end_time
    footer_text = f"ID: {giveaway_id} | {num_winners} {'Winners' if num_winners > 1 else 'Winner'} | Ends At"
    embed.set_footer(text=footer_text)
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("🎉")

    giveaways[giveaway_id] = {
        "title": title,
        "end_time": end_time,
        "channel_id": interaction.channel_id,
        "message_id": message.id,
        "participants": set(),
        "num_winners": num_winners
    }

    client.loop.create_task(check_giveaway_end(giveaway_id))

async def check_giveaway_end(giveaway_id):
    giveaway = giveaways[giveaway_id]
    num_winners = giveaway['num_winners']
    delay = (giveaway["end_time"] - datetime.now(timezone.utc)).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)

    channel = client.get_channel(giveaway["channel_id"])
    message = await channel.fetch_message(giveaway["message_id"])
    users = [user async for user in message.reactions[0].users() if not user.bot]

    if users and len(users) >= giveaway["num_winners"]:
        winners = random.sample(users, giveaway["num_winners"])
        winners_mentions = ', '.join([winner.mention for winner in winners])
        embed = discord.Embed(
            title=f"🎁 {giveaway['title']} 🎁",
            description = f"{'Winners' if num_winners > 1 else 'Winner'}: {winners_mentions}",
            color=discord.Color.blue()
        )
        embed.timestamp = datetime.now(timezone.utc)
        footer_text = f"ID: {giveaway_id} | {giveaway['num_winners']} {'Winners' if giveaway['num_winners'] > 1 else 'Winner'} | Ended At"
        embed.set_footer(text=footer_text)
        await message.edit(embed=embed)

        winner_names = ', '.join([winner.mention for winner in winners])
        has_have = 'have' if len(winners) > 1 else 'has'
        await channel.send(f"GGs! {winner_names} {has_have} won **{giveaway['title']}**!")
        result_embed = discord.Embed(
            title="Giveaway Result",
            description=f"Congratulations to {winners_mentions}!",
            color=discord.Color.blue()
        )
        result_embed.set_footer(text="• Reply to this with !reroll(id) to reroll")
        await channel.send(embed=result_embed)
    else:
        embed = discord.Embed(
            title=f"🎁 {giveaway['title']} 🎁",
            description="Giveaway ended: Not enough participants.",
            color=discord.Color.red()
        )
        embed.timestamp = datetime.now(timezone.utc)
        footer_text = f"0 winners | Ended at | ID: {giveaway_id}"
        embed.set_footer(text=footer_text)
        await message.edit(embed=embed)

        await channel.send("Unfortunately, there were not enough participants to determine a winner.")

    giveaways[giveaway_id]['status'] = 'ended'

# REROLL GIVEAWAY COMMAND----------------------------------------------
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!reroll'):
        giveaway_id_str = message.content[len('!reroll'):].strip()
        if not giveaway_id_str.isdigit():
            await message.channel.send("Please provide a valid giveaway ID.")
            return

        giveaway_id = int(giveaway_id_str)
        if giveaway_id not in giveaways or giveaways[giveaway_id].get('status') != 'ended':
            await message.channel.send("No ended giveaway found with that ID.")
            return

        giveaway = giveaways[giveaway_id]
        channel = client.get_channel(giveaway["channel_id"])
        giveaway_message = await channel.fetch_message(giveaway["message_id"])
        users = [user async for user in giveaway_message.reactions[0].users() if not user.bot]

        if len(users) < giveaway["num_winners"]:
            await message.channel.send("Not enough participants to reroll.")
            return

        winners = random.sample(users, giveaway["num_winners"])
        winners_mentions = ', '.join([winner.mention for winner in winners])
        await message.channel.send(f"Reroll winners for giveaway ID: {giveaway_id} - {winners_mentions}")

# MEMBER STATS COMMAND----------------------------------------------
@tree.command(
    name="setup_member_count",
    description="Sets up or updates a category and a voice channel to display the live member count",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.default_permissions(administrator=True)
async def setup_member_count(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("This command must be used within a server.", ephemeral=True)
        return

    existing_channel = None
    for channel in guild.channels:
        if channel.name.startswith("⭐｜Members:"):
            existing_channel = channel
            break

    if existing_channel:
        await interaction.response.send_message("Member count channel already exists and is being updated.", ephemeral=True)
        return

    if not guild.me.guild_permissions.manage_channels:
        await interaction.response.send_message("I do not have permissions to manage channels.", ephemeral=True)
        return

    category = await guild.create_category("✴|〔 SERVER STATS 〕|✴")
    await category.edit(position=0)
    member_count = sum(1 for member in guild.members if not member.bot)
    voice_channel = await guild.create_voice_channel(f"⭐｜Members: {member_count}", category=category)
    await interaction.response.send_message("Category and member count channel created successfully!", ephemeral=True)
    client.loop.create_task(update_member_count(guild, voice_channel))

# REACTION ROLES----------------------------------------------
@client.event
async def on_raw_reaction_add(payload):

    guild = client.get_guild(payload.guild_id)
    if not guild:
        return

    reaction_roles = {
        1234643917442387978: {
            '📢': '📢Announcements Ping',
            '🎉': '🎉Event Ping',
            '🎁': '🎁Giveaway Ping',
            '📊': '📊Poll Ping',
            '❓': '❓Random Stuff Ping',
            '🎥': '🎥Video Ping',
            '📰': '📰News Ping'
        },
        1233895950238486610: {
            '💻': '💻Scripter',
            '🧬': '🧬Programmer',
            '🔧': '🔧Modeler',
            '🤺': '🤺Animator',
            '🔨': '🔨Builder',
            '📸': '📸GFX Designer',
            '✨': '✨VFX Designer',
            '🧩': '🧩UI Designer',
            '🔊': '🔊SFX Designer',
            '💼': '💼Project Manager',
            '🎭': '🎭Video Editor'
        }
    }

    roles = reaction_roles.get(payload.message_id, {})
    role_name = roles.get(payload.emoji.name)
    if role_name:
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            member = guild.get_member(payload.user_id)
            if member:
                await member.add_roles(role)

@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(payload.guild_id)
    if not guild:
        return

    reaction_roles = {
        1234643917442387978: {
            '📢': '📢Announcements Ping',
            '🎉': '🎉Event Ping',
            '🎁': '🎁Giveaway Ping',
            '📊': '📊Poll Ping',
            '❓': '❓Random Stuff Ping',
            '🎥': '🎥Video Ping',
            '📰': '📰News Ping'
        },
        1233895950238486610: {
            '💻': '💻Scripter',
            '🧬': '🧬Programmer',
            '🔧': '🔧Modeler',
            '🤺': '🤺Animator',
            '🔨': '🔨Builder',
            '📸': '📸GFX Designer',
            '✨': '✨VFX Designer',
            '🧩': '🧩UI Designer',
            '🔊': '🔊SFX Designer',
            '💼': '💼Project Manager',
            '🎭': '🎭Video Editor'
        }
    }

    roles = reaction_roles.get(payload.message_id, {})
    role_name = roles.get(payload.emoji.name)
    if role_name:
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            member = guild.get_member(payload.user_id)
            if member:
                await member.remove_roles(role)

# MEMBER STATS UPDATE COMMAND----------------------------------------------
async def update_member_count(guild, voice_channel):
    while True:
        await asyncio.sleep(600)
        if voice_channel not in guild.channels:
            print("Member count channel has been deleted. Stopping update task.")
            break
        non_bot_members = sum(1 for member in guild.members if not member.bot)
        await voice_channel.edit(name=f"⭐｜Members: {non_bot_members}")

# SYNC, LOAD DATA, START MEMBER COUNT UPDATE----------------------------------------------
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

client.run(TOKEN)