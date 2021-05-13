import os
import json
import datetime
from pathlib import Path
from discord.ext import commands
import discord
import chart

from authorize import user_is_authorized
from tree import DisplayablePath


def push_github(commit_message):
    with open("log.txt", "a") as log:
        log.write(commit_message)
    os.system("git add .")
    os.system(f"git commit -m \"{commit_message}\"")
    os.system("git push")


TOKEN = ""

with open("setting.json") as setting:
    text = setting.read()
    json_data = json.loads(text)
    TOKEN = json_data["token"]

BOT = commands.Bot(".")


@BOT.command(help="Check in a chart.")
async def checkin(ctx, path):
    path = path.lower()
    if await chart.checkin(ctx, path):
        push_github(f"{datetime.datetime.now()}：{ctx.author.name} 上傳了 {path}")


@BOT.command()
async def checkout(ctx, path):
    path = path.lower()
    await chart.checkout(ctx, path)


@BOT.command(help="delete the path")
async def delete(ctx, path):
    path = path.lower()
    if await chart.delete(ctx, path):
        push_github(f"{datetime.datetime.now()}：{ctx.author.name} 刪除了 {path}")


@BOT.command(help="View the files")
async def tree(ctx, path=""):
    path = path.lower()
    paths = DisplayablePath.make_tree(Path(f"{os.getcwd()}/charts/{path}"))
    
    """
    if len(paths) == 0:
        await ctx.send("這個路徑沒有譜面！")
        return
    """
    text = ""

    for path in paths:
        text += path.displayable() + "\n"

    await ctx.send(f"```\n{text}\n```")


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