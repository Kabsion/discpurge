import asyncio, aiohttp, discord
token = "mfa.NotAToken"
client = discord.Client()
HEADERS = {'Authorization': token} #HTTP headers
MESSAGE_CONTENTS = [
    ] #searching for messages with this content

@client.event
async def on_ready():
  print('logged in')
  for guild in client.guilds:
    print(guild.name)
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).view_channel:
            print(channel.name)
            async for message in channel.history(limit=200):
                if message.author == client.user and message.type == discord.MessageType.default:
                    for con in MESSAGE_CONTENTS:
                        if con in message.content:
                            try:
                                await message.delete()
                                print(f'deleted msg in {channel}')
                            except:
                                pass
  async with aiohttp.ClientSession() as session:
    resp = await session.get('https://discord.com/api/v9/users/@me/channels', headers=HEADERS)
    respjson = await resp.json()
    print(respjson); print('fetched dm channels')
    dmchannels = [x["id"] for x in respjson] #puts all channel ids into a list
    for channel_id in dmchannels:
        print(f'searching {channel_id}')
        resp2 = await session.get(f'https://discord.com/api/v9/channels/{channel_id}/messages?&limit=100', headers=HEADERS)
        if resp2.status == 429:
            print('wtf ratelimited one sec')
            await asyncio.sleep(5) #just sleeps 5 seconds
        resp2json = await resp2.json() #searches through all the msgs since possible response
        for message in resp2json:
            try: print(f'{message["content"]} - {message["author"]["username"]}')
            except: pass
            for MESSAGE_CONTENT in MESSAGE_CONTENTS:
                try:
                    if MESSAGE_CONTENT in message['content'] and int(message['author']['id']) == client.user.id:
                        s = await session.delete(f'https://discord.com/api/v9/channels/{channel_id}/messages/{message["id"]}', headers=HEADERS)
                        if s.status == 204:
                            print('deleted a msg')
                        elif s.status == 429:
                            print('ratelimited swhile DELETING MESSAGES')
                            jsn = await s.json()
                            await asyncio.sleep(jsn['retry_after'] + 2) 
                        await asyncio.sleep(1.5)
                except:
                    pass
        await asyncio.sleep(0.5) #avoid ratelimits
    print('do be have finished')
    await client.close()

try:
    client.run(token, bot=False)
except:
    print('invalid token')
