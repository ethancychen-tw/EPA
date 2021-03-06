import os

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
login_manager.login_message = '請先登入以存取此頁面'
login_manager.login_message_category = 'alert-info'
login_manager.login_view = 'login'
mail = Mail()

# Line: this is not consistent with other extensions
# line doesn't have init_app method
line_bot_api = LineBotApi(config[os.environ.get('FLASK_ENV')].LINEBOT_MSG_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config[os.environ.get('FLASK_ENV')].LINEBOT_MSG_CHANNEL_SECRET)

from app.routes.route import index, login, logout, register, page_not_found, \
    edit_profile, reset_password_request, password_reset, create_review, request_review, edit_review, view_all_reviews, inspect_review, delete_review, milestone_stat, epa_stat
from app.routes.admin_routes import admin_view_users, create_notifications_fill_review_wrapper
from app.channels import linebot

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    app.add_url_rule('/index', 'index', methods=['GET', 'POST'])
    app.add_url_rule('/', 'index', index, methods=['GET', 'POST'])
    app.add_url_rule('/error', page_not_found, methods=['GET'])
    
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
    # app.add_url_rule('/<account>', 'profile', user, methods=['GET', 'POST'])
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

    # TODO: Blueprint
    app.add_url_rule('/review/create', 'create_review', create_review, methods=['GET', 'POST'])
    app.add_url_rule('/review/request', 'request_review', request_review, methods=['GET', 'POST'])
    app.add_url_rule('/review/edit/<review_id>', 'edit_review', edit_review, methods=['GET', 'POST'])
    app.add_url_rule('/review/delete/<review_id>', 'delete_review', delete_review, methods=['GET', 'POST'])
    app.add_url_rule('/review/inspect/<review_id>', 'inspect_review', inspect_review, methods=['GET'])
    app.add_url_rule('/review/view_all', 'view_all_reviews', view_all_reviews, methods=['GET', 'POST'])

    app.add_url_rule('/milestone_stat', 'milestone_stat', milestone_stat, methods=['GET'])
    app.add_url_rule('/epa_stat', 'epa_stat', epa_stat, methods=['GET'])
    
    # admin
    app.add_url_rule('/admin/view_users','admin_view_users', admin_view_users, methods=['GET', 'POST'])
    app.add_url_rule('/admin/create_notifications_fill_review','create_notifications_fill_review', create_notifications_fill_review_wrapper, methods=['GET', 'POST'])

    # channels
    app.add_url_rule('/linebot_callback', 'linebot_callback', linebot.callback, methods=['POST'])

    
    return app

# app/__init__
# declare a function create_app that return app