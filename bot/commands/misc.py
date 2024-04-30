import discord
from discord import app_commands
import asyncio

# Clear command
@app_commands.command(
    name="clear",
    description="Clears a specified number of messages from the channel",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.describe(amount="Number of messages to delete")
async def clear_command(interaction: discord.Interaction, amount: int):
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

# Create embed command
@app_commands.command(
    name="create_embed",
    description="Create an embedded message in a specific channel",
    guild=discord.Object(id=1218638760049119242)
)
async def create_embed_command(interaction: discord.Interaction):
    await interaction.response.send_message("Initiating embed creation. This will continue in DMs.", ephemeral=True)

    def check(m):
        return m.author == interaction.user and m.channel == interaction.user.dm_channel

    dm_channel = await interaction.user.create_dm()

    await dm_channel.send("What is the title of your embed?")
    title = await interaction.client.wait_for('message', check=check)

    await dm_channel.send("What is the description of your embed?")
    description = await interaction.client.wait_for('message', check=check)

    embed = discord.Embed(title=title.content, description=description.content, color=discord.Color.blue())

    await dm_channel.send("Do you want to add any fields to your embed? (yes/no)")
    add_fields = await interaction.client.wait_for('message', check=check)

    if add_fields.content.lower() == 'yes':
        await dm_channel.send("How many fields do you want to add?")
        field_count = await interaction.client.wait_for('message', check=check)
        field_count = int(field_count.content)

        for i in range(field_count):
            await dm_channel.send(f"What is the name of field {i+1}?")
            field_name = await interaction.client.wait_for('message', check=check)

            await dm_channel.send(f"What is the value of field {i+1}?")
            field_value = await interaction.client.wait_for('message', check=check)

            embed.add_field(name=field_name.content, value=field_value.content, inline=False)

    await interaction.response.send_message("Your embed is ready!", embed=embed)

# Setup member count command
async def update_member_count(guild, voice_channel):
    while True:
        await asyncio.sleep(600)
        if voice_channel not in guild.channels:
            print("Member count channel has been deleted. Stopping update task.")
            break
        non_bot_members = sum(1 for member in guild.members if not member.bot)
        await voice_channel.edit(name=f"Members: {non_bot_members}")

@app_commands.command(
    name="setup_member_count",
    description="Sets up or updates a category and a voice channel to display the live member count",
    guild=discord.Object(id=1218638760049119242)
)
async def setup_member_count_command(interaction: discord.Interaction):
    guild = interaction.guild
    category_name = "Member Count"
    voice_channel_name = "Member Count"

    category = discord.utils.get(guild.categories, name=category_name)
    if not category:
        category = await guild.create_category(category_name)

    voice_channel = discord.utils.get(guild.voice_channels, name=voice_channel_name)
    if not voice_channel:
        voice_channel = await guild.create_voice_channel(voice_channel_name, category=category)

    # Start the background task to update the member count
    interaction.client.loop.create_task(update_member_count(guild, voice_channel))

    await interaction.response.send_message("Member count setup is complete!", ephemeral=True)

# Help command
@app_commands.command(
    name="help",
    description="List all available commands and instructions",
    guild=discord.Object(id=1218638760049119242)
)
async def help_command(interaction: discord.Interaction):
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
        value="For further assistance try asking around first. If you still in need help, don't hesitate to open a ticket in <#1230989050559860886>.", # Blue text for channel link
        inline=False
    )
    embed.add_field(
        name="Tip",
        value="You can get a message ID by enabling Developer Mode in Settings > Advanced. Then simply right-click the message and click on 'Copy Message ID'.",
        inline=False
    )
    await interaction.response.send_message(embed=embed)
