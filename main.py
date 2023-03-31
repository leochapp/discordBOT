import os

import pymysql as MySQLdb
import discord
from discord.ext import commands
import youtube_dl
import asyncio
import random
from youtube_search import YoutubeSearch
from discord.utils import get
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


#Import des informations de connexions
token = os.environ['TOKEN']
host = os.environ['HOST']
username = os.environ['USER']
password = os.environ['PASSWORD']
db2 = os.environ['DATABASE']
superadmin = os.environ['SUPERADMIN']   # Les supersadmins sont écris en dur dans le code pour être certain d'avoir toujours tous les droits.


# Connexion du BOT :

intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents, description="Bot cool fait entre pote avec amour et tendresse")
intents.members = True
intents.message_content = True
help_command = commands.DefaultHelpCommand(no_category = 'Commands')

@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user} ! ")






# BOT MUSIQUE DEPUIS YOUTUBE
#========================================================================================================================================================#
ydl_opts = {
    'format': 'beataudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
}
ytdl = youtube_dl.YoutubeDL(ydl_opts)



musics = {}

class Video:
    def __init__(self, url):
        self.video = ytdl.extract_info(url, download=False)
        self.video_format = self.video["formats"][0]
        self.url = self.video["webpage_url"]
        self.stream_url = self.video_format["url"]
        self.repeat = 0


def play_song(clientg,queue ,song):
    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(song.stream_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
    )

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(clientg, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(clientg.disconnect(), client.loop)

    clientg.play(source, after=next)



@client.command()
async def play(ctx, *args):
    print('play')

    clientg = ctx.guild.voice_client


    if ctx.message.author.voice == None:
        await ctx.send(f" You have to be in a voice channel to command the music BOT {ctx.message.author.mention}")


    verif_music = 0

    if "www.youtube.com" in args[0]:
        url = args[0]
    else:
        search = " ".join(args)
        yt = YoutubeSearch(search, max_results=1).to_dict()
        url_suffix = yt[0]['url_suffix']
        url = "https://www.youtube.com"+url_suffix
        verif_music = 1


    if clientg and clientg.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
        await ctx.message.add_reaction('✅')
    else:
        # Si connecté à un channel.
        channel = ctx.author.voice.channel

        video = Video(url)
        musics[ctx.guild] = []

        clientg = await channel.connect()
        play_song(clientg, musics[ctx.guild], video)

        nbrandom =random.randint(1,10)
        emojis = ['✅', '👍', '🍆']
        nb2 = random.randint(1,3) -1
        if nbrandom == 9:
            await ctx.send(f" Musique de PD lancée pour {ctx.message.author.mention}")
        else:
            await ctx.message.add_reaction(emojis[nb2])

        if verif_music == 1:
            await ctx.send(f"La musique lancée est {url} ")

    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()

    user = get(client.get_all_members(), id= ctx.message.author.id)
    server = ctx.message.guild.name
    parameters = (None,url,user,server)
    query = "INSERT INTO datamusic VALUES(%s,%s,%s,%s)"

    cursor.execute(query, parameters)
    db.commit()
    db.close()



@client.command()
async def skip(ctx):
    clientg = ctx.guild.voice_client
    clientg.stop()
    await ctx.message.add_reaction('✅')


@client.command()
async def pause(ctx):
    clientg = ctx.guild.voice_client
    if not clientg.is_paused():
        clientg.pause()

@client.command()
async def resume(ctx):
    clientg = ctx.guild.voice_client
    if clientg.is_paused():
        clientg.resume()

@client.command()
async def disconnect(ctx):
    server = ctx.message.guild.name
    admins_uid = getdata('admins', server,1)
    bot_channel = ctx.guild.voice_client
    uid = ctx.message.author.id
    if (uid in admins_uid) or (uid in superadmin):
        await bot_channel.disconnect()
        musics[ctx.guild] = []
        await ctx.message.add_reaction('✅')
    else:

        if ctx.author.voice.channel == ctx.voice_client.channel:
            await bot_channel.disconnect()
            musics[ctx.guild] = []
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send('You have to be connected to the same voice channel to disconnect the BOT .\n Ptit PD')


@client.command()
async def clear(ctx):
    server = ctx.message.guild.name
    admins_uid = getdata(1,'admins',server)
    uid = ctx.message.author.id
    if (uid in admins_uid) or (uid in superadmin):
        musics[ctx.guild].clear()
        await ctx.message.add_reaction('✅')
    else:
        if ctx.author.voice.channel == ctx.voice_client.channel:
            musics[ctx.guild].clear()
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send('You have to be connected to the same voice channel to disconnect the BOT.\n Gros PD')

@client.command()
async def queue(ctx):

    if len(musics[ctx.guild]) > 0:

        embed = discord.Embed(
            title="Queue List",
            url="",
            description="Here are the musics that will be played next :",
            color=discord.Color.blue())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.message.author.avatar)

        embed.set_thumbnail(url=musics[ctx.guild][0])
        url = musics[ctx.guild][0].url
        yt = YoutubeSearch(url, max_results=1).to_dict()
        thbnail = yt[0]['thumbnails'][0]
        embed.set_thumbnail(url=thbnail)


        i = 1
        for video in musics[ctx.guild]:
            url = video.url
            yt = YoutubeSearch(url, max_results=1).to_dict()
            title = yt[0]['title']
            channel = yt[0]['channel']
            publish = yt[0]['publish_time']
            duration = yt[0]['duration']
            embed.add_field(name=f"**{i}**", value=f"**{title}** - {duration} | {channel}  {url}", inline=False)
            i+=1

        embed.set_footer(text="La biz de Léo")
    else:
        embed = discord.Embed(
            title="Queue List",
            url="",
            description="No song in the queue",
            color=discord.Color.blue())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.message.author.avatar)
        embed.set_thumbnail(url="https://lchappuis.fr/chien.jpg")
        embed.set_footer(text="La biz de Léo")


    await ctx.send(embed=embed)


@client.command()
async def last(ctx):
    clientg = ctx.guild.voice_client
    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()

    server = ctx.message.guild.name
    parameters = (server)
    query = "SELECT link FROM datamusic WHERE id = (SELECT MAX(id) FROM datamusic WHERE server=%s)"

    cursor.execute(query, parameters)
    url = cursor.fetchone()[0]


    if clientg and clientg.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
        await ctx.message.add_reaction('✅')
    else:
        # Si connecté à un channel.
        channel = ctx.author.voice.channel

        video = Video(url)
        musics[ctx.guild] = []

        clientg = await channel.connect()
        play_song(clientg, musics[ctx.guild], video)

        emojis = '✅'
        await ctx.message.add_reaction(emojis)
        await ctx.send(f"La musique lancée est {url} ")




    db.close()

@client.command()
async def p(ctx, *args):
    await play(ctx, *args)

@client.command()
async def r(ctx):
    await resume(ctx)

@client.command()
async def s(ctx):
    await skip(ctx)

@client.command()
async def d(ctx):
    await disconnect(ctx)

@client.command()
async def q(ctx):
    await queue(ctx)

@client.command()
async def quit(ctx):
    await disconnect(ctx)




# Quelques fonctions qui serveront plusieurs fois :

def getdata(table,serv, active):
    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()
    parameters = (active, serv)
    query = f"SELECT uid FROM {table} WHERE isactive = %s AND servername = %s"
    cursor.execute(query, parameters)
    tab = cursor.fetchall()
    data = []
    for tup in tab:
        data.append(tup[0])
    db.close()
    return data






# Fonctions qui servaient à lire les phrases du BOT troll

def readphrases():
    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()
    query = "SELECT phrase.value FROM phrase;"
    cursor.execute(query)
    tab = cursor.fetchall()
    data = []
    for tup in tab:
        data.append(tup[0])
    db.close()
    return data


def readphraseshard():
    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()
    query = "SELECT phrasehard.value FROM phrasehard;"
    cursor.execute(query)
    tab = cursor.fetchall()
    data = []
    for tup in tab:
        data.append(tup[0])
    db.close()
    return data






client.run(token)
