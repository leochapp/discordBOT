import asyncio
import random

import discord
from discord.ext import commands
from pytube import YouTube
from youtube_search import YoutubeSearch
from db import *

superadmin = os.environ['SUPERADMIN']


class Video:
    def __init__(self, url):
        self.url = url
        self.video = YouTube(url)
        self.stream = self.video.streams.filter(only_audio=True).order_by('abr').desc().first()
        self.repeat = 0

    @property
    def stream_url(self):
        return self.stream.url


class MusicBOT(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.musics = {}

    @commands.command()
    async def play(self, ctx, *args):
        print('play')
        clientg = ctx.guild.voice_client
        if ctx.message.author.voice is None:
            await ctx.send(f"You have to be in a voice channel to command the music BOT {ctx.message.author.mention}")
            return

        verif_music = 0

        if "www.youtube.com" in args[0]:
            url = args[0]
        else:
            search = " ".join(args)
            yt = YoutubeSearch(search, max_results=1).to_dict()
            url_suffix = yt[0]['url_suffix']
            url = "https://www.youtube.com" + url_suffix
            verif_music = 1

        if clientg and clientg.channel:
            video = Video(url)
            self.musics[ctx.guild].append(video)
            await ctx.message.add_reaction('✅')
        else:
            channel = ctx.author.voice.channel
            video = Video(url)
            self.musics[ctx.guild] = []
            clientg = await channel.connect()
            self.play_song(clientg, self.musics[ctx.guild], video)

            nbrandom = random.randint(1, 10)
            emojis = ['✅', '👍', '🍆']
            nb2 = random.randint(1, 3) - 1
            if nbrandom == 9:
                await ctx.send(f"Musique de PD lancée pour {ctx.message.author.mention}")
            else:
                await ctx.message.add_reaction(emojis[nb2])

            if verif_music == 1:
                await ctx.send(f"La musique lancée est {url}")

        user = ctx.author
        server = ctx.message.guild.id
        add_music_palyed(url, user.id, server)

    def play_song(self, clientg, queue, song):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            song.stream_url, executable="./ffmpeg/bin/ffmpeg.exe",
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

        def next(_):
            if len(queue) > 0:
                new_song = queue[0]
                del queue[0]
                self.play_song(clientg, queue, new_song)
            else:
                asyncio.run_coroutine_threadsafe(clientg.disconnect(), self.client.loop)

        clientg.play(source, after=next)

    @commands.command()
    async def p(self, ctx, *args):
        await self.play(ctx, *args)

    @commands.command()
    async def skip(self, ctx):
        clientg = ctx.guild.voice_client
        clientg.stop()
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def s(self, ctx):
        await self.skip(ctx)

    @commands.command()
    async def pause(self, ctx):
        clientg = ctx.guild.voice_client
        if not clientg.is_paused():
            clientg.pause()

    @commands.command()
    async def resume(self, ctx):
        clientg = ctx.guild.voice_client
        if clientg.is_paused():
            clientg.resume()

    @commands.command()
    async def r(self, ctx):
        await self.resume(ctx)

    @commands.command()
    async def clear(self, ctx):
        server = ctx.message.guild.name
        admins_uid = getdata(1, 'admins', server)
        uid = ctx.message.author.id
        if (uid in admins_uid) or (uid in superadmin):
            self.musics[ctx.guild].clear()
            await ctx.message.add_reaction('✅')
        else:
            if ctx.author.voice.channel == ctx.voice_client.channel:
                self.musics[ctx.guild].clear()
                await ctx.message.add_reaction('✅')
            else:
                await ctx.send('You have to be connected to the same voice channel to disconnect the BOT.\n Gros PD')

    @commands.command()
    async def queue(self, ctx):

        if len(self.musics[ctx.guild]) > 0:

            embed = discord.Embed(
                title="Queue List",
                url="",
                description="Here are the musics that will be played next :",
                color=discord.Color.blue())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.message.author.avatar)

            embed.set_thumbnail(url=self.musics[ctx.guild][0])
            url = self.musics[ctx.guild][0].url
            yt = YoutubeSearch(url, max_results=1).to_dict()
            thbnail = yt[0]['thumbnails'][0]
            embed.set_thumbnail(url=thbnail)

            i = 1
            for video in self.musics[ctx.guild]:
                url = video.url
                yt = YoutubeSearch(url, max_results=1).to_dict()
                title = yt[0]['title']
                channel = yt[0]['channel']
                publish = yt[0]['publish_time']
                duration = yt[0]['duration']
                embed.add_field(name=f"**{i}**", value=f"**{title}** - {duration} | {channel}  {url}", inline=False)
                i += 1

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

    @commands.command()
    async def q(self, ctx):
        await self.queue(ctx)

    @commands.command()
    async def disconnect(self, ctx):
        bot = ctx.voice_client
        server = ctx.message.guild.id
        bot_channel = bot.channel
        user_channel = ctx.author.voice.channel
        uid = ctx.message.author.id

        print(getdata('admin', server), superadmin)

        if (uid in getdata('admin', server)) or (uid in superadmin):
            await bot.disconnect()
            self.musics[ctx.guild] = []
            await ctx.message.add_reaction('✅')
        else:
            if user_channel == bot_channel:
                await bot.disconnect()
                self.musics[ctx.guild] = []
                await ctx.message.add_reaction('✅')
            else:
                await ctx.send('You have to be connected to the same voice channel to disconnect the BOT .\n Ptit PD')

    @commands.command()
    async def d(self, ctx):
        await self.disconnect(ctx)

    @commands.command()
    async def quit(self, ctx):
        await self.disconnect(ctx)

# il faut écrire la partie db pour la commande last

# @client.command()
# async def last(ctx):
#     clientg = ctx.guild.voice_client
#     db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
#     cursor = db.cursor()
#
#     server = ctx.message.guild.name
#     parameters = (server)
#     query = "SELECT link FROM datamusic WHERE id = (SELECT MAX(id) FROM datamusic WHERE server=%s)"
#
#     cursor.execute(query, parameters)
#     url = cursor.fetchone()[0]


# if clientg and clientg.channel:
#     video = Video(url)
#     musics[ctx.guild].append(video)
#     await ctx.message.add_reaction('✅')
# else:
#     # Si connecté à un channel.
#     channel = ctx.author.voice.channel
#
#     video = Video(url)
#     musics[ctx.guild] = []
#
#     clientg = await channel.connect()
#     play_song(clientg, musics[ctx.guild], video)
#
#     emojis = '✅'
#     await ctx.message.add_reaction(emojis)
#     await ctx.send(f"La musique lancée est {url} ")
# db.close()
