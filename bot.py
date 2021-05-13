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

CHECK_IN_HELP_TEXT = """
// 上傳譜面（如果已經上傳的會自動更新）\n.checkin 上傳路徑（要附加譜面檔案 chart.難度.txt）\n// 示範\n.checkin "v.1.0/journey's end/mellicious"（附加檔案：chart.easy.txt）
"""
@BOT.command(help=CHECK_IN_HELP_TEXT)
async def checkin(ctx, path):
    path = path.lower()
    if await chart.checkin(ctx, path):
        push_github(f"{datetime.datetime.now()}：{ctx.author.name} 上傳了 {path}")

CHECKOUT_HELP_TEXT = """
// 下載譜面（單個譜面）
.checkout 到譜面的路徑
// 示範
.checkout "v.1.0/journey's end/mellicious/chart.hard.txt"
"""
@BOT.command(help=CHECKOUT_HELP_TEXT)
async def checkout(ctx, path):
    path = path.lower()
    await chart.checkout(ctx, path)


DELETE_HELP_TEXT="""
// 刪除譜面
.delete 到譜面的路徑
// 示範
.delete "v.1.0/journey's end/mellicious/chart.hard.txt"
"""
@BOT.command(help=DELETE_HELP_TEXT)
async def delete(ctx, path):
    path = path.lower()
    if await chart.delete(ctx, path):
        push_github(f"{datetime.datetime.now()}：{ctx.author.name} 刪除了 {path}")


TREE_HELP_TEXT="""
// 查看路徑（全部的路徑）
.tree

// 查看路徑（指定哪個檔案夾）
.tree 檔案夾的路徑
// 示範（顯示v.1.0/journey's end裡所有的路徑）
.tree "v.1.0/journey's end"
"""
@BOT.command(help=TREE_HELP_TEXT)
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