from flask import request, abort, url_for
from app import db, line_bot_api, handler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from linebot.exceptions import InvalidSignatureError

linebotinfo = line_bot_api.get_bot_info()

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
    print(f"event type: {event.type}")
    line_userId = event.source.user_id # The attribute is called user_id, surprise lol
    print(line_userId)
    
    user = User.query.filter(User.line_userId == line_userId).first()
    
    if not user:
        # I think this is not safe. But let use this for now
        # for more advanced link token see, https://developers.line.biz/en/docs/messaging-api/linking-accounts/#implement-account-link-feature
        # or alternatively, we could have our own token auth method
        line_new_user = LineNewUser(line_userId=line_userId)
        db.session.add(line_new_user)
        db.session.commit()
        line_new_user_token = line_new_user.get_jwt()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(f'請點此註冊或綁定你的帳號: {url_for("register", _external=True, line_new_user_token=line_new_user_token)}'))  
    else:
        # if registered, reply with greeting msg
        line_bot_api.reply_message(event.reply_token,TextSendMessage(f'嗨，{user.username}，請點此連結登入EPA系統 {url_for("index", _external=True)}'))

def send_line(to, subject, msg_body):
    line_bot_api.push_message(to, TextSendMessage(text=(subject + "\n" + msg_body)))