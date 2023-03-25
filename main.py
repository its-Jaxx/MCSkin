import discord
import requests
import datetime

with open('config.txt', 'r') as f:
  prefix = f.read().strip()

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print(f"Logged in as {client.user.name}")
  print("Bot is ready to use")


@client.event
async def on_message(message):
  global prefix
  if message.content.startswith(prefix + 'skin'):
    if len(message.content.split()) < 2:
      embed = discord.Embed(title="Error",
                            description="Please provide a Minecraft username",
                            color=discord.Color.red())
      await message.channel.send(embed=embed)
      return

    username = message.content[6:]
    response = requests.get(
      f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 204:
      embed = discord.Embed(
        title="Error",
        description=f"Unable to find player UUID for user {username}",
        color=discord.Color.red())
      await message.channel.send(embed=embed)
      return

    try:
      uuid = response.json()['id']
    except KeyError:
      embed = discord.Embed(
        title="Error",
        description=f"Unable to find player UUID for user {username}",
        color=discord.Color.red())
      await message.channel.send(embed=embed)
      return

    skin_url = f"https://crafatar.com/renders/body/{uuid}"

    embed = discord.Embed(title=f"Skin for user {username}")
    embed.set_image(url=skin_url)
    await message.channel.send(embed=embed)

    print(f"Received message: {message.content}")
    print(f"Parsed username: {username}")
    print(f"Retrieved UUID: {uuid}")
    print(f"Retrieved skin URL: {skin_url}")
    print("Message sent successfully")

  elif message.content.startswith(prefix + 'ping'):
    start_time = datetime.datetime.now()
    message_sent = await message.channel.send("Pinging...")
    end_time = datetime.datetime.now()

    latency = end_time - start_time
    ping_time = round(latency.total_seconds() * 1000)

    await message_sent.edit(content=f"Pong! Latency: {ping_time} ms")
    print("Ping-pong!")

  elif client.user.mentioned_in(message):
    await message.reply(f"My prefix is {prefix}")

  elif message.content.startswith(prefix + 'changeprefix'):
    if message.author.guild_permissions.administrator:
      new_prefix = message.content.split()[1]
      with open('config.txt', 'w') as f:
        f.write(new_prefix)
      await message.channel.send(f'Prefix changed to {new_prefix}')
      prefix = new_prefix
    else:
      await message.channel.send(
        "You don't have the permission to change the prefix.")


client.run("")
