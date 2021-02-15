import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np

# 引用套件
from linebot.models import (
    MessageEvent,ImageMessage,TextSendMessage
)

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

from linebot import (
    LineBotApi
)

import os

class LineImageService:

    # Load the model
    model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel', compile=False)
    line_bot_api = LineBotApi(channel_access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))

    class_dict = {}
    with open('converted_savedmodel/labels.txt') as f:
        for line in f:
            (key, val) = line.split()
            class_dict[int(key)] = val

    @classmethod
    def ai_image_detect(cls,event):

        message_content = cls.line_bot_api.get_message_content(event.message.id)
        file_name = event.message.id + '.jpg'
        with open(file_name, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)

        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image = Image.open(file_name)
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)
        # turn the image into a numpy array
        image_array = np.asarray(image)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0 - 1)

        # Load the image into the array
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array[0:224, 0:224, 0:3]
        # run the inference
        prediction = cls.model.predict(data)

        max_probability_item_index = np.argmax(prediction[0])

        if prediction.max() > 0.6:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    """這個物件極有可能是 %s ，其相似機率為 %s ，他就是你的白馬王子。""" % (
                    cls.class_dict.get(max_probability_item_index), prediction[0][max_probability_item_index])
                )
            )
        else:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    """再混啊！亂拍照！！"""
                )
            )
