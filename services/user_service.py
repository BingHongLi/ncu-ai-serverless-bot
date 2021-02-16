from models.user import User

from linebot import (
    LineBotApi
)
import os

from daos.user_dao import UserDAO

# 圖片下載與上傳專用
import urllib.request

#
import boto3


class UserService:

    line_bot_api = LineBotApi(channel_access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))

    # 取得line event，將line event拿去取個資，轉換成User，並將其照片取出
    @classmethod
    def line_user_follow(cls, event):
        print(event)
        # 取個資
        line_user_profile = cls.line_bot_api.get_profile(event.source.user_id)
        # line_user_profile= cls.line_bot_api.get_profile(event)

        # event轉換成user
        user = User(
            line_user_id=line_user_profile.user_id,
            line_user_pic_url=line_user_profile.picture_url,
            line_user_nickname=line_user_profile.display_name,
            line_user_status=line_user_profile.status_message,
            line_user_system_language=line_user_profile.language,
            blocked=False
        )

        # 取得用戶照片，存放回cloud storage，並將連結存回user的連結
        if user.line_user_pic_url is not None:
            file_name = f"/tmp/{user.line_user_id}.jpg"
            urllib.request.urlretrieve(user.line_user_pic_url, file_name)

            # 更換為s3的做法
            storage_client = boto3.client('s3')
            bucket_name = os.environ['USER_INFO_GS_BUCKET_NAME']
            destination_blob_name = f'{user.line_user_id}/user_pic.png'
            storage_client.upload_file(file_name, bucket_name, destination_blob_name)
            destination_url = f'https://{bucket_name}.s3.amazonaws.com//{user.line_user_id}/user_pic.png'
            user.line_user_pic_url = destination_url

        # 存入資料庫
        UserDAO.save_user(user)

        # 打印結果
        print(user)
        os.remove(file_name)

        # 回傳結果給handler
        # 關注的部分，不回傳，交由控制台回傳
        pass

    # 從資料庫內取出用戶資料，並將其blocked狀態，更改為True
    @classmethod
    def line_user_unfollow(cls, event):
        user = UserDAO.get_user_by_id(event.source.user_id)
        user.blocked = True
        UserDAO.save_user(user)
        print(user)
        print('用戶已封鎖')

        pass

    @classmethod
    def get_user(cls, user_id: str):
        user = UserDAO.get_user_by_id(user_id)
        return user
