import datetime
import json
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    abort,
    current_app,
    flash,
    Markup,
)
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, func, String

from app.forms.general import (
    LoginForm,
    RegisterForm,
    EditProfileForm,
    PasswdResetRequestForm,
    PasswdResetForm,
    ReviewForm,
    ReviewFilterForm,
)

# from app.forms import AdminEditGroupForm, AdminEditReviewForm, AdminEditProfileForm
from app.models.user import User, load_user, Group, Role, LineNewUser, Notification
from app.models.review import (
    Review,
    EPA,
    MilestoneItemEPA,
    MilestoneItem,
    Milestone,
    CoreCompetence,
    Location,
    ReviewDifficulty,
    ReviewScore,
    ReviewSource,
)
from app import db
from app.channels.linebot import linebotinfo, line_bot_api
from app.routes.admin_routes import flush_channel_notifications # temploraily make the notification imediate

@login_required
def inspect_review(review_id):
    """
    see only, can't edit
    only reviewer or reviewee could see
    """
    prefilled_review = Review.query.get(review_id)
    if not prefilled_review:
        flash("no such review", "alert-danger")
        return redirect(url_for("index"))
    if not current_user.can_view_review(prefilled_review):
        flash("您沒有權限存取這個評核", "alert-warning")
        return redirect(url_for("index"))
    
    # (1) form configuration
    form = ReviewForm()
    
    form.location.choices = [("", prefilled_review.location.desc)]
    form.epa.choices = [("", prefilled_review.epa.desc)]
    form.reviewee.choices = [("", prefilled_review.reviewee.username)]
    form.reviewer.choices = [("", prefilled_review.reviewer.username)]
    form.review_difficulty.choices = [
        (
            "",
            prefilled_review.review_difficulty.desc
            if prefilled_review.review_difficulty
            else "",
        )
    ]
    form.review_score.choices = [
        (
            "",
            prefilled_review.review_score.desc if prefilled_review.review_score else "",
        )
    ]
    form.creator.choices = [("", prefilled_review.creator.username)]
    form.review_source.choices = [("", prefilled_review.review_source.desc)]


    for field in form:
        field.render_kw = {"disabled": "disabled"}
    if not prefilled_review.complete and prefilled_review.creator_id == current_user.id and prefilled_review.review_source_id == ReviewSource.query.filter(ReviewSource.name=='request').first().id:
        showing_fields = form.requesting_fields + form.meta_fields
    else:   
        showing_fields = form.requesting_fields + form.scoring_fields + form.meta_fields
    # (2) on submit handle (not applicable here)

    # (3) prefill: (for select fields, must be valid choices configured above)
    form.implement_date.data = prefilled_review.implement_date
    form.reviewee_note.data = prefilled_review.reviewee_note
    form.review_compliment.data = prefilled_review.review_compliment
    form.review_suggestion.data = prefilled_review.review_suggestion
    form.creator.data= [("", prefilled_review.creator.username)]
    form.review_source.data = [("", prefilled_review.review_source.desc)]
    form.complete = [("", prefilled_review.complete)]
    form.create_time.data = prefilled_review.create_time
    form.last_edited.data = prefilled_review.last_edited

    milestone_item_epa_linkage, milestone_items, epa_milestones = get_epa_linkages()
    
    return render_template(
        "make_review.html",
        title="查看評核",
        form=form,
        milestone_item_epa_linkage=milestone_item_epa_linkage,
        milestone_items=milestone_items,
        epa_milestones=epa_milestones,
        review=prefilled_review,
        review_type="inspect",
        showing_fields=showing_fields
    )

@login_required
def create_review():
    if not current_user.can_create_review():
        if current_user.can_request_review():
            return redirect(url_for('request_review'))
        flash('你沒有權限建立評核','alert-danger')
        return redirect(url_for('index'))
    review = Review()
    review.reviewer = current_user
    review.creator = current_user
    review.is_draft = True
    review.review_source = ReviewSource.query.filter(ReviewSource.name == 'new').first()
    return process_review(review, is_new=True)


@login_required
def request_review():
    if not current_user.can_request_review():
        if current_user.can_create_review():
            return redirect(url_for('create_review'))
        flash('你沒有權限請求評核','alert-danger')
        return redirect(url_for('index'))
    review = Review()
    review.reviewee = current_user
    review.creator = current_user
    review.review_source = ReviewSource.query.filter(ReviewSource.name == 'request').first()
    review.is_draft = True # must set to true so that could edit
    return process_review(review, is_new=True)

@login_required
def edit_review(review_id):
    try:
        review = Review.query.get(review_id)
    except Exception as e:
        flash("review not found!")
        print(e)
    if not current_user.can_edit_review(review):
        flash("您沒有權限編輯這個評核", "alert-warning")
        return redirect(url_for("index"))
    return process_review(review)

def process_review(review, is_new=False):
    review_type = "user_edit"
    # (1) form configuration mostly for select fields
    form = ReviewForm()

    # configure - request fields
    form.epa.choices = [(str(epa.id), epa.desc)for epa in EPA.query.with_entities(EPA.id,EPA.desc).all()]
    if current_user == review.reviewer:
        form.reviewer.choices = [(review.reviewer_id, review.reviewer.username)]
        form.reviewee.choices = [(user.id, user.username) for user in current_user.get_potential_reviewees()]
        form.reviewee_note.render_kw = {'disabled':'disabled'}
    elif current_user == review.reviewee:
        form.reviewer.choices = [(user.id, user.username) for user in current_user.get_potential_reviewers()]
        form.reviewee.choices = [(review.reviewee.id, review.reviewee.username)]
        form.review_difficulty.validate_choice=False
        form.review_score.validate_choice=False
    form.location.choices = [(str(location.id), location.desc) for location in Location.query.with_entities(Location.id, Location.desc).all()]
    # configure - scoring field
    form.review_difficulty.choices = [(str(rd.id), rd.desc) for rd in ReviewDifficulty.query.with_entities(ReviewDifficulty.id, ReviewDifficulty.desc).all()]
    form.review_score.choices = [(str(rs.id), rs.desc) for rs in ReviewScore.query.with_entities(ReviewScore.id, ReviewScore.desc).all()]
    
    if current_user == review.reviewer:
        showing_fields = form.requesting_fields + form.scoring_fields
    elif current_user == review.reviewee:
        showing_fields = form.requesting_fields

    # (2) on submit process
    if form.validate_on_submit():
        # requesting fields
        review.epa = EPA.query.get(int(form.epa.data))
        review.reviewer = User.query.get(form.reviewer.data)
        review.reviewee = User.query.get(form.reviewee.data)
        review.location = Location.query.get(int(form.location.data))
        review.implement_date = form.implement_date.data
        review.reviewee_note = form.reviewee_note.data
        # scoring fields
        if current_user.id == review.reviewer_id:
            if form.review_difficulty.data:
                review.review_difficulty = ReviewDifficulty.query.get(int(form.review_difficulty.data)) 
            review.review_compliment = form.review_compliment.data
            review.review_suggestion = form.review_suggestion.data
            if form.review_score.data:
                review.review_score = ReviewScore.query.get(int(form.review_score.data))
        # meta fields (when editing, no need to update every one)
        if form.submit.data:
            # press submit btn
            review.is_draft = False
            if review.reviewer == current_user:
                review.complete = True
            else:
                # 是學生 提交 就設為false，這樣就會通知老師
                review.complete = False
        elif form.submit_draft.data:
            if review.reviewer == current_user and review.review_source.name == 'request':
                review.is_draft = False
            else:
                review.is_draft = True
            # press save draft btn
        review.last_edited = datetime.datetime.now()

        try:
            if is_new:
                db.session.add(review)
            db.session.commit()
            if review.complete and form.submit.data:
                flash("評核提交成功", "alert-success")
                # notify std
                subject = "[EPA通知]您已被評核"
                msg_body = f'{review.reviewee.username}你好，\n{review.reviewer.username}已評核你於{review.implement_date.strftime("%Y-%m-%d")}實作的{review.epa.desc}，你可前往系統查看'
                notification = Notification(user_id=review.reviewee.id,subject=subject, msg_body=msg_body)
                db.session.add(notification)
            elif form.submit.data and not review.complete:
                subject = "[EPA通知]學生請求評核"
                msg_body = f'{review.reviewer.username}你好，\n{review.reviewee.username}請求您評核他於{review.implement_date.strftime("%Y-%m-%d")}實作的{review.epa.desc}'
                notification = Notification(user_id=review.reviewer.id,subject=subject, msg_body=msg_body)
                db.session.add(notification)
                flash('請求提交成功，將會通知老師評核','alert-success')
            elif form.submit_draft.data:
                flash('儲存成功','alert-success')
        except Exception as e:
            print(e)
        
        return redirect(url_for("inspect_review", review_id=review.id))

    # (3) prefill (if have)
    # no matter it's std or teacher, we could prefill with prefilled review anyway
    # (PS) if field render_kw is disabled, the prefill could only be default, or it won't pass form validation
    # requesting fields
    # if prefilled_review.epa_id:
    form.epa.data = str(review.epa_id or form.epa.choices[0][0])
    # if prefilled_review.reviewer_id:
    form.reviewer.data = review.reviewer_id or form.reviewer.choices[0][0]
    # if prefilled_review.reviewee_id:
    form.reviewee.data = review.reviewee_id or form.reviewee.choices[0][0]
    # if prefilled_review.location_id:
    form.location.data = str(review.location_id) or form.location.choices[0][0]
    form.implement_date.data = review.implement_date or datetime.datetime.now()
    form.reviewee_note.data = review.reviewee_note 

    # scoring field
    form.review_difficulty.data = str(review.review_difficulty_id or str(form.review_difficulty.choices[0][0]))
    form.review_compliment.data = review.review_compliment
    form.review_suggestion.data = review.review_suggestion
    form.review_score.data = str(review.review_score_id or str(form.review_score.choices[0][0]))
    
    
    milestone_item_epa_linkage, milestone_items, epa_milestones = get_epa_linkages()
    
    return render_template(
        "make_review.html",
        title="新增評核",
        form=form,
        milestone_item_epa_linkage=milestone_item_epa_linkage,
        milestone_items=milestone_items,
        epa_milestones=epa_milestones,
        review=review,
        review_type=review_type,
        showing_fields=showing_fields,
        is_new=is_new
    )


@login_required
def delete_review(review_id):
    try:
        review = Review.query.get(review_id)
    except Exception as e:
        flash("review not found!")
        print(e)

    if current_user.can_delete_review(review):
        try:
            db.session.delete(review)
            db.session.commit()
            flash("已成功刪除", "alert-info")
        except Exception as e:
            flash("未成功刪除，如果問題一直存在，請聯絡管理員")
            print(e)
    return redirect(request.referrer) # stay on the same page


@login_required
def view_all_reviews():

    view_as = request.args.get("view_as", None)
    filter_form = ReviewFilterForm()
    # (1) filter form configuration
    
    if current_user.role.can_be_reviewee:
        filter_form.reviewers.choices = sorted([
            (user.id.hex, user.username)
            for user in current_user.get_potential_reviewers()
        ],key=lambda x:x[0])
    else:
        filter_form.reviewers.render_kw = {'disabled':'disabled'}
    if current_user.role.can_be_reviewer:
        filter_form.reviewees.choices = sorted([
            (user.id.hex, user.username)
            for user in current_user.get_potential_reviewees()
        ], key=lambda x:x[0])
    else:
        filter_form.reviewees.render_kw = {'disabled':'disabled'}
    filter_form.groups.choices = sorted([
        (group.id.hex, group.name)
        for group in [current_user.internal_group ]+ current_user.external_groups.all()
    ],key=lambda x:x[0])

    if view_as == 'reviewer' and current_user.role.can_be_reviewer:
        filter_form.reviewers.choices = [(current_user.id.hex, current_user.username)]
        filter_form.reviewers.render_kw = {'disabled':'disabled'}
    elif view_as == 'reviewee' and current_user.role.can_be_reviewee:
        filter_form.reviewees.choices = [(current_user.id.hex, current_user.username)]
        filter_form.reviewees.render_kw = {'disabled':'disabled'}
    

    filter_form.epas.choices = [
        (str(epa.id), epa.desc)
        for epa in EPA.query.with_entities(EPA.id, EPA.desc).all()
    ]

    # (2) fitler form on submit
    if filter_form.validate_on_submit():
        filters_json = json.dumps(
            {
                field.name: field.data
                for field in filter_form
                if field.type not in ["SubmitField", "CSRFTokenField"]
            },
            default=lambda x: str(x) if isinstance(x, datetime.date) else "",
        )
        return redirect(url_for("view_all_reviews", filters_json=filters_json))
    
    sort_entity = Review.create_time.desc()
    filtering_clause = []

    if view_as == 'reviewer':
        filtering_clause.append(Review.reviewer_id == current_user.id)
    elif view_as == 'reviewee':
        filtering_clause.append(Review.reviewee_id == current_user.id)

    # filters handling. Should pull into a function
    filters_json = request.args.get("filters_json", None)
    if filters_json:
        filters = json.loads(filters_json)
        reviewees = filters.get("reviewees", [])
        reviewers = filters.get("reviewers", [])
        groups = filters.get("groups", [])
        implement_date_start = filters.get("implement_date_start", None)
        implement_date_end = filters.get("implement_date_end", None)
        epas = filters.get("epas",[])
        sort_key = filters.get("sort_key", 'create_time')

        # TODO: could refactor this in factory
        # check again for if option in get parameter is valid for this user. 
        # cuz Some hackers may hit the url directly, rather use the form to genereate url
        # TODO: make 'select all'(+ clear all selected) in select be handle in FE
        if set(reviewees) & set([reviewee[0] for reviewee in filter_form.reviewees.choices]):
            filter_form.reviewees.data = reviewees
            filtering_clause.append(Review.reviewee_id.in_(reviewees))

        if set(reviewers) & set([reviewer[0] for reviewer in filter_form.reviewers.choices]):
            filter_form.reviewers.data = reviewers
            filtering_clause.append(Review.reviewer_id.in_(reviewers))
            
            
        if set(groups) & set([group[0] for group in filter_form.groups.choices]):
            
            filter_form.groups.data = groups
            selected_groups = Group.query.filter(Group.id.in_(groups)).all()
            selected_user_ids = list(
                set(
                    [
                        user.id.hex
                        for group in selected_groups
                        for user in group.internal_users.all() + group.external_users
                    ]
                )
            )
            filtering_clause.append(
                or_(
                    Review.reviewer_id.in_(selected_user_ids),
                    Review.reviewee_id.in_(selected_user_ids),
                )
            )
        if implement_date_start:
            filter_form.implement_date_start.data = datetime.date.fromisoformat(implement_date_start)
            filtering_clause.append(
                Review.implement_date >= datetime.date.fromisoformat(implement_date_start)
            )
            
        if implement_date_end:
            filter_form.implement_date_end.data = datetime.date.fromisoformat(implement_date_end)
            filtering_clause.append(
                Review.implement_date < datetime.date.fromisoformat(implement_date_end)
            )
        if set(epas) & set([epa[0] for epa in filter_form.epas.choices]):
            filter_form.epas.data = epas
            filtering_clause.append(
                Review.epa_id.in_(epas)
            )
                
        
        if sort_key:
            filter_form.sort_key.data = sort_key
            if sort_key == "EPA":
                sort_entity = Review.epa_id
            elif sort_key == "implement_date":
                sort_entity = Review.implement_date.desc()
            elif sort_key == "complete":
                sort_entity = Review.complete

    cur_page_num = int(request.args.get("page") or 1)

    all_user_related_reviews_q = Review.query
    if not current_user.role.is_manager:
        all_user_related_reviews_q = all_user_related_reviews_q.filter(
            or_(Review.reviewer == current_user, Review.reviewee == current_user),
            Review.complete == True
        )
    if filtering_clause:
        all_user_related_reviews_q = all_user_related_reviews_q.filter(
            *filtering_clause
        )
    all_user_related_reviews_q = all_user_related_reviews_q.order_by(sort_entity)
    all_user_related_reviews = all_user_related_reviews_q.paginate(
        page=cur_page_num,
        per_page=int(current_app.config["REVIEW_PER_PAGE"]),
        error_out=False,
    )
    next_url = (
        url_for(
            "view_all_reviews",
            page=all_user_related_reviews.next_num,
            filters_json=filters_json,
            view_as=view_as
        )
        if all_user_related_reviews.has_next
        else None
    )
    prev_url = (
        url_for(
            "view_all_reviews",
            page=all_user_related_reviews.prev_num,
            filters_json=filters_json,
            view_as=view_as
        )
        if all_user_related_reviews.has_prev
        else None
    )
    return render_template(
        "view_reviews.html",
        title="查看所有評核",
        reviews=all_user_related_reviews.items,
        filter_form=filter_form,
        next_url=next_url,
        prev_url=prev_url,
        view_as=view_as
    )

def get_epa_linkages():
    entities = [
        EPA.name.label('epa'),
        MilestoneItemEPA.min_epa_level,
        MilestoneItem.code.label('milestone_item_code')
    ]
    mies = MilestoneItemEPA.query.join(EPA).join(MilestoneItem).with_entities(*entities).order_by(MilestoneItemEPA.min_epa_level).all()
    mies_dict = dict()
    for mie in mies:
        if not mie.epa in mies_dict.keys():
            mies_dict[mie.epa] = {'milestone_item_codes':[mie.milestone_item_code], 'min_epa_level':[mie.min_epa_level]}
        else:
            mies_dict[mie.epa]['milestone_item_codes'].append(mie.milestone_item_code)
            mies_dict[mie.epa]['min_epa_level'].append(mie.min_epa_level)
    mies_json = json.dumps(mies_dict)
    mis = MilestoneItem.query.with_entities(MilestoneItem.code.label('milestone_item_code'), MilestoneItem.content.label('milestone_item_content')).all()
    mis_json = json.dumps({mi['milestone_item_code']:mi['milestone_item_content']  for mi in mis})

    epa_milestones = Milestone.query.join(MilestoneItem).join(MilestoneItemEPA).join(EPA).with_entities(EPA.name.label('epa'), Milestone.name.label('milestone_name'), Milestone.desc.label('milestone_desc')).distinct().order_by(EPA.name, Milestone.name).all()
    epa_milestone_dict = dict()
    for em in epa_milestones:
        if not em.epa in epa_milestone_dict.keys():
            epa_milestone_dict[em.epa] = []
        epa_milestone_dict[em.epa].append({'name':em.milestone_name, 'desc':em.milestone_desc})
    epa_milestone_json = json.dumps(epa_milestone_dict)

    return mies_json, mis_json, epa_milestone_json

@login_required
def index():
    view_as = request.args.get('view_as', None)
    # show notification and del notification
    if not view_as:
        for notification in current_user.notifications:
            flash( Markup(f'{notification.subject}: {notification.msg_body}') , 'alert-info',)
            db.session.delete(notification)
        db.session.commit()
    if current_user.can_request_review() and current_user.can_create_review() and not view_as:
        todos = {
            '暫存評核': current_user.get_draft_request_reviews(),
            '等待老師評核': current_user.get_unfin_request_reviews(),
            '暫存評核(老師)': current_user.get_draft_reviews(),
            '未完成評核(老師)':current_user.get_unfin_reviews()
            }
    elif view_as == 'reviewer' or (current_user.can_create_review() and not current_user.can_request_review()):
        todos = {
            '暫存評核': current_user.get_draft_reviews(),
            '未完成評核': current_user.get_unfin_reviews(),
            }
    elif view_as == 'reviewee' or (not current_user.can_create_review() and current_user.can_request_review()):
        todos = {
            '暫存評核': current_user.get_draft_request_reviews(),
            '等待老師評核': current_user.get_unfin_request_reviews(),
            }
    return render_template(
        "index.html",
        title="首頁" if not view_as else '未完成評核(老師)' if view_as == 'reviewer' else '未完成評核(學生)',
        todos=todos
    )


def login():
    # already login
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u is None or not u.check_password(form.password.data):
            flash("帳號或密碼錯誤", "alert-danger")
            return redirect(url_for("login"))
        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("index"))
    return render_template("login.html", title="登入", form=form)


def logout():
    logout_user()
    return redirect(url_for("login"))




def register():
    line_new_user_token = request.args.get("line_new_user_token", None)
    if line_new_user_token:
        try:
            line_new_user = LineNewUser.verify_jwt(line_new_user_token)
            line_user_profile = line_bot_api.get_profile(line_new_user.line_userId)
        except Exception as e:
            flash(
                "抱歉，無法辨識你的 Line 帳號，你還是可以繼續註冊，或退出後再次聯繫EPA Line官方帳號索取註冊連結",
                "alert-warning",
            )
            print(e)
            line_user_profile = None
    else:
        line_user_profile = None

    if current_user.is_authenticated:
        if not current_user.line_userId:
            if line_user_profile:
                current_user.line_userId = line_new_user.line_userId
                db.session.commit()
                flash("已將你的帳號與line帳號綁定", "alert-success")
                return redirect(url_for("index"))
            else:
                flash("綁定失敗，你的line帳號似乎出了點問題，請聯絡系統管理者", "alert-danger")
        return redirect(url_for("index"))
    # (1) form configuration
    form = RegisterForm()
    registerable_roles = (
        Role.query.filter(Role.is_manager == False)
        .with_entities(Role.id, Role.name)
        .all()
    )
    form.role.choices = [(role.id.hex, role.name) for role in registerable_roles]
    form.bindline.data = True if line_user_profile else False
    all_groups = Group.query.all()
    form.internal_group.choices = [(group.id.hex, group.name) for group in all_groups]
    form.external_groups.choices = [(group.id.hex, group.name) for group in all_groups]

    # (2) on submit handling
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.role = Role.query.filter(
            Role.id == form.role.data, Role.is_manager == False
        ).first()
        if line_user_profile and form.bindline.data:
            user.line_userId = line_user_profile.user_id
            db.session.delete(line_new_user)
        user.internal_group = Group.query.get(form.internal_group.data)

        for group_id in form.external_groups.data:
            user.external_groups.append(Group.query.get(group_id))

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(
            Markup(
                f'註冊成功，請以帳號密碼登入<br>如果你有綁定Line帳號，歡迎透過 <a href="https://line.me/R/ti/p/{linebotinfo.basic_id}">Line官方帳號</a>使用快速登入功能'
            ),
            "alert-success",
        )
        return redirect(url_for("login"))

    if not line_user_profile:
        flash(
            Markup(
                f'EPA系統可以透過 line 通知你，你可以考慮 <a href="https://line.me/R/ti/p/{linebotinfo.basic_id}">點此透過line註冊</a>'
            ),
            "alert-info",
        )
    return render_template(
        "register.html",
        title="註冊新帳號",
        form=form,
        line_user_profile=line_user_profile,
        linebotinfo=linebotinfo,
    )

def page_not_found(e):
    return render_template("404.html"), 404

def get_stats_by_user(user):
    entities = [ Review.epa_id, ReviewScore.value.label('score')]
    user_reviews = Review.query.join(EPA).join(ReviewScore).filter(Review.reviewee_id == user.id ).with_entities(*entities).all()

    epas = EPA.query.with_entities(EPA.id.label('epa_id'), EPA.name, EPA.desc).all()
    milestones = Milestone.query.with_entities(Milestone.name, Milestone.id.label('milestone_id'), Milestone.desc).all()
    corecompetences = CoreCompetence.query.with_entities(CoreCompetence.name, CoreCompetence.id.label('corecompetence_id'),CoreCompetence.desc).all()

    re_dict = dict()
    if len(user_reviews) == 0:
        re_dict['epa_stats'] = {epa.name: {'id': epa.epa_id, 'score': 0, 'review_cnt':0, 'desc': epa.desc} for epa in epas}
        re_dict['milestone_stats'] = {ms.name: {'id': ms.milestone_id, 'score': 0, 'desc': ms.desc} for ms in milestones}
        re_dict['corecompetence_stats'] = {cc.name: {'id': cc.corecompetence_id, 'score': 0, 'desc': cc.desc} for cc in corecompetences}
        re_dict['milestone_item_checking'] = dict()
        return re_dict

    import pandas as pd
    review_df = pd.DataFrame(user_reviews,columns=user_reviews[0].keys())
    milestone_items = MilestoneItem.query.join(Milestone).with_entities(MilestoneItem.id.label('milestone_item_id'), MilestoneItem.level, Milestone.name.label('milestone'), MilestoneItem.code, MilestoneItem.content)
    
    epa_df = pd.DataFrame(epas, columns=epas[0].keys())
    milestone_df = pd.DataFrame(milestones, columns=milestones[0].keys())
    milestone_item_df = pd.DataFrame(milestone_items, columns=milestone_items[0].keys())
    corecompetence_df = pd.DataFrame(corecompetences, columns=corecompetences[0].keys())
    linkage_entites = [
        EPA.id.label('epa_id'),
        MilestoneItem.id.label('milestone_item_id'),
        MilestoneItem.level.label('milestone_item_level'),
        MilestoneItemEPA.min_epa_level,
        Milestone.id.label('milestone_id'),
        CoreCompetence.id.label('corecompetence_id')
        ]
    linkage = MilestoneItemEPA.query.join(EPA).join(MilestoneItem).join(Milestone).join(CoreCompetence).with_entities(*linkage_entites).all()
    linkage_df = pd.DataFrame(linkage, columns=linkage[0].keys())

    # epa
    grouped = review_df.groupby('epa_id')
    epa_stats_df = pd.concat([
        grouped['score'].max().rename('score'),
        grouped['score'].count().rename('review_cnt')
        ],axis='columns')
    epa_stats_df = pd.merge(epa_stats_df,epa_df, on='epa_id', how='outer').fillna(0)
    epa_stats = epa_stats_df.rename({'epa_id':'id'},axis='columns').set_index('name').T.to_dict()

    milestoneitem_stats_df = pd.merge(epa_stats_df[['epa_id','score']], linkage_df, on='epa_id')
    milestoneitem_stats_df['checked'] = milestoneitem_stats_df['score'] > milestoneitem_stats_df['min_epa_level']
    
    grouped = milestoneitem_stats_df.groupby(['milestone_id','milestone_item_level'])
    milestone_level_stats_df = pd.concat([
        grouped['checked'].all().rename('all'),
        grouped['checked'].any().rename('any'),
    ],axis='columns').unstack(-1)
    milestone_level_stats_df.columns = [f'{col[0]}_{col[1]}' for col in milestone_level_stats_df.columns.values]
    def cal_milestone_score(milestone_ser):
        score = 0
        for i in range(1,6):
            if milestone_ser[f'all_{i}']:
                score+=1
            else:
                if milestone_ser[f'any_{i}']:
                    score+=0.5
                break
        if score == 0 and any([f'any_{i}' for i in range(1,6)]):
            score = 0.5
        return score
        
    milestone_stats_df = milestone_level_stats_df.apply(cal_milestone_score,axis='columns').rename('score').reset_index()
    ms2cc = linkage_df[['milestone_id','corecompetence_id']].drop_duplicates().set_index('milestone_id')['corecompetence_id']
    milestone_stats_df['corecompetence_id'] = milestone_stats_df['milestone_id'].map(ms2cc)

    milestone_stats = milestone_stats_df[['milestone_id','score']]
    corecompetence_stats = milestone_stats_df.groupby('corecompetence_id')['score'].mean().reset_index()
    
    milestone_stats = pd.merge(milestone_stats, milestone_df, on='milestone_id',how='outer').fillna(0).drop(['milestone_id'],axis='columns').set_index('name').T.to_dict()
    corecompetence_stats = pd.merge(corecompetence_stats, corecompetence_df, on='corecompetence_id',how='outer').drop(['corecompetence_id'],axis='columns').fillna(0).set_index('name').T.to_dict()
    milestone_item_checking = pd.merge(milestoneitem_stats_df.groupby('milestone_item_id')['checked'].any().reset_index(), milestone_item_df , on='milestone_item_id').drop(['milestone_item_id'],axis='columns')#.set_index(['code']).T.to_dict()
    
    milestone_item_checking_dict = dict()
    for _, row in milestone_item_checking.iterrows():
        if not row['milestone'] in milestone_item_checking_dict.keys():
            milestone_item_checking_dict[row['milestone']] = {i:[] for i in range(1,6)}
        milestone_item_checking_dict[row['milestone']][row['level']].append(row.loc[['code','checked','content']].to_dict())
    for key in milestone_item_checking_dict.keys():
        for level in range(1,6):
            milestone_item_checking_dict[key][level].sort(key=lambda x:int(x['code'].split(".")[-1]))
    
    re_dict['epa_stats'] = epa_stats
    re_dict['milestone_stats'] = milestone_stats
    re_dict['corecompetence_stats'] = corecompetence_stats
    re_dict['milestone_item_checking'] = milestone_item_checking_dict

    return re_dict

def get_corecompetence_stats_by_user(user):
    pass

@login_required
def progress_stat():
    query_user_id = request.args.get("username", None)
    if current_user.role.is_manager and query_user_id:
        user = User.query.filter(User.username == "username").first()
    else:
        user = current_user
    
    user_stats = get_stats_by_user(user)
    epa_stats = user_stats['epa_stats']
    corecompetence_stats_json = json.dumps(user_stats['corecompetence_stats'])
    milestone_stats_json = json.dumps(user_stats['milestone_stats'])
    milestone_item_checking_json = json.dumps(user_stats['milestone_item_checking'])
    for key in epa_stats:
        epa_stats[key].update({
            'img_src':f'{key[3:].zfill(2)}.svg',
            'url':url_for('view_all_reviews',view_as='reviewee',filters_json=json.dumps({"epas":[str(epa_stats[key]['id'])]}))
            })
    epa_stats=dict(sorted(epa_stats.items(),key=lambda x:int(x[0].split(" ")[0][3:])))

    return render_template(
        "progress_stat.html",
        title=user.username,
        user=user,
        epa_stats=epa_stats,
        corecompetence_stats_json=corecompetence_stats_json,
        milestone_stats_json=milestone_stats_json,
        milestone_item_checking_json=milestone_item_checking_json
    )

@login_required
def edit_profile():
    query_user_id = request.args.get("query_user_id", None)

    if current_user.role.is_manager and query_user_id:
        user = User.query.get(query_user_id)
    else:
        user = current_user

    if user.line_userId:
        try:
            line_user_profile = line_bot_api.get_profile(user.line_userId)
        except Exception as e:
            print(e)
    else:
        print("no line_userId")
        line_user_profile = None

    # (1) form configuration
    form = EditProfileForm()
    all_groups = Group.query.with_entities(Group.id, Group.name).all()
    form.role.render_kw = {"disabled": "disabled"}
    form.internal_group.choices = [(group.id.hex, group.name) for group in all_groups]
    form.external_groups.choices = [(group.id.hex, group.name) for group in all_groups]

    # (2) on submit handling
    if form.validate_on_submit():
        if not form.bindline.data:
            user.line_userId = None
        user.email = form.email.data
        user.internal_group = Group.query.get(form.internal_group.data)
        user.external_groups = [
            Group.query.get(group_id) for group_id in form.external_groups.data
        ]
        db.session.commit()
        flash("資料更新成功", "alert-success")
        return redirect(url_for("edit_profile"))
    # (3) prefill
    form.bindline.data = True if user.line_userId else False
    form.email.data = user.email
    form.role.choices = [
        ("", user.role.name)
    ]  # for dummy field, make sure you have default choice in form class definition
    form.internal_group.data = user.internal_group.id.hex
    form.external_groups.data = [ext_group.id.hex for ext_group in user.external_groups]

    return render_template(
        "edit_profile.html",
        title=user.username,
        user=user,
        form=form,
        linebotinfo=linebotinfo,
        line_user_profile=line_user_profile,
    )


def reset_password_request():
    # if already login, directly reset
    if current_user.is_authenticated:
        token = current_user.get_jwt()
        return redirect(url_for("password_reset", token=token))

    form = PasswdResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("已發送密碼重置連結到你的 line 或 email", "alert-info")
            token = user.get_jwt()
            url_password_reset = url_for("password_reset", token=token, _external=True)
            subject = "[EPA]密碼重設"
            msg_body = f"{user.username}你好，\n你的密碼重設連結為{url_password_reset}"
            try:
                user.send_message(subject=subject, msg_body=msg_body,channels=["email"])
            except Exception as e:
                print(e)
        else:
            flash("找不到這個這個email註冊的使用者", "alert-warning")
        return redirect(url_for("login"))
    return render_template("password_reset_request.html", form=form)


def password_reset(token):
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    user = User.verify_jwt(token)
    if not user:
        flash("你哪來這個 Token  是我給的嗎？", "alert-info")
        return redirect(url_for("login"))
    form = PasswdResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("密碼重設完成，記得下次用新密碼登入喔！", "alert-info")
        subject = "[EPA通知]密碼已重設"
        msg_body = f"{user.username}你好，你的EPA密碼已重設，如果您並未發出重設密碼請求，請立即聯絡管理員"
        user.send_message(subject=subject, msg_body=msg_body,channels=['email','line'])
        return redirect(url_for("login"))
    return render_template("password_reset.html", title="Password Reset", form=form)
    