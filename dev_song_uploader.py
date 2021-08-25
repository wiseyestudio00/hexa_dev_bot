from os import path
import pathlib
import discord
from datetime import datetime
from pathlib import Path
from discord import widget

from discord.file import File
from authorize import user_is_authorized
from authorize import context_sender_is_authorized
from generate_index import generate_dev_songs_catalog


def get_dev_song_path(file_path):
    """ return dev_songs/file_path"""
    return f"dev_songs/{file_path}"


async def add_to_dev_songs(ctx, song_name):
    """
    Exposed method for Discord Bot Command.

    Add all the attachments to the specified path in Dev-Songs. Update Catalog. 
    """

    if not context_sender_is_authorized(ctx):
        return False, "上傳者無權限更改Dev-Song。"

    attachments = ctx.message.attachments

    if len(attachments) == 0:
        return False, "沒有附加檔案"

    file = attachments[0]

    file_name = file.filename
    content_bytes = await file.read()

    return add_to_dev_songs_helper(content_bytes, song_name, file_name)


def add_to_dev_songs_helper(byte_array, song_name, file_name):
    """
    Write the byte_array to the song_name in dev_songs (f"dev_songs/{song_name}").
    Then, update the catalog.

    Return true if all the process are successful, else return false.
    Ps. Will always return True at this current implementation. 
    """

    song_directory = Path(get_dev_song_path(song_name))

    if not song_directory.exists():
        print("A Dev-Song directoy was made. May need to supply fo Song-Info.")
        song_directory.mkdir(parents=True, exist_ok=True)
    
    chart_path = Path(get_dev_song_path(f"{song_name}/{file_name}"))

    if not chart_path.exists():
        chart_path.touch(exist_ok=True)

    chart_path.write_bytes(byte_array);        

    generate_dev_songs_catalog()

    return True, f"成功上傳{song_name} - {file_name}"


async def delete_from_dev_songs(ctx, path):
    """
    Exposed method for Discord Bot Command.
    
    Delete the specified file from dev-Songs.
    """

    if not context_sender_is_authorized(ctx):
        return False, "上傳者無權限更改Dev-Song。"

    return delete_from_dev_songs_helper(path)


def delete_from_dev_songs_helper(delete_from_path):
    """
    Delete the specify file in Dev-Songs ("dev_songs/delete_from_path"). Update Catalog.

    Does nothing if file does not exists, return False.
    """
    path = Path(get_dev_song_path(delete_from_path))

    if not path.exists():
        return False, "路徑原本就不存在"

    if path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        path.rmdir()

    generate_dev_songs_catalog()
    
    return True, f"成功刪除{delete_from_path}"