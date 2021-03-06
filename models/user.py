from __future__ import annotations
'''
抓出Line User的屬性
並設置
主要屬性，以供Dynamodb建置表格使用
建構子
from_dict，以dict去建構User物件
to_dict，將User物件轉換成dict
__repr__，客製化Print的內容
'''
import boto3
class User(object):

    table_name="users"
    attribute_definitions = [
        {
            'AttributeName': 'line_user_id',
            'AttributeType': 'S',
        }
    ]
    key_schema=[
            {
                'AttributeName': 'line_user_id',
                'KeyType': 'HASH',
            }
    ]

    def __init__(self,line_user_id,line_user_pic_url,line_user_nickname,line_user_status,line_user_system_language,blocked=False,ai_image_quota=5):
        self.line_user_id = line_user_id
        self.line_user_pic_url = line_user_pic_url
        self.line_user_nickname = line_user_nickname
        self.line_user_status = line_user_status
        self.line_user_system_language=line_user_system_language
        self.blocked=blocked
        self.ai_image_quota=ai_image_quota


    @staticmethod
    def from_dict(source:dict) -> User :
        user=User(
            line_user_id=source.get(u'line_user_id'),
            line_user_pic_url=source.get(u'line_user_pic_url'),
            line_user_nickname=source.get(u'line_user_nickname'),
            line_user_status=source.get(u'line_user_status'),
            line_user_system_language=source.get(u'line_user_system_language'),
            blocked=source.get(u'blocked'),
            ai_image_quota=source.get(u'ai_image_quota',3)
            )
        return user

    def to_dict(self):
        user_dict={
            "line_user_id":self.line_user_id,
            "line_user_pic_url":self.line_user_pic_url,
            "line_user_nickname":self.line_user_nickname,
            "line_user_status":self.line_user_status,
            "line_user_system_language":self.line_user_system_language,
            "blocked":self.blocked,
            'ai_image_quota':self.ai_image_quota
        }
        return user_dict


    def __repr__(self):
        return (f'''User(
            line_user_id={self.line_user_id},
            line_user_pic_url={self.line_user_pic_url},
            line_user_nickname={self.line_user_nickname},
            line_user_status={self.line_user_status},
            line_user_system_language={self.line_user_system_language},
            blocked={self.blocked},
            ai_image_quota={self.ai_image_quota}
            )'''
            )

