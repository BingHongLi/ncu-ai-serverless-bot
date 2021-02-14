from models.user import User

import boto3
import os
class UserDAO:

    # 檢查表格，若不存在，則創建
    print(os.environ.get("DYNAMODB_LOCAL_PATH"))
    dynamodb_client = boto3.resource('dynamodb', endpoint_url=os.environ.get("DYNAMODB_LOCAL_PATH"))
    users_ref = dynamodb_client.Table(User.table_name)
    try:
        table_does_exist = users_ref.attribute_definitions
    except:
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
        print("插入資料")

        try:
            result = cls.users_ref.put_item(
                Item=user.to_dict(),
                ConditionExpression="line_user_nickname <> :nick_name",
                ExpressionAttributeValues={':nick_name':user.line_user_nickname}
            )
            return result

        except:
            print("用戶插入失敗，因用戶名未更新")
            pass

    # 讀取資料
    @classmethod
    def get_user_by_id(cls,line_user_id:str):
        print(f"讀取用戶資料，用戶id為 {line_user_id}")
        user = cls.users_ref.get_item(
            Key={
            "line_user_id":line_user_id
            }
        )
        return user

    # 更新資料

