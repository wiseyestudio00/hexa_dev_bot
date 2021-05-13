import os
import json
from pathlib import Path
from discord.ext import commands
import discord
import chart

BOT = commands.Bot("/")

@BOT.command(help="Check in a chart.")
async def checkin(ctx, path):
    await chart.checkin(ctx, path)

    os.system("git add .")
    os.system(f"git commit -m \"added {path}\"")
    os.system("git push")

    with open("log.txt", "a") as log:
        log.write(f"{ctx.author.name}上傳了{path}")


@BOT.command()
async def checkout(ctx, path):
    await chart.checkout(ctx, path)


@BOT.command(help="View the files")
async def tree(ctx, path=None):
    def list_files(startpath):
        result = ""
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            result += f'{indent}{os.path.basename(root)}/\n'
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if f.startswith("."):
                    continue
                result += f"{subindent}{f}\n"
        return result
    
    if path is None:
        path = ""

    text = list_files(f"{os.getcwd()}/charts/{path}")
    
    if text == "":
        await ctx.send("這個路徑沒有譜面！")
        return

    await ctx.send(f"```\n{text}\n```")

@BOT.command(help="delete the path")
async def delete(ctx, path):
    pass


@BOT.event
async def on_message(message):
    await BOT.process_commands(message)


with open("setting.json") as setting:
    text = setting.read()
    json_data = json.loads(text)
    token = json_data["token"]
    BOT.run(token)