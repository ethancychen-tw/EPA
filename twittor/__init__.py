from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_login import LoginManager
from flask_mail import Mail

from linebot import LineBotApi, WebhookHandler
from linebot.models.rich_menu import RichMenu, RichMenuSize,RichMenuArea,RichMenuBounds
from linebot.models.actions import URIAction
from twittor.config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'
mail = Mail()
line_bot_api = LineBotApi(config['production'].LINEBOT_MSG_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config['production'].LINEBOT_MSG_CHANNEL_SECRET)

rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=False,
    name="Nice richmenu",
    chat_bar_text="Tap here",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
        action=URIAction(label='Go to line.me', uri='https://636d7168be66.ngrok.io/'))]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
with open("./kerker.png", 'rb') as f:
    try:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
        line_bot_api.set_default_rich_menu(rich_menu_id)
    except Exception as e:
        print("===Upload Exception===")

from twittor.route import index, login, logout, register, user, page_not_found, \
    edit_profile, reset_password_request, password_reset, user_activate, new_review, request_review, fill_review, view_reviews, review, callback

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)


    app.add_url_rule('/index', 'index', methods=['GET', 'POST'])
    app.add_url_rule('/', 'index', index, methods=['GET', 'POST'])
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
    app.add_url_rule('/<username>', 'profile', user, methods=['GET', 'POST'])
    app.add_url_rule('/edit_profile', 'edit_profile', edit_profile, methods=['GET', 'POST'])
    app.add_url_rule(
        '/reset_password_request',
        'reset_password_request',
        reset_password_request,
        methods=['GET', 'POST']
    )
    app.add_url_rule(
        '/password_reset/<token>',
        'password_reset',
        password_reset,
        methods=['GET', 'POST']
    )
    app.register_error_handler(404, page_not_found)
    # app.add_url_rule('/explore', 'explore', explore)
    app.add_url_rule('/activate/<token>', 'user_activate', user_activate)
    app.add_url_rule('/review/new', 'new_review', new_review, methods=['GET', 'POST'])
    app.add_url_rule('/review/request', 'request_review', request_review, methods=['GET', 'POST'])
    app.add_url_rule('/review/fill/<review_id>', 'fill_review', fill_review, methods=['GET', 'POST'])
    app.add_url_rule('/view_reviews', 'view_reviews', view_reviews, methods=['GET', 'POST'])
    app.add_url_rule('/review/<review_id>', 'review', review, methods=['GET'])

    app.add_url_rule('/callback', 'callback', callback, methods=['POST'])
    return app

# app/__init__
# declare a function create_app that return app