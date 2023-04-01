import discord, datetime, requests
from discord.ext import commands, tasks
from datetime import datetime
from discord import app_commands

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="ping", description="Pings the bot for latency in ms")
async def ping(interaction: discord.Interaction):
    start_time = datetime.utcnow()
    end_time = datetime.utcnow()

    latency = end_time - start_time
    ping_time = round(latency.total_seconds() * 1000)

    await interaction.response.send_message(f"Pong! Latency: {ping_time} ms")

@tree.command(name="skin", description="Get the skin for a Minecraft user")
async def skin(interaction: discord.Interaction, username: str):
    if not username:
        embed = discord.Embed(title="Error", description="Please provide a Minecraft username", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 204:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(value=f"Unable to find player UUID for user {username}")
        embed.add_field(value=f"Make sure you spelled it correctly")
        await interaction.response.send_message(embed=embed)
        return

    try:
        uuid = response.json()['id']
    except KeyError:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value=f"Unable to find player UUID for user {username}", inline=False)
        embed.add_field(name="", value=f"Make sure you spelled it correctly", inline=False)
        await interaction.response.send_message(embed=embed)
        return

    skin_url = f"https://crafatar.com/renders/body/{uuid}"
    model_url = f"https://crafatar.com/skins/{uuid}"

    embed = discord.Embed(title=f"Skin for user {username}")
    embed.set_image(url=skin_url)
    embed.add_field(name="", value=f"[Click to download template]({model_url})", inline=False)
    await interaction.response.send_message(embed=embed)
    print(f"Received command: {interaction.data['name']}\nUsername: {username}\nUUID: {uuid}\nSkin: {skin_url}\nModel: {model_url}\nCommand sent")

@tree.command(name="steal", description="Get the skin for a Minecraft user")
async def skin(interaction: discord.Interaction, username: str):
    if not username:
        embed = discord.Embed(title="Error", description="Please provide a Minecraft username", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 204:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(value=f"Unable to find player UUID for user {username}")
        embed.add_field(value=f"Make sure you spelled it correctly")
        await interaction.response.send_message(embed=embed)
        return

    try:
        uuid = response.json()['id']
    except KeyError:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value=f"Unable to find player UUID for user {username}", inline=False)
        embed.add_field(name="", value=f"Make sure you spelled it correctly", inline=False)
        await interaction.response.send_message(embed=embed)
        return

    skin_url = f"https://crafatar.com/renders/body/{uuid}"
    model_url = f"https://crafatar.com/skins/{uuid}"

    embed = discord.Embed(title=f"Skin for user {username}")
    embed.set_image(url=skin_url)
    embed.add_field(name="", value=f"[Click to download template]({model_url})", inline=False)
    await interaction.response.send_message(embed=embed)
    print(f"Received command: {interaction.data['name']}\nUsername: {username}\nUUID: {uuid}\nSkin: {skin_url}\nModel: {model_url}\nCommand sent")

@tree.command(name="creator", description="List of the people who created me")
async def creator(ctx):
    nismo_url = f"https://github.com/nismo1337"
    jaxx_url = f"https://github.com/its-Jaxx"
    github_url = f"https://github.com/nismo1337/MCSkin"
    embed = discord.Embed(title="I was created by:", color=discord.Color.blue())
    embed.add_field(name="", value=f"[nismo1337]({nismo_url})", inline=False)
    embed.add_field(name="", value=f"[its-Jaxx]({jaxx_url})", inline=False)
    embed.add_field(name="", value=f"[Open source on github]({github_url})", inline=False)

    await ctx.response.send_message(embed=embed)

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")
    activity = discord.Activity(name="Minecraft", type=discord.ActivityType.playing)
    await client.change_presence(activity=activity)
    print(f"Logged in as {client.user.name}\nBot is ready to use\n-------------------")

client.run("bot token here")
