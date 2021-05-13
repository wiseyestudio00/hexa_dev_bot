import discord
from datetime import datetime
from pathlib import Path


def get_charts_path(path):
    return f"charts/{path}"


def is_in_chart_format(filename):
    splited = filename.split(".")
    if len(splited) != 3 \
        or splited[0] != "chart" \
        or splited[2] != "txt":
        return False
    return True


def get_checkout_success_embed(description):
    result = discord.Embed(
        title="譜面上傳成功！",
        description=description,
        color=discord.Color.blue())
    result.set_footer(text=str(datetime.now()))
    return result


def get_checkout_fail_embed(description):
    result = discord.Embed(
        title="譜面上傳失敗",
        description=description,
        color=discord.Color.red())
    result.set_footer(text=str(datetime.now()))
    return result


async def checkin(ctx, path):
    if ctx.message.channel:
        # todo: return message
        pass
    
    attachments = ctx.message.attachments

    if len(attachments) == 0:
        emb = get_checkout_fail_embed("請附加譜面！")
        await ctx.send(embed=emb)
        return

    chart_file = attachments[0]

    if not is_in_chart_format(chart_file.filename):
        emb = get_checkout_fail_embed("譜面的名字要是chart.[名字].txt！")
        await ctx.send(embed=emb)
        return
    
    content_bytes = await chart_file.read()
    chart_text = content_bytes.decode("utf-8")

    directory = Path(get_charts_path(path))
    directory.mkdir(parents=True, exist_ok=True)
    path = Path(get_charts_path(f"{path}/{chart_file.filename}"))
    path.write_text(chart_text)

    success_embed = get_checkout_success_embed(
        f"{ctx.author.name}上傳了{path}")

    await ctx.send(embed=success_embed)


def get_checkout_success_embed(description):
    return discord.Embed(
        title="取出成功！",
        description=description,
        color=discord.Color.blue())


def get_checkout_fail_embed(description):
    return discord.Embed(
        title="取出失敗！",
        description=description,
        color=discord.Color.red())


async def checkout(ctx, path):
    target_path = Path(get_charts_path(path))

    if not target_path.exists():
        emb = get_checkout_fail_embed("路徑不存在！")
        await ctx.send(embed=emb)
        return

    charts = []
    names = ""

    if target_path.is_file():
        with open(target_path) as chart:
            names += chart.name + "\n"
            charts.append(discord.File(
                chart,
                filename=chart.name.replace(str(target_path), "")))
    
    if target_path.is_dir():
        for c in target_path.glob("chart.*.txt"):
            with open(c) as chart:
                names += chart.name + "\n"
                charts.append(discord.File(
                    chart,
                    filename=chart.name.replace(str(target_path), "")))

    success_emb = get_checkout_success_embed(names)
    await ctx.send(files=charts, embed=success_emb)