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
import boto3
from daos.user_dao import UserDAO
from models.user import User
class LineImageService:


    line_bot_api = LineBotApi(channel_access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))

    @classmethod
    def ai_face_compare_aws_rekognition_model(cls,event):

        # 取得用戶資料，檢測用戶的用量，若為0，則發訊息
        user:User = UserDAO.get_user_by_id(event.source.user_id)

        if int(user.ai_image_quota) <= 0 :
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    """你的AI呼吸已經用完了，只剩下求老師一途了。"""
                )
            )
        else:
            reko_client = boto3.client('rekognition')
            imageSource = open("converted_savedmodel/compare_source.jpg", 'rb')

            message_content = cls.line_bot_api.get_message_content(event.message.id)
            file_name = f"/tmp/{event.source.user_id}_{event.message.id}.jpg"
            with open(file_name, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)

            imageTarget = open(file_name, 'rb')

            try:

                compare_response = reko_client.compare_faces(
                    SimilarityThreshold=80,
                    SourceImage={'Bytes': imageSource.read()},
                    TargetImage={'Bytes': imageTarget.read()}
                )
                print(compare_response)
                print(len(compare_response['FaceMatches']))
                user.ai_image_quota = user.ai_image_quota - 1
                UserDAO.update_user_image_quota(user)

                if len(compare_response['FaceMatches']) > 0:
                    cls.line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            f"""你老師在此，快來拿加選單， 你的AI呼吸還有{user.ai_image_quota}次"""
                        )
                    )
                else:
                    cls.line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            f"""再混啊！亂拍照！！你在拍心儀對象，別以為我不知道，不過這樣也好，愛情比課程重要，退選吧。 對了，你的AI呼吸還有{user.ai_image_quota}次"""
                        )
                    )

                storage_client = boto3.client('s3')
                bucket_name = os.environ['USER_INFO_GS_BUCKET_NAME']
                destination_blob_name = f'{user.line_user_id}/img/{event.message.id}.png'
                storage_client.upload_file(file_name, bucket_name, destination_blob_name)


            except:

                cls.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        f"""再混啊！亂拍照！！這張照片裡面沒有人，你能拍的張數不多了，你的AI呼吸還有{user.ai_image_quota}次，快去選下門課吧。"""
                    )
                )

            finally:
                os.remove(file_name)





    @classmethod
    def ai_face_compare_local_model(cls,event):

        class_dict = {}
        with open('converted_savedmodel/labels.txt') as f:
            for line in f:
                (key, val) = line.split()
                class_dict[int(key)] = val

        # Load the model
        model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel', compile=False)

        message_content = cls.line_bot_api.get_message_content(event.message.id)
        file_name = '/tmp/' + event.message.id + '.jpg'
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
        prediction = model.predict(data)

        max_probability_item_index = np.argmax(prediction[0])

        if prediction.max() > 0.6:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    """這個物件極有可能是 %s ，其相似機率為 %s ，他就是你的白馬王子。""" % (
                    class_dict.get(max_probability_item_index), prediction[0][max_probability_item_index])
                )
            )
        else:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    """再混啊！亂拍照！！"""
                )
            )
