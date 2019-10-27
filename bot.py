# bot.py
import os

import discord
f = list(open('.env'))

TOKEN = f[0].strip('\n')
GUILD = f[1].strip('\n')

print(TOKEN)
print(GUILD)

client = discord.Client()

kzCounter = 0
    
@client.event
async def on_message(message):
    if message.author != client.user:
        #failsafe against self response
        print(str(message.author))
        if (str(message.author) == 'Wahaha#0365'):
            await message.channel.send('ur bad lol')
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
        if '$comrade' in message.content.lower():
            parse = str(message.content).strip('$comrade').split()
            print(parse)
            if parse[0] == 'banKZ':
                global kzCounter
                kzCounter += 1
                await message.channel.send(str('Vote added.' + str(2-kzCounter) + ' more needed to kick.' ))
                if (kzCounter >= 2):
                    tgt = ''
                    for member in message.guild.members:
                        if str(member) == 'Wahaha#0365':
                            tgt = member
                     
                    await message.channel.send(str('@' + str(tgt)+ ' has been kicked successfully'))
            
            

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    kzCounter = 0
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')
    

client.run(TOKEN)