import jwt
from flask import request, abort, url_for, current_app
from linebot.models.responses import Profile
from app import db, line_bot_api, handler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from linebot.exceptions import InvalidSignatureError
import datetime

linebotinfo = line_bot_api.get_bot_info()

class LineUser():
    def __init__(self, line_userId):
        self.user_id = line_userId

    def get_jwt(self, expire_sec=300):
        print("jwt encoding------")
        print({
                'line_userId': self.user_id,
                'exp': datetime.datetime.now() + datetime.timedelta(seconds=expire_sec)
            })
        return jwt.encode(
            {
                'line_userId': self.user_id,
                'exp': datetime.datetime.now() + datetime.timedelta(seconds=expire_sec)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_jwt(token):
        try:
            pay_load = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            line_user_Id = pay_load.get('line_userId', None)
            if not line_user_Id:
                raise ValueError('verify jwt error: no line_userId in payload')
            line_user_profile = line_bot_api.get_profile(line_user_Id)
        except Exception as e:
            print('verify jwt line_new_user_token error')
            print(e)
            return None
        return line_user_profile

def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except Exception as e: #InvalidSignatureError:
        print(e)
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    from app.models.user import User, LineNewUser
    # if registered, reply login link(using token)
    print(f"line event type: {event.type}")
    line_userId = event.source.user_id # The attribute is called user_id, surprise lol
    
    user = User.query.filter(User.line_userId == line_userId).first()
    
    if not user:
        # I think this is not safe. But let use this for now
        # for more advanced link token see, https://developers.line.biz/en/docs/messaging-api/linking-accounts/#implement-account-link-feature
        # or alternatively, we could have our own token auth method
        line_new_user_token = LineUser(line_userId).get_jwt()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(f'請點此註冊或綁定你的帳號: {url_for("register", _external=True, line_new_user_token=line_new_user_token)}')) 
    else:
        # if registered, reply with greeting msg
        line_bot_api.reply_message(event.reply_token,TextSendMessage(f'嗨，{user.username}，請點此連結登入EPA系統 {url_for("index", _external=True)}'))

def send_line(to, subject, msg_body):
    line_bot_api.push_message(to, TextSendMessage(text=(subject + "\n" + msg_body)))