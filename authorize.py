import os
import json

AUTHORIZED_USERS = [ ]

with open("setting.json") as setting:
    text = setting.read()
    json_data = json.loads(text)
    AUTHORIZED_USERS = json_data["authorized"]


def user_id_is_authorized(id):
    """
    Takes in a Discord User ID. Return true if the User is authorized.
    """
    
    return str(id) in AUTHORIZED_USERS


def discord_user_is_authorized(user):
    """Returns if the discord user is authorized.

    Args:
        user (Discord User): The user to be tested.

    Returns:
        [bool]: Is the user authorized?
    """
    return str(user.id) in AUTHORIZED_USERS