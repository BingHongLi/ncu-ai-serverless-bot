from services.user_service import UserService

import json

class UserController:

    @classmethod
    def get_user(cls,request):
        user_id= request.get('queryStringParameters').get('line_user_id')
        user = UserService.get_user(user_id)
        return user.to_dict()