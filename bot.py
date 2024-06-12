import discord
from discord.ext import commands
import os
import random
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Путь к папке для сохранения музыкальных файлов
base_music_folder = 'music_files'
if not os.path.exists(base_music_folder):
    os.makedirs(base_music_folder)

# Текущий текстовый канал для загрузки файлов
current_text_channel_id = None
current_music_folder = None

async def download_mp3_files_from_channel(channel):
    global current_music_folder
    async for message in channel.history(limit=1000):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.endswith('.mp3'):
                    filepath = os.path.join(current_music_folder, attachment.filename)
                    if not os.path.exists(filepath):
                        await attachment.save(filepath)
                        await channel.send(f'Saved {attachment.filename}')

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

@bot.event
async def on_message(message):
    global current_text_channel_id, current_music_folder
    if message.author == bot.user:
        return
    
    if message.channel.id == current_text_channel_id and message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith('.mp3'):
                filepath = os.path.join(current_music_folder, attachment.filename)
                if not os.path.exists(filepath):
                    await attachment.save(filepath)
                    await message.channel.send(f'Saved {attachment.filename}')
                
    await bot.process_commands(message)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send(f'Joined {channel.name}')
        else:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f'Moved to {channel.name}')
    else:
        await ctx.send('You need to be in a voice channel to use this command.')

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected from the voice channel')
    else:
        await ctx.send('I am not in a voice channel.')

@bot.command()
async def playmusic(ctx):
    if ctx.voice_client:
        files = [f for f in os.listdir(current_music_folder) if f.endswith('.mp3')]
        if not files:
            await ctx.send(f'No music files found in the specified folder for channel {ctx.guild.get_channel(current_text_channel_id).name}.')
            return

        await ctx.send('Starting music playback...')
        while files:
            random_file = random.choice(files)
            source = discord.FFmpegPCMAudio(os.path.join(current_music_folder, random_file))
            ctx.voice_client.play(source)
            
            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)
                
            files = [f for f in os.listdir(current_music_folder) if f.endswith('.mp3')]
    else:
        await ctx.send('I need to be in a voice channel to play music. Use !join to invite me.')

@bot.command()
async def setchannel(ctx):
    global current_text_channel_id, current_music_folder
    current_text_channel_id = ctx.channel.id
    current_music_folder = os.path.join(base_music_folder, str(current_text_channel_id))
    if not os.path.exists(current_music_folder):
        os.makedirs(current_music_folder)
    await download_mp3_files_from_channel(ctx.channel)
    await ctx.send(f'Set the current channel to {ctx.channel.name} for downloading mp3 files and downloaded all existing mp3 files.')

@bot.command(name='commands')
async def _commands(ctx):
    help_text = """
    **Available Commands:**
    `!join` - Join the voice channel you are in.
    `!leave` - Leave the voice channel.
    `!playmusic` - Start playing random music from the saved files.
    `!setchannel` - Set the current channel for downloading mp3 files and download all existing mp3 files.
    `!commands` - Show this help message.
    """
    await ctx.send(help_text)

# Ваш токен бота
TOKEN = ''

bot.run(TOKEN)
