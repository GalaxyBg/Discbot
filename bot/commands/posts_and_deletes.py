import discord
from discord import app_commands
import json
import os
import asyncio

# Global variable for posts
posts = {}

# Function to save posts data
def save_posts_data():
    with open('posts_data.json', 'w') as f:
        json.dump(posts, f, indent=4)

# Function to load posts data
def load_posts_data():
    if os.path.isfile('posts_data.json'):
        with open('posts_data.json', 'r') as f:
            loaded_posts = json.load(f)
            return loaded_posts
    return {}

# Post command
@app_commands.command(
    name="post",
    description="Create a post",
    guild=discord.Object(id=1218638760049119242)
)
async def post_command(interaction: discord.Interaction, client):
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


@app_commands.command(
    name="delete",
    description="Delete your post",
    guild=discord.Object(id=1218638760049119242)
)
async def delete_command(interaction: discord.Interaction, message_id: str, client):
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
