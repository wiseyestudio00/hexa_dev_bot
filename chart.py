import discord
from datetime import datetime
from pathlib import Path
from authorize import user_id_is_authorized


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

async def checkin(ctx, path):
    """
    Add all the attachments in ctx to the specified chart_library path.

    return a 2-Tuple (success_bool, error_message)
    """

    attachments = ctx.message.attachments

    if len(attachments) == 0:
        print("ERROR: User did not attach any file!")
        return False, "請附加譜面！"

    directory = Path(get_charts_path(path))

    if not directory.exists():
        if user_id_is_authorized(ctx.message.author.id):
            directory.mkdir(parents=True, exist_ok=True)
        else:
            print("ERROR: User-specified directory does not exist")
            return (False, "你不能新增檔案夾！")

    chart_file = attachments[0]

    if not is_in_chart_format(chart_file.filename):
        print("ERROR: File Name is not in Chart-Format")
        return False, "譜面的名字要是chart.[名字].txt！"
    
    content_bytes = await chart_file.read()
    chart_text = content_bytes.decode("utf-8")

    chart_path = Path(get_charts_path(f"{path}/{chart_file.filename}"))
    chart_path.write_text(chart_text)

    return True, f"{ctx.author.name}上傳了{chart_path}"


async def checkout(ctx, path):
    """ Send a list of Charts to Discord.
    Return (Operation_success_bool, Message). """

    target_path = Path(get_charts_path(path))

    if not target_path.exists():
        return False, "路徑不存在！"

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
        return False, "這個路徑沒有檔案"

    await ctx.send(files=charts)

    return True, f"成功取出{names}"


async def delete(ctx, path):
    path = Path(get_charts_path(path))

    if not path.exists():
        return False, "路徑不存在！"

    if path.is_file():
        path.unlink()
        return True, f"你刪除了{path}"

    # todo: if the user wants to delete a directory
    # only authroize user can do that
    if user_id_is_authorized(ctx.message.author.id):

        for child in path.glob('*'):
            if child.is_file():
                child.unlink()
            else:
                rm_tree(child)

        path.rmdir()

        return True, f"你刪除了{path}"
    else:

        return False, "你不能刪除檔案夾！"
