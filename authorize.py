import os
import json

AUTHORIZED_USERS = [ ]

with open("setting.json") as setting:
    text = setting.read()
    json_data = json.loads(text)
    AUTHORIZED_USERS = json_data["authorized"]

def user_is_authorized(id):
    """
    Takes in a Discord User ID. Return true if the User is authorized.
    """
    
    return id in AUTHORIZED_USERS


def context_sender_is_authorized(ctx):
    """
    Takes in a Discord-Context. Checks if its author is autorized
    """

    return ctx.message.author.id in AUTHORIZED_USERS