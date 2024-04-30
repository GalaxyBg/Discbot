import discord
from discord import app_commands
import random
from datetime import datetime, timedelta, timezone
import asyncio

# Global variable for giveaways
giveaways = {}
giveaway_counter = 0

# Giveaway command
@app_commands.command(
    name="giveaway",
    description="Start a giveaway with a title, duration, and number of winners",
    guild=discord.Object(id=1218638760049119242)
)
@app_commands.describe(title="Title of the giveaway", duration="Duration of the giveaway in seconds", num_winners="Number of winners")
async def giveaway_command(interaction: discord.Interaction, title: str, duration: int, num_winners: int):
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

    # Schedule the giveaway end check
    asyncio.create_task(check_giveaway_end(giveaway_id))

async def check_giveaway_end(giveaway_id, client):
    giveaway = giveaways[giveaway_id]
    num_winners = giveaway['num_winners']
    delay = (giveaway["end_time"] - datetime.now(timezone.utc)).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)

    channel = client.get_channel(giveaway["channel_id"])
    if not channel:
        print(f"Channel not found for giveaway ID: {giveaway_id}")
        return

    try:
        message = await channel.fetch_message(giveaway["message_id"])
    except discord.NotFound:
        print(f"Message not found for giveaway ID: {giveaway_id}")
        return

    users = [user async for user in message.reactions[0].users() if not user.bot]

    if users and len(users) >= giveaway["num_winners"]:
        winners = random.sample(users, giveaway["num_winners"])
        winners_mentions = ', '.join([winner.mention for winner in winners])
        embed = discord.Embed(
            title=f"🎁 {giveaway['title']} 🎁",
            description=f"{'Winners' if num_winners > 1 else 'Winner'}: {winners_mentions}",
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


# Reroll command
async def reroll_command(message):
    giveaway_id_str = message.content[len('!reroll'):].strip()
    if not giveaway_id_str.isdigit():
        await message.channel.send("Please provide a valid giveaway ID.")
        return

    giveaway_id = int(giveaway_id_str)
    if giveaway_id not in giveaways or giveaways[giveaway_id].get('status') != 'ended':
        await message.channel.send("No ended giveaway found with that ID.")
        return

    giveaway = giveaways[giveaway_id]
    channel = message.guild.get_channel(giveaway["channel_id"])
    giveaway_message = await channel.fetch_message(giveaway["message_id"])
    users = [user async for user in giveaway_message.reactions[0].users() if not user.bot]

    if len(users) < giveaway["num_winners"]:
        await message.channel.send("Not enough participants to reroll.")
        return

    winners = random.sample(users, giveaway["num_winners"])
    winners_mentions = ', '.join([winner.mention for winner in winners])
    await message.channel.send(f"Reroll winners for giveaway ID: {giveaway_id} - {winners_mentions}")
