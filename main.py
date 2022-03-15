import discord
import youtube_dl
import os
import requests
import json
import asyncio
from os.path import exists
from keep_alive import keep_alive
from discord.ext import commands, tasks
from requests import Requests

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

in_voice_channel = False
last_played_audio = ''
DM_ID = '316229726555340801'

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        if not exists(filename):
          os.remove(filename)
          last_played_audio = ''
        else:
          last_played_audio = filename
        return filename

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
  global in_voice_channel
  if not ctx.message.author.voice:
      await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
      return
  else:
      channel = ctx.message.author.voice.channel
  await channel.connect()
  in_voice_channel = True

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
  global in_voice_channel
  voice_client = ctx.message.guild.voice_client
  try:
    if voice_client.is_connected():
        await voice_client.disconnect()
        in_voice_channel = False
    else:
        in_voice_channel = False
        await ctx.send("Error with leave command")
  except:
    print('Error disconnecting from voice client')

@bot.command(name='play', help='To play audio')
async def play(ctx,url):
  global in_voice_channel, last_played_audio
  try:
    voice_client = ctx.message.guild.voice_client
    if not in_voice_channel:
      await join(ctx)
    if voice_client.is_playing():
      await stop(ctx)
      in_voice_channel = True
  except:
    await ctx.send("Error stopping song/joining channel")
    server = ctx.message.guild
    voice_channel = server.voice_client
  try:
    async with ctx.typing():
      filename = await YTDLSource.from_url(url, loop=bot.loop)
      voice_channel.play(discord.FFmpegPCMAudio(filename))
    await ctx.send('**Now playing:** {}'.format(filename))
  except:
    await ctx.send("Error loading song")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
  global in_voice_channel
  try:
    if not in_voice_channel:
      await join(ctx)
  except:
    print('Error joining the voice channel upon pause')
  voice_client = ctx.message.guild.voice_client
  if voice_client.is_playing():
    voice_client.pause()
  else:
    await ctx.send("Error with pause command")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
  global in_voice_channel
  if not in_voice_channel:
        await join(ctx)
        in_voice_channel = True
  voice_client = ctx.message.guild.voice_client
  if voice_client.is_paused():
    voice_client.resume()
  else:
    await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
  global in_voice_channel
  try:
    if not in_voice_channel:
      await join(ctx)
      in_voice_channel = True
  except:
    print('Error adding bot to voice channel upon stop')

  voice_client = ctx.message.guild.voice_client

  try:
    if voice_client.is_playing():
      await voice_client.stop()
    else:
      try:
        await ctx.send("The bot is not playing anything at the moment.")
      except:
        print('Error stopping the stopped bot')
  except:
    print('Error stopping voice client')



@bot.command(name='hello', help='Says hello kinda')
async def hello(ctx):
  try:
    await ctx.send('Que fucko el needo')
  except:
    print('Error sending hello message')

@bot.command(name='insult', help='Generates insult via API')
async def insult(ctx, user=None):
  try:
    if(user == None):
      await ctx.send('Give me a target to shoot at slap nuts')
      return
  except:
    print('Error handling invalid/no user')
  
  msg = user + ', ' + Requests.get_insult()
  try:
    await ctx.send(msg)
  except:
    print('Error sending insult')

@bot.command(name='yo_momma', help='Generates yo momma joke via API')
async def mom_joke(ctx, user=None):
  try:
    if(user == None):
      await ctx.send('Give me a target to shoot at slap nuts')
      return
  except:
    print('Error handling invalid/no user')
    
  msg = user + ', ' + Requests.get_mom_joke()
  try:
    await ctx.send(msg)
  except:
    print('Error sending mom joke')

# @bot.event
# async def on_voice_state_update(member, before, after):
#   global bot
#   if not before.channel and after.channel:
#     greeting = f"Ting!"
#     msg = await member.guild.system_channel.send(greeting, tts=True)
#     await asyncio.sleep(6)
#     await msg.delete()



@bot.event
async def on_ready():
  print('We are logged in')

if __name__ == "__main__" :
  keep_alive()
  bot.run(os.environ['MHB_TOKEN'])