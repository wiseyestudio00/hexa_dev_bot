import discord
from datetime import datetime
from pathlib import Path
from authorize import user_is_authorized


def get_charts_path(path):
    """ Return "chart_library/{path}" """

    return f"chart_library/{path}"


def is_in_chart_format(filename):
    """ Check if the filename is in the format of chart.name.txt """

    splited = filename.split(".")

    if len(splited) != 3 \
        or splited[0] != "chart" \
        or splited[2] != "txt":
        return False
    
    return True


def get_checkin_success_embed(description):
    """ Return an Discord Embed with Blue Background. """
    result = discord.Embed(
        title="譜面上傳成功！",
        description=description,
        color=discord.Color.blue())

    result.set_footer(text=str(datetime.now()))

    return result


def get_checkin_fail_embed(description):
    """ Return an Discord Embed with Red Background. """

    result = discord.Embed(
        title="譜面上傳失敗",
        description=description,
        color=discord.Color.red())

    result.set_footer(text=str(datetime.now()))

    return result


async def checkin(ctx, path):
    """
    Add all the attachments in ctx to the specified chart_library path.
    Return False if the function encountered an error. Else return true.
    """

    attachments = ctx.message.attachments

    if len(attachments) == 0:
        print("ERROR: User did not attach any file!")

        emb = get_checkin_fail_embed("請附加譜面！")
        await ctx.send(embed=emb)
        return False

    directory = Path(get_charts_path(path))

    if not directory.exists():
        if user_is_authorized(ctx.message.author.id):
            directory.mkdir(parents=True, exist_ok=True)
        else:
            print("ERROR: User-specified directory does not exist")
            
            fail_emb = get_checkin_fail_embed("你不能新增檔案夾！")
            await ctx.send(embed = fail_emb)
            return False    

    for chart_file in attachments:
        if not is_in_chart_format(chart_file.filename):
            print("ERROR: File Name is not in Chart-Format")

            emb = get_checkin_fail_embed("譜面的名字要是chart.[名字].txt！")
            await ctx.send(embed=emb)
            return False
        
        content_bytes = await chart_file.read()
        chart_text = content_bytes.decode("utf-8")
    
        chart_path = Path(get_charts_path(f"{path}/{chart_file.filename}"))
        chart_path.write_text(chart_text)

        success_embed = get_checkin_success_embed(
            f"{ctx.author.name}上傳了{chart_path}")

        await ctx.send(embed=success_embed)

    return True


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
    """ Send a list of Charts to Discord. Return False if the operation fails. """

    target_path = Path(get_charts_path(path))

    if not target_path.exists():
        emb = get_checkout_fail_embed("路徑不存在！")
        await ctx.send(embed=emb)
        return False

    charts = []
    names = ""

    if target_path.is_file():
        with open(target_path, "rb") as chart:
            names += chart.name + "\n"
            splited = chart.name.split("/")
            filename = splited[len(splited) - 1]
            charts.append(discord.File(
                chart,
                filename=filename))

    elif target_path.is_dir():
        for c in target_path.glob("chart.*.txt"):
            with open(c, "rb") as chart:
                names += chart.name + "\n"
                charts.append(discord.File(
                    chart,
                    filename=chart.name.replace(str(target_path) + "/", "")))

    if len(charts) == 0:
        fail_emb = get_checkout_fail_embed("這個路徑裡沒有檔案")
        await ctx.send(embed=fail_emb)
        return False

    for c in charts:
        print(c.filename)

    success_emb = get_checkout_success_embed(names)
    await ctx.send(files=charts, embed=success_emb)
    return True


def get_delete_success_emb(description):
    return discord.Embed(
        title="刪除成功！",
        description=description,
        color=discord.Color.blue())


def get_delete_fail_emb(description):
    return discord.Embed(
        title="刪除失敗！",
        description=description,
        color=discord.Color.red())


async def delete(ctx, path):
    path = Path(get_charts_path(path))

    if not path.exists():
        fail_emb = get_delete_fail_emb("路徑不存在！")
        await ctx.send(embed=fail_emb)
        return False

    if path.is_file():
        path.unlink()
        success_emb = get_delete_success_emb(f"你刪除了{path}")
        await ctx.send(embed=success_emb)
        return False

    # todo: if the user wants to delete a directory
    # only authroize user can do that
    if user_is_authorized(ctx.message.author.id):

        for child in path.glob('*'):
            if child.is_file():
                child.unlink()
            else:
                rm_tree(child)

        path.rmdir()

        success_emb = get_delete_success_emb(f"你刪除了{path}")
        await ctx.send(embed=success_emb)
        return True
    else:
        fail_emb = get_delete_fail_emb("你不能刪除檔案夾！")
        await ctx.send(embed=fail_emb)
        return False
