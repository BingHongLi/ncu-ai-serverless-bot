import json

# import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage
)

from linebot.models import (FollowEvent,UnfollowEvent)
from controllers.line_bot_handler import LineBotController
import os
import watchtower, logging
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

# log 紀錄
logging.basicConfig(level=logging.INFO)
line_logger = logging.getLogger("ncu_ai_serverless_line_event")
line_logger.addHandler(watchtower.CloudWatchLogHandler())

def lambda_handler(event, context):

    # get X-Line-Signature header value
    signature = event.get("headers").get('X-Line-Signature')

    # get request body as text
    body = event.get("body")
    line_logger.info(body)
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

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    return LineBotController.image_event(event)

