import os
import json
from datetime import datetime
from pathlib import Path
from discord.utils import get
from discord.ext import commands
import arrow
import discord
from tree import tree

BOT = commands.Bot("/")


def is_in_chart_format(filename):
    splited = filename.split(".")

    if len(splited) != 3 \
        or splited[0] != "chart" \
        or splited[2] != "txt":
        return False
    
    return True


def get_checkin_emded(description):
    result = discord.Embed(
        title="譜面上傳成功！",
        description=description,
        color=discord.Color.blue())
    result.set_footer(text=str(datetime.now()))
    return result


@BOT.command(help="Check in a chart.")
async def checkin(ctx, path):
    if ctx.message.channel:
        # todo: return message
        pass
    
    attachments = ctx.message.attachments

    if len(attachments) > 1 or len(attachments) == 0:
        pass
        # todo: say it's not allowed

    chart_file = attachments[0]

    if not is_in_chart_format(chart_file.filename):
        pass
        # todo: say it's not allowed
    
    content_bytes = await chart_file.read()
    chart_text = content_bytes.decode("utf-8")

    directory = Path(f"{path}")
    directory.mkdir(parents=True, exist_ok=True)
    path = Path(f"{path}/{chart_file.filename}")
    path.write_text(chart_text)

    embed = get_checkin_emded(
        f"{ctx.author.name}上傳了{path}")

    await ctx.send(embed=embed)


@BOT.command(help="View the files")
async def tree(ctx):
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

    print(list_files(f"{os.getcwd()}/charts"))


@BOT.command(help="delete a file")
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