import discord, datetime, requests, os, aiohttp, aioredis
from mcstatus import *
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from discord import app_commands
from PIL import Image
from PIL import *
from io import BytesIO
from typing import Dict

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
cooldowns: Dict[int, Dict[str, datetime]] = {}

@commands.cooldown(1, 5, commands.BucketType.user)
@tree.command(name="ping", description="Pings the bot for image processing latency in ms")
async def ping(interaction: discord.Interaction):
    user_id = interaction.user.id
    command_name = "ping"
    if user_id not in cooldowns:
        cooldowns[user_id] = {}

    now = datetime.now()
    if command_name in cooldowns[user_id]:
        cooldown_end_time = cooldowns[user_id][command_name]
        if now < cooldown_end_time:
            time_left = (cooldown_end_time - now).total_seconds()
            response = f"Please wait {time_left:.1f} seconds before using this command again."
            await interaction.response.send_message(response, ephemeral=True)
            return

    start_time = datetime.utcnow()

    minetar_url = "https://api.mineatar.io/body/full/161c986278854ef8af3dd7631d9610f9"
    imgur_url = "https://api.imgur.com/3/image"
    async with aiohttp.ClientSession() as session:
        async with session.get(minetar_url) as resp:
            image_bytes = await resp.read()
    with BytesIO(image_bytes) as image_buffer:
        with Image.open(image_buffer) as image:
            image.thumbnail((256, 256))
            with BytesIO() as output_buffer:
                image.save(output_buffer, "PNG")
                output_bytes = output_buffer.getvalue()

    headers = {
        "Authorization": f"Client-ID [YOUR_CLIENT_ID]"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(imgur_url, headers=headers, data=output_bytes) as resp:
            imgur_data = await resp.json()
    imgur_url = imgur_data["data"]["link"]

    end_time = datetime.utcnow()
    latency = end_time - start_time
    processing_time = round((end_time - start_time - latency).total_seconds() * 1000)
    ping_time = round(latency.total_seconds() * 1000)

    cooldowns[user_id][command_name] = now + timedelta(seconds=5)
    await interaction.response.send_message(
        f"Pinging image processing and upload time... (this may take a few seconds)")
    await interaction.edit_original_response(
        content=f"Pong!\nImage processing and upload time: {ping_time} ms")

@tree.command(name="help", description="Provides a list of commands MCSkin currently supports")
async def help(ctx):

    embed = discord.Embed(title="Command list", color=discord.Color.blue())
    embed.add_field(name="", value=f"/ping - Pings the bot for image processing latency in ms", inline=False)
    embed.add_field(name="", value=f"/skin 'username' - Fetches Minecraft model of desired username", inline=False)
    embed.add_field(name="", value=f"/steal 'username' - Fetches Minecraft model of desired username", inline=False)
    embed.add_field(name="", value=f"/creator - Shows a list of the current creators/owners of the bot.", inline=False)
    embed.add_field(name="", value=f"/java 'server ip' Quickly retrieve the status of any Java Minecraft server", inline=False)
    embed.add_field(name="", value=f"/hypixel 'username' - Displays what game specified user is playing within Hypixel", inline=False)
    embed.add_field(name="", value=f"/help - displays this list of commands", inline=False)

    await ctx.response.send_message(embed=embed)

@tree.command(name="hypixel", description="Displays information of a Hypixel user")
async def hypixel(interaction: discord.Interaction, username: str):
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

    embed = discord.Embed(title=f"Hypixel user {username}:", color=discord.Color.blurple())

    try:
        uuid = response.json()['id']
    except KeyError:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value=f"Unable to find player UUID for user {username}")
        embed.add_field(name="", value=f"Make sure you spelled it correctly", inline=False)
        await interaction.response.send_message(embed=embed)

    api_key = f"YOUR_API_KEY"
    status_url = f"https://api.hypixel.net/status?key={api_key}&uuid={uuid}"
    player_url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"

    response = requests.get(status_url)
    if response.status_code == 403:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value="API Key is invalid, please contact the owner regarding this issue.")
        print("Invalid API key")
        await interaction.response.send_message(embed=embed)
        return

    session = response.json()["session"]

    if session['online']:
        if 'gameType' in session:
            game_type = session['gameType']
            if game_type == 'LEGACY':
                embed.add_field(name="", value=f"{username} is in Limbo", inline=False)
            elif 'mode' in session and session['mode'] == 'LOBBY':
                embed.add_field(name="", value=f"{username} is in {game_type} lobby", inline=False)
            else:
                embed.add_field(name="", value=f"{username} is currently playing {game_type}", inline=False)
        else:
            embed.add_field(name="", value=f"{username} is online", inline=False)
    else:
        embed.add_field(name="", value=f"{username} is offline", inline=False)
    await interaction.response.send_message(embed=embed)
    print(f"Received command: {interaction.data['name']}\nUsername: {username}\nUUID: {uuid}\nCommand sent\n")

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

    rendered_skin_url = f"https://api.mineatar.io/body/full/{uuid}"
    model_url = f"https://crafatar.com/skins/{uuid}"
    response = requests.get(rendered_skin_url)

    image = Image.open(BytesIO(response.content))
    image = image.resize((120, 270))
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    headers = {"Authorization": f"Client-ID [YOUR_CLIENT_ID]"}
    imgur_url = "https://api.imgur.com/3/image"
    response = requests.post(imgur_url, headers=headers, data={"image": img_bytes})
    full_skin_url = response.json()["data"]["link"]

    embed = discord.Embed(title=f"Skin for user {username}", color=discord.Color.blurple())
    embed.set_image(url=full_skin_url)
    embed.add_field(name="", value=f"[Click to download template]({model_url})", inline=False)
    embed.add_field(name="", value=f"UUID: {uuid}", inline=False)
    await interaction.response.send_message(embed=embed)
    print(f"Received command: {interaction.data['name']}\nUsername: {username}\nUUID: {uuid}\nSkin: {full_skin_url}\nModel: {model_url}\nCommand sent")

@tree.command(name="steal", description="Get the skin for a Minecraft user")
async def steal(interaction: discord.Interaction, username: str):
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

    rendered_skin_url = f"https://api.mineatar.io/body/full/{uuid}"
    model_url = f"https://crafatar.com/skins/{uuid}"
    response = requests.get(rendered_skin_url)

    image = Image.open(BytesIO(response.content))
    image = image.resize((120, 270))
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    headers = {"Authorization": f"Client-ID [YOUR_CLIENT_ID]"}
    imgur_url = "https://api.imgur.com/3/image"
    response = requests.post(imgur_url, headers=headers, data={"image": img_bytes})
    full_skin_url = response.json()["data"]["link"]

    embed = discord.Embed(title=f"Skin for user {username}", color=discord.Color.blurple())
    embed.set_image(url=full_skin_url)
    embed.add_field(name="", value=f"[Click to download template]({model_url})", inline=False)
    embed.add_field(name="", value=f"UUID: {uuid}", inline=False)

    await interaction.response.send_message(embed=embed)
    print(f"Received command: {interaction.data['name']}\nUsername: {username}\nUUID: {uuid}\nSkin: {full_skin_url}\nModel: {model_url}\nCommand sent")

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

@tree.command(name="java", description="Quickly retrieve the status of any Java Minecraft server")
async def java(interaction: discord.Interaction, java_address: str):

    try:
        server = JavaServer(java_address)
        status = server.status()

        embed = discord.Embed(title=f"Status of {java_address}", color=discord.Color.green())
        embed.add_field(name="Status", value="Online", inline=False)
        embed.add_field(name="Host", value=java_address, inline=False)
        embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{java_address}")
        embed.add_field(name="Version", value=status.version.name, inline=False)
        embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=False)
        embed.add_field(name="Protocol Version", value=status.version.protocol, inline=False)

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"An error occurred while retrieving the server status: {e}")

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")
    activity = discord.Activity(name="Minecraft", type=discord.ActivityType.playing)
    await client.change_presence(activity=activity)
    print(f"Logged in as {client.user.name}\nBot is ready to use\n-------------------")

client.run("YOUR_BOT_TOKEN")
