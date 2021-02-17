from models.user import User

import boto3
import os
from decimal import Decimal
'''
串聯dynamodb，並偵測是否有相應的dynamodb table，
    若無，則建立；若有，則跳過。
save_user，將User物件插入資料庫，並設置了更新條件，必須在暱稱有變動的情況下，才允許重新插入資料
get_user_by_id，以用戶id，取得用戶資料
update_user_image_quota，傳入user，但只更新user的ai_image照片數與 封鎖狀態
'''
class UserDAO:

    # 檢查表格，若不存在，則創建
    # 分多個階段開發，第一階段的開發，會使用本地DynamoDB，此刻建立的客戶端如下
    # print(os.environ.get("DYNAMODB_LOCAL_PATH"))
    # dynamodb_client = boto3.resource('dynamodb', endpoint_url=os.environ.get("DYNAMODB_LOCAL_PATH"))

    # 第二階段的開發，串接雲端的DynamoDB，此刻建立的客戶端如下
    dynamodb_client = boto3.resource('dynamodb')

    # 建立表格連線
    users_ref = dynamodb_client.Table(User.table_name)
    try:
        # 描述表格的屬性，若不存在表格，則會發生例外
        table_does_exist = users_ref.attribute_definitions
    except:
        # 創建表格
        dynamodb_client.create_table(
            TableName=User.table_name,
            AttributeDefinitions=User.attribute_definitions,
            KeySchema=User.key_schema,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )


    # 插入資料
    # 此處設計暫時為若名字不同，才更新
    @classmethod
    def save_user(cls,user:User):

        try:
            result = cls.users_ref.put_item(
                Item=user.to_dict(),
                ConditionExpression="line_user_nickname <> :nick_name",
                ExpressionAttributeValues={':nick_name':user.line_user_nickname}
            )
            return result

        except:
            print("用戶插入失敗，因用戶名未更新")
            return None

    # 讀取資料
    @classmethod
    def get_user_by_id(cls,line_user_id:str):

        print(f"讀取用戶資料，用戶id為 {line_user_id}")
        item_dict = cls.users_ref.get_item(
            Key={
            "line_user_id":line_user_id
            }
        )
        user_dict=item_dict.get('Item')
        print(f"用戶資料為{user_dict}")
        user=User.from_dict(user_dict)
        return user

    # 更新資料
    @classmethod
    def update_user_image_quota(cls,user):

        print(f'更新用戶資料')
        update_response = cls.users_ref.update_item(
            Key={
                "line_user_id": user.line_user_id
            },
            UpdateExpression="set ai_image_quota=:n, blocked=:s",
            ExpressionAttributeValues={
                ':n': Decimal(user.ai_image_quota),
                ':s': user.blocked
            },
            ReturnValues="UPDATED_NEW"
        )
        return update_response