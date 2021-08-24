import os
import json
import datetime
from pathlib import Path
from discord.ext import commands
import discord
import chart
import dev_song_uploader

from authorize import user_is_authorized
from tree import DisplayablePath

TOKEN = ""

with open("setting.json") as setting:
    text = setting.read()
    json_data = json.loads(text)
    TOKEN = json_data["token"]

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
        title="Hexa Hysteria譜面上傳處指令",
        color=discord.Color.blue())
    
    embd.add_field(
        name=".checkin 上傳路徑（要附加譜面檔案 chart.難度.txt）",
        value="""
        .checkin "v.1.0/journey's end/mellicious"\n（附加檔案：chart.easy.txt）
        """,
        inline=False)

    embd.add_field(
        name=".checkout 到譜面的路徑",
        value="""
        .checkout "v.1.0/journey's end/mellicious/chart.hard.txt"
        """,
        inline=False)

    embd.add_field(
        name=".checkout 到譜面檔案夾的路徑",
        value="""
        .checkout "v.1.0/journey's end/mellicious"
        """,
        inline=False)

    embd.add_field(
        name=".delete 到譜面的路徑",
        value="""
        .delete "v.1.0/journey's end/mellicious/chart.hard.txt"
        """,
        inline=False)

    embd.add_field(
        name=".tree",
        value="查看全部的路徑",
        inline=False)

    embd.add_field(
        name=".tree 檔案夾的路徑",
        value="""
        .tree "v.1.0/journey's end"
        """,
        inline=False)

    await ctx.send(embed=embd)



@BOT.command()
async def checkin(ctx, path):
    path = path.lower()
    if await chart.checkin(ctx, path):
        log = f"{datetime.datetime.now()}：{ctx.author.name} 更新 chart-library {path}\n"
        print(log)
        song_name = path.split("/")[-1]
        await add_to_dev_song(ctx, song_name)
        push_github(log)


@BOT.command()
async def checkout(ctx, path):
    path = path.lower()
    print(f"{ctx.author.name} asked for {path}")
    await chart.checkout(ctx, path)


@BOT.command()
async def delete(ctx, path):
    path = path.lower()
    if await chart.delete(ctx, path):
        log = f"{datetime.datetime.now()}：{ctx.author.name} 刪除 chart-library {path}\n"
        push_github(log)


@BOT.command()
async def add_to_dev_song(ctx, song_name):
    song_name = song_name.lower()

    if await dev_song_uploader.add_to_dev_songs(ctx, song_name):
        log = f"{datetime.datetime.now()}: {ctx.author.name} 更新 Dev-Songs的 {song_name}\n"
        push_github(log)


@BOT.command()
async def delete_from_dev_song(ctx, path):
    song_name = path.lower()

    if await dev_song_uploader.delete_from_dev_songs(ctx, path):
        log = f"{datetime.datetime.now()}: {ctx.author.name} 刪除 Dev-Songs的 {song_name}\n"
        push_github(log)


@BOT.command()
async def chart_library_tree(ctx, path=""):
    path = f"{os.getcwd()}/chart_library/{path}"

    for text in make_tree(path):
        await ctx.send(f"```\n{text}\n```")


@BOT.command()
async def dev_song_tree(ctx, path=""):
    path = f"{os.getcwd()}/dev_songs/{path}"

    for text in make_tree(path):
        await ctx.send(f"```\n{text}\n```")


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

    if not user_is_authorized(message.author.id) \
        and message.guild == None:
        await message.channel.send("你只能在伺服器裡使用我！")
        return

    await BOT.process_commands(message)


BOT.run(TOKEN)
