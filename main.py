import discord, requests, datetime
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    activity = discord.Activity(name="Minecraft", type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)
    print(f"Logged in as {bot.user.name}\nBot is ready to use\n-------------------")

@bot.command(aliases=["steal"])
async def skin(ctx, *, username=None):
    if not username:
        embed = discord.Embed(title="Error", description="Please provide a Minecraft username", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 204:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(value=f"Unable to find player UUID for user {username}")
        embed.add_field(value=f"Make sure you spelled it correctly")
        await ctx.send(embed=embed)
        return
    
    try:
        uuid = response.json()['id']
    except KeyError:
        embed = discord.Embed(title="Error", color=discord.Color.red())
        embed.add_field(name="", value=f"Unable to find player UUID for user {username}", inline=False)
        embed.add_field(name="", value=f"Make sure you spelled it correctly", inline=False)
        await ctx.send(embed=embed)
        return

    skin_url = f"https://crafatar.com/renders/body/{uuid}"
    model_url = f"https://crafatar.com/skins/{uuid}"

    embed = discord.Embed(title=f"Skin for user {username}")
    embed.set_image(url=skin_url)
    embed.add_field(name="", value=f"[Click to download template]({model_url})", inline=False)
    await ctx.send(embed=embed)

    print(f"Received command: {ctx.message.content}\nUsername: {username}\nUUID: {uuid}\nSkin: {skin_url}\nModel: {model_url}\nCommand sent")

@bot.command()
async def ping(ctx):
    start_time = datetime.datetime.now()
    message_sent = await ctx.send("Pinging...")
    end_time = datetime.datetime.now()

    latency = end_time - start_time
    ping_time = round(latency.total_seconds() * 1000)

    await message_sent.edit(content=f"Pong! Latency: {ping_time} ms")
    print("Ping-pong!")
    
@bot.command(aliases=["command"])
async def commands(ctx):
    skin = "Grabs a model of the skin"
    ping = "Pings the server to retrieve latency in ms"
    mention1 = "@mention"
    mention2 = "Ping the bot to get the current prefix"
    commandlist = "Shows this list of commands"
    creatorlist = "Shows who created the bot"

    embed = discord.Embed(title="Commands List", color=discord.Color.green())
    embed.add_field(name="!skin - !steal", value=f"{skin}", inline=False)
    embed.add_field(name="!ping", value=f"{ping}", inline=False)
    embed.add_field(name=f"{mention1}", value=f"{mention2}", inline=False)
    embed.add_field(name="!command", value=f"{commandlist}", inline=False)
    embed.add_field(name="!creator", value=f"{creatorlist}", inline=False)

    message_sent = await ctx.send(embed=embed)
    print("Commands list being printed")
    
@bot.command(aliases=["creators"])
async def creator(ctx):
    nismo_url = f"https://github.com/nismo1337"
    jaxx_url = f"https://github.com/its-Jaxx"
    github_url = f"https://github.com/nismo1337/MCSkin"
    embed = discord.Embed(title="I was created by:", color=discord.Color.blue())
    embed.add_field(name="", value=f"[nismo1337]({nismo_url})", inline=False)
    embed.add_field(name="", value=f"[its-Jaxx]({jaxx_url})", inline=False)
    embed.add_field(name="", value=f"[Open source on github]({github_url})", inline=False)
    
    message_sent = await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.reply(f"My prefix is `!`")
    
    await bot.process_commands(message)

bot.run("Put your bot token here")
