# Imports important libraries
import discord, datetime, requests, os
from discord.ext import commands, tasks
from datetime import datetime
from discord import app_commands
from PIL import Image
from io import BytesIO

# Important intents to make things function properly
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# Ping command - Pings the bot for latency
@tree.command(name="ping", description="Pings the bot for image processing latency in ms")
async def ping(interaction: discord.Interaction):
    start_time = datetime.utcnow()
    # Request image from Minetar and resize it
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

    # Upload the image to Imgur
    headers = {
        "Authorization": f"Client-ID IMGUR_CLIENT_ID"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(imgur_url, headers=headers, data=output_bytes) as resp:
            imgur_data = await resp.json()
    imgur_url = imgur_data["data"]["link"]
    
    # Send the message back with latency and image processing time
    end_time = datetime.utcnow()
    latency = end_time - start_time
    processing_time = round((end_time - start_time - latency).total_seconds() * 1000)
    ping_time = round(latency.total_seconds() * 1000)
    await interaction.response.send_message(
        f"Pinging image processing and upload time... (this may take a few seconds)")
    await interaction.edit_original_response(
        content=f"Pong!\nImage processing and upload time: {ping_time} ms")
    
    @tree.command(name="help", description="Provides a list of commands MCSkin currently supports")
async def help(ctx):
    help_one = f"/ping - Pings the bot for image processing latency in ms"
    help_two = f"/skin 'username' - Fetches Minecraft model of desired username"
    help_three = f"/steal 'username' - Fetches Minecraft model of desired username"
    help_four = f"/creator - Shows a list of the current creators/owners of the bot."
    help_five = f"/help - displays this list of commands"
    embed = discord.Embed(title="Command list", color=discord.Color.blue())
    embed.add_field(name="", value=f"{help_one}", inline=False)
    embed.add_field(name="", value=f"{help_two}", inline=False)
    embed.add_field(name="", value=f"{help_three}", inline=False)
    embed.add_field(name="", value=f"{help_four}", inline=False)
    embed.add_field(name="", value=f"{help_five}", inline=False)

    await ctx.response.send_message(embed=embed)
    
# Skin command - Get the skin for a Minecraft user
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

    headers = {"Authorization": f"Client-ID IMGUR_CLIENT_ID"}
    imgur_url = "https://api.imgur.com/3/image"
    response = requests.post(imgur_url, headers=headers, data={"image": img_bytes})
    full_skin_url = response.json()["data"]["link"]

    embed = discord.Embed(title=f"Skin for user {username}")
    embed.set_image(url=full_skin_url)
    embed.add_field(name="", value=f"[Click to download template]({model_url})", inline=False)
    embed.add_field(name="", value=f"UUID: {uuid}", inline=False)
    await interaction.response.send_message(embed=embed)
    print(f"Received command: {interaction.data['name']}\nUsername: {username}\nUUID: {uuid}\nSkin: {full_skin_url}\nModel: {model_url}\nCommand sent")

# Steal command - Get the skin for a Minecraft user
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
    rendered_skin_url = f"https://api.mineatar.io/body/full/{uuid}"
    model_url = f"https://crafatar.com/skins/{uuid}"
    response = requests.get(rendered_skin_url)

    image = Image.open(BytesIO(response.content))
    image = image.resize((120, 270))
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    headers = {"Authorization": f"Client-ID IMGUR_CLIENT_ID"}
    imgur_url = "https://api.imgur.com/3/image"
    response = requests.post(imgur_url, headers=headers, data={"image": img_bytes})
    full_skin_url = response.json()["data"]["link"]

    embed = discord.Embed(title=f"Skin for user {username}")
    embed.set_image(url=full_skin_url)
    embed.add_field(name="", value=f"[Click to download template]({model_url})", inline=False)
    embed.add_field(name="", value=f"UUID: {uuid}", inline=False)
    await interaction.response.send_message(embed=embed)
    print(f"Received command: {interaction.data['name']}\nUsername: {username}\nUUID: {uuid}\nSkin: {full_skin_url}\nModel: {model_url}\nCommand sent")
# Creator command - List of the people who created me
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
# Connects between bot server and Discord and readies it up

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")
    activity = discord.Activity(name="Minecraft", type=discord.ActivityType.playing)
    await client.change_presence(activity=activity)
    print(f"Logged in as {client.user.name}\nBot is ready to use\n-------------------")

client.run("")
