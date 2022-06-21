import os
import json
import datetime
from pathlib import Path
from discord import message
from discord.ext import commands
import discord
import chart
import dev_song_uploader

from authorize import user_id_is_authorized
from tree import DisplayablePath

TOKEN = ""

# Load in setting
with open("setting.json") as setting:
    text = setting.read()
    json_data = json.loads(text)
    TOKEN = json_data["token"]

# Bot instance is created here.
BOT = commands.Bot(".", help_command=None)


def push_github(commit_message):
    with open("log.txt", "a") as log:
        log.write(commit_message)

    os.system("git pull")
    os.system("git add .")
    os.system(f"git commit -m \"{commit_message}\"")
    os.system("git push")


@BOT.command()
async def help(ctx):
    embd = discord.Embed(
        title = "Hexa Hysteria譜面上傳處指令表",
        color = discord.Color.blue())
    
    embd.add_field(
        name = ".checkin 上傳路徑（要附加譜面檔案，名稱為chart.難度.txt）",
        value = """
        將譜面上傳到譜面資料庫，並且更新Dev-Song。

        例：.checkin "v.1.0/journey's end/mellicious"\n（附加檔案：chart.easy.txt）
        """,
        inline = False)

    embd.add_field(
        name = ".checkout 到譜面的路徑",
        value = """
        將譜面從譜面資料庫提出。

        例：.checkout "v.1.0/journey's end/mellicious/chart.hard.txt"
        """,
        inline = False)

    embd.add_field(
        name = ".checkout 到譜面檔案夾的路徑",
        value = """
        將全部的譜面從譜面資料庫中的檔案夾提出。

        例：.checkout "v.1.0/journey's end/mellicious"
        """,
        inline = False)

    embd.add_field(
        name = ".delete 到譜面的路徑",
        value = """
        刪除譜面資料庫的譜面。

        例：.delete "v.1.0/journey's end/mellicious/chart.hard.txt"
        """,
        inline=False)

    embd.add_field(
        name = ".chart_library_tree",
        value = """
        查看譜面資料庫的所有路徑。
        """,
        inline = False
    )

    embd.add_field(
        name = ".chart_library_tree 路徑",
        value="""
        查看譜面資料庫特定的路徑。
        """,
        inline=False
    )

    embd.add_field(
        name = ".add_to_dev_song 歌曲名稱 (需要附加檔案，可以是任何檔案)",
        value = """
        將檔案上傳到Dev-Songs。

        只有有權限的人才可以使用。

        例：.add_to_dev_song 歌曲名稱 （附加檔案：audio.ogg）
        """,
        inline=False
    )

    embd.add_field(
        name=".delete_from_dev_song 檔案路徑",
        value="""
        將Dev-Song的檔案刪除。

        只有有權限的人才可以使用。

        例：.add_to_dev_song blue/chart.hard.txt
        """,
        inline=False
    )

    await ctx.send(embed=embd)


def get_success_embed(description):
    return discord.Embed(
        title="成功",
        description=description,
        color=discord.Color.blue())


def get_fail_embed(description):
    return discord.Embed(
        title="失敗",
        description=description,
        color=discord.Color.red())


@BOT.command()
async def checkin(ctx, path):
    path = path.lower()

    success, message = await chart.checkin(ctx, path)

    embed = get_success_embed(message) if success else get_fail_embed(message)
    await ctx.send(embed=embed)

    if success:
        log = f"{datetime.datetime.now()}：{ctx.author.name} 更新 chart-library {path}\n"
        print(log)
        song_name = path.split("/")[-1]
        await add_to_dev_song_skip_authorize(ctx, song_name)
        push_github(log)


@BOT.command()
async def checkout(ctx, path):
    path = path.lower()

    success, message = await chart.checkout(ctx, path)

    embed = get_success_embed(message) if success else get_fail_embed(message)
    await ctx.send(embed=embed)

    print(f"{ctx.author.name} asked for {path}")


@BOT.command()
async def delete(ctx, path):
    path = path.lower()
    
    success, message = await chart.delete(ctx, path)

    embed = get_success_embed(message) if success else get_fail_embed(message)
    await ctx.send(embed=embed)

    if success:
        log = f"{datetime.datetime.now()}：{ctx.author.name} 刪除 chart-library {path}\n"
        push_github(log)


@BOT.command()
async def add_to_dev_song(ctx, song_name):
    song_name = song_name.lower()

    success, message = await dev_song_uploader.add_to_dev_songs(ctx, song_name)

    embed = get_success_embed(message) if success else get_fail_embed(message)
    await ctx.send(embed=embed)

    if success:
        log = f"{datetime.datetime.now()}: {ctx.author.name} 更新 Dev-Songs的 {song_name}\n"
        push_github(log)


async def add_to_dev_song_skip_authorize(ctx, song_name):
    song_name = song_name.lower()

    success, message = await dev_song_uploader.add_to_dev_song_skip_authorize(ctx, song_name)

    embed = get_success_embed(message) if success else get_fail_embed(message)
    await ctx.send(embed=embed)

    if success:
        log = f"{datetime.datetime.now()}: {ctx.author.name} 更新 Dev-Songs的 {song_name}\n"
        push_github(log)


@BOT.command()
async def delete_from_dev_song(ctx, path):
    success, message = await dev_song_uploader.delete_from_dev_songs(ctx, path)

    embed = get_success_embed(message) if success else get_fail_embed(message)
    await ctx.send(embed=embed)

    if success:
        song_name = path.lower()
        log = f"{datetime.datetime.now()}: {ctx.author.name} 刪除 Dev-Songs的 {song_name}\n"
        push_github(log)


@BOT.command()
async def chart_library_tree(ctx, path = ""):
    path = f"{os.getcwd()}/chart_library/{path}"        

    for text in make_tree(path):
        await ctx.send(f"```\n{text}\n```")


@BOT.command()
async def dev_song_tree(ctx, path = ""):
    """
    Send the Tree of the Dev-Song directory to the channel which calls command.
    """

    path = f"{os.getcwd()}/dev_songs/{path}"

    for text in make_tree(path):
        await ctx.send(f"```\n{text}\n```")


async def tester_report(ctx, ):
    """
    The testers report either a suggestion or a bug through this command.
    """


def make_tree(path):
    path = path.lower()
    paths = DisplayablePath.make_tree(Path(path))

    result = []

    text = ""

    for path in paths:
        # Discord can not send message of over 2000 characters.
        if len(text) > 1800:
            result.append(text)
            text = ""
        text += path.displayable() + "\n"

    result.append(text)

    return result


@BOT.event
async def on_message(message):
    if message.author.id == BOT.user.id:
        return

    if not user_id_is_authorized(message.author.id) \
        and message.guild == None:
        await message.channel.send("你只能在伺服器裡使用我！")
        return

    await BOT.process_commands(message)


BOT.run(TOKEN)
