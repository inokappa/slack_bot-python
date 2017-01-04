# -*- coding: utf-8 -*-
import os
import time
from slackclient import SlackClient
import feedparser
import json
import requests
import logging
import toml

SETTING = toml.load(open('setting.toml'))

BOT_ID = SETTING['slack']['bot_id']
AT_BOT = '<@' + BOT_ID + '>'
EXAMPLE_COMMAND = SETTING['common']['example_command']

stream_log = logging.StreamHandler()
stream_log.setLevel(logging.DEBUG)
stream_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logging.getLogger().addHandler(stream_log)
logging.getLogger().setLevel(logging.DEBUG)

slack_client = SlackClient(SETTING['slack']['api_token'])

def get_weather():
    uri = SETTING['get_weather']['uri']
    response  = json.loads(requests.get(uri).text)
    title     = response['title']
    link      = response['link']
    weather   = response['forecasts'][0]
    image_url = weather['image']['url']

    responses = ''
    responses = weather['date'] + ' ' + title + weather['telop'] + '\n'
    responses += image_url
    return responses

def train_delay():
    uri = SETTING['train_delay']['uri']

    response = feedparser.parse(uri)
    responses = ''
    for entry in response.entries:
        responses += entry.title + '\n'
        responses += entry.updated + '\n'
        responses += entry.link + '\n'
    return responses

def handle_command(command, channel):
    response = u'ごめんなさい. コマンドを理解できません. *' + EXAMPLE_COMMAND + \
               u'* を付けて呼んで下さいね.'
    if command.startswith(EXAMPLE_COMMAND) or command.startswith(': ' + EXAMPLE_COMMAND):
        if command.split()[-1] == u'遅延':
            response = train_delay()
        elif command.split()[-1] == u'天気':
            response = get_weather()
        else:
            response = u'わかりません'
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = SETTING['common']['interval']
    if slack_client.rtm_connect():
        logging.info('bot を開始しました...')
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        logging.warn('slack への接続に失敗しました.')
