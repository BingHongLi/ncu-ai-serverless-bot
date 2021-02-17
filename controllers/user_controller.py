from services.user_service import UserService

import json

'''
用戶GET查詢路徑時，下達line_user_id，可查閱用戶資料
'''
class UserController:

    @classmethod
    def get_user(cls,request):
        user_id= request.get('queryStringParameters').get('line_user_id')
        user = UserService.get_user(user_id)
        return user.to_dict()