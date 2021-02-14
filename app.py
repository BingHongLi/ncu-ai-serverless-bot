import json

# import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from linebot.models import (FollowEvent,UnfollowEvent)
from controllers.line_bot_handler import LineBotController
import os

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

def lambda_handler(event, context):
    print(os.environ.get("DYNAMODB_LOCAL_PATH"))
    print(os.environ.get("LINE_CHANNEL_SECRET"))
    print(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
    # get X-Line-Signature header value
    signature = event.get("headers").get('X-Line-Signature')

    # get request body as text
    body = event.get("body")

    # handle webhook body
    try:
        print(body)
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }

@handler.add(FollowEvent)
def handle_line_follow(event):
    return LineBotController.follow_event(event)

@handler.add(UnfollowEvent)
def handle_line_unfollow(event):
    return LineBotController.unfollow_event(event)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))