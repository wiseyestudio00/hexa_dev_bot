import os
import json

AUTHORIZED_USERS = [ ]

with open("setting.json") as setting:
    text = setting.read()
    json_data = json.loads(text)
    AUTHORIZED_USERS = json_data["authorized"]

def user_is_authorized(id):
    return id in AUTHORIZED_USERS