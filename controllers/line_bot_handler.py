'''
當用戶關注時，必須取用照片，並存放至指定bucket位置，而後生成User物件，存回db
當用戶取消關注時，
    從資料庫提取用戶數據，修改用戶的封鎖狀態後，存回資料庫
'''

from services.user_service import UserService

class LineBotController:


    # 將消息交給用戶服務處理
    @classmethod
    def follow_event(cls,event):
        print(event)
        UserService.line_user_follow(event)

    @classmethod
    def unfollow_event(cls,event):
        UserService.line_user_unfollow(event)