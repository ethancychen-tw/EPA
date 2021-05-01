from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_login import LoginManager
from flask_mail import Mail

from linebot import LineBotApi, WebhookHandler
from app.config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'
mail = Mail()
line_bot_api = LineBotApi(config['production'].LINEBOT_MSG_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config['production'].LINEBOT_MSG_CHANNEL_SECRET)

from app.route import index, login, logout, register, user, page_not_found, \
    edit_profile, reset_password_request, password_reset, user_activate, new_review, request_review, edit_review, view_reviews, callback, login_token, inspect_review

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
    app.add_url_rule('/login_token', 'login_token', login_token, methods=['GET', 'POST'])
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
    app.add_url_rule('/review/edit/<review_id>', 'edit_review', edit_review, methods=['GET', 'POST'])
    app.add_url_rule('/review/inspect/<review_id>', 'inspect_review', inspect_review, methods=['GET'])
    
    app.add_url_rule('/view_reviews', 'view_reviews', view_reviews, methods=['GET', 'POST'])
    

    app.add_url_rule('/callback', 'callback', callback, methods=['POST'])
    return app

# app/__init__
# declare a function create_app that return app