import discord
import requests

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")
    print("Bot is ready to use")

@client.event
async def on_message(message):
    if message.content.startswith('!skin'):
        username = message.content[6:]
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if response.status_code == 204:
            embed = discord.Embed(title="Error", description=f"Unable to find player UUID for user {username}", color=discord.Color.red())
            await message.channel.send(embed=embed)
            return
        
        try:
            uuid = response.json()['id']
        except KeyError:
            embed = discord.Embed(title="Error", description=f"Unable to find player UUID for user {username}", color=discord.Color.red())
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
    elif message.content.startswith('!ping'):
        await message.channel.send("Pong!")
        print("Ping-pong!")

client.run("put ur bot token here :D")
