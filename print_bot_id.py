import os
from slackclient import SlackClient
import toml

BOT_NAME = 'pika'
SETTING = toml.load(open('setting.toml'))

slack_client = SlackClient(SETTING['slack']['api_token'])

if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)
