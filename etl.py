# this is only for system admin, not managers
# store some etl jobs that later on we could make them cronjobs
import datetime
from flask import url_for

from app import db, create_app  # 此時db仍沒有連上engine，因為app在  __init__.py 中只有初始化SQLAlchemy空物件而已
app = create_app() # 這裏db也還是沒有連上，只是創造出app 環境而已
app.app_context().push()  # 把環境推入，這時候db就連上了，也可以使用with app.context():裡面再使用query

from app.models.review import Review, Location, ReviewDifficulty, ReviewScore, ReviewSource, Milestone, CoreCompetence, MilestoneItemEPA, EPA, MilestoneItem
from app.models.user import User, Group, Role, Notification

def update_all_R_user_role():
    r1 = Role.query.filter(Role.name=="住院醫師-R1").first()
    r2 = Role.query.filter(Role.name=="住院醫師-R2").first()
    r3 = Role.query.filter(Role.name=="住院醫師-R3").first()
    r4 = Role.query.filter(Role.name=="住院醫師-R4").first()
    r5 = Role.query.filter(Role.name=="住院醫師-R5(總醫師)").first()
    students_to_update = User.query.join(Role).filter(User.role_id.in_([role.id for role in [r1,r2,r3,r4]])).all()
    for std in students_to_update:
        if std.role_id == r1.id:
            std.role = r2
        elif std.role_id == r2.id:
            std.role = r3
        elif std.role_id == r3.id:
            std.role = r4
        else:
            std.role = r5
        db.session.commit()


# temporialy do this. later should move this into flask cmd
def update_rich_menu(callback_url=None):
    if not callback_url:
        raise ValueError("need callback_url to update button links")
    from app.routes.route import index
    from flask import url_for
    from app import line_bot_api
    from linebot.models import RichMenu,RichMenuSize, RichMenuArea, RichMenuBounds, URIAction
    print('deleting all rich menu')
    old_rich_menu_list = line_bot_api.get_rich_menu_list()
    for rich_menu in old_rich_menu_list:
        line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)
        
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=1200, height=400),
        selected=False,
        name=f"EPA rich menu {datetime.datetime.now()}",
        chat_bar_text="Tap here",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=400, height=400),
                action=URIAction(label='New review', uri=callback_url+"/review/request")
                ),
            RichMenuArea(
                bounds=RichMenuBounds(x=400, y=0, width=400, height=400),
                action=URIAction(label='Index', uri=callback_url)
                ),
            RichMenuArea(
                bounds=RichMenuBounds(x=800, y=0, width=400, height=400),
                action=URIAction(label='View reviews', uri=callback_url+"/review/view_all")
                ),
                ]
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
    print(f'{rich_menu_id} created as default rich menu');   
    # upload img for rich menu
    with open("./app/static/img/line_richmenu.png", 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)
    line_bot_api.set_default_rich_menu(rich_menu_id)
update_rich_menu("https://ljbikaxozf.execute-api.ap-northeast-1.amazonaws.com/development/")