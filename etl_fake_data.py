import datetime
import random

from app import db, create_app  # 此時db仍沒有連上engine，因為app在  __init__.py 中只有初始化SQLAlchemy空物件而已
app = create_app() # 這裏db也還是沒有連上，只是創造出app 環境而已
app.app_context().push()  # 把環境推入，這時候db就連上了，也可以使用with app.context():裡面再使用query

from app.models.review import Review, Location, ReviewDifficulty, ReviewScore, ReviewSource, Milestone, CoreCompetence, MilestoneItemEPA, EPA, MilestoneItem
from app.models.user import User, Group, Role, Notification

for table_name in [
    "epa", "corecompetence",'milestone','milestone_item', "milestone_item_epa",
     "role", 
     "reviews", "location",  "review_source", "review_score", "review_difficulty", 
     "users", "groups", "user_externalgroup",  'notifications']:
    db.session.execute(f"TRUNCATE TABLE \"{table_name}\" RESTART IDENTITY CASCADE ;")# RESTART IDENTITY would reset id starting from 1, cascade would del related rows in other tables

# Role
for i in range(1,5):
    role = Role(name=f"住院醫師-R{i}", desc=f"住院醫師-R{i} desc", can_request_review=True, can_create_and_edit_review=False, is_manager=False)
    db.session.add(role)
role = Role(name=f"住院醫師-R5(總醫師)", desc="住院醫師-R5 desc", can_request_review=True, can_create_and_edit_review=True, is_manager=False)
db.session.add(role)
role = Role(name=f"主治醫師", desc="主治醫師 desc", can_request_review=False, can_create_and_edit_review=True, is_manager=False)
db.session.add(role)
role = Role(name=f"醫院管理者", desc="醫院管理者 desc", can_request_review=True, can_create_and_edit_review=True, is_manager=True)
db.session.add(role)

# #EPA
epa_desc = [
    "EPA01(Airway) 呼吸道評估與處置",
    "EPA02(FB) 耳鼻喉頭頸部異物評估與處置",
    "EPA03(Bleeding) 耳鼻喉頭頸部出血評估與處置",
    "EPA04(Vertigo) 眩暈評估與處置",
    "EPA05(Infection) 耳鼻喉頭頸部感染症評估與處置",
    "EPA06(H&N) 耳鼻喉頭頸部(含口腔)腫瘤評估與處置",
    "EPA07(Ear/Hearing) 耳部與聽力疾病評估與處置",
    "EPA08(Nose/Sinus) 鼻部與鼻竇疾病評估與處置",
    "EPA09(Larynx) 咽喉部(音聲、語言、吞嚥)疾病評估與處置",
    "EPA10(SDB) 睡眠呼吸障礙評估與處置",
    "EPA11(Plasty) 顏面整形重建評估與處置"]
for i in range(len(epa_desc)):
    epa = EPA(name=f"EPA{str(i+1).zfill(2)}", desc=epa_desc[i])
    db.session.add(epa)
db.session.commit()

# corecompetence
corecompetence_names = ['PC','MK','PROF','ICS','PBLI','SBP']
for corecompetence in corecompetence_names:
    db.session.add(CoreCompetence(name=corecompetence, desc=f"desc for {corecompetence}"))
db.session.commit()

# milestone
milestone_names = ['PC1', 'PC2', 'PC3','PC5', 'PC6', 'PC7','PC8','PCA1','MK1','MK2','MK3','MK4','MKA1','SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2']
for milestone in milestone_names:
    c = CoreCompetence.query.filter(CoreCompetence.name.like(milestone[:2]+"%")).first()
    m = Milestone(name=milestone, desc=f"desc for {milestone}")
    m.corecompetence = c
    db.session.add(m)
db.session.commit()

# assume we have these PC1.level.item
milestone_items_lines = open("../temp/milestone_items.csv").readlines()
for line in milestone_items_lines:
    if len(line)<2:
        continue
    li = line.split(",")
    code = li[0].strip()
    level = int(code.split(".")[1])
    content = li[1].replace("\n","")
    milestone = Milestone.query.filter(Milestone.name==code.split(".")[0]).first()
    mi = MilestoneItem(code=code,level=level,content=content,milestone=milestone)
    db.session.add(mi)
db.session.commit()

# milestone_item_epa
milestone_items_epa_lines = open("../temp/milestone_item_epa.csv").readlines()
for line in milestone_items_epa_lines:
    if len(line)<2:
        continue
    li = line.split(",")
    milestone_item_code = li[0].strip()
    milestone_item = MilestoneItem.query.filter(MilestoneItem.code==milestone_item_code).first()
    epa_name = li[1].split(".")[0]
    epa_name = epa_name[:3] + epa_name[3:].zfill(2)
    epa = EPA.query.filter(EPA.name==epa_name).first()
    min_epa_level = int(li[1].split(".")[1])
    mie = MilestoneItemEPA(min_epa_level=min_epa_level,epa=epa,milestone_item=milestone_item)
    db.session.add(mie)
db.session.commit()

#location
location_name = ["outpatient", "emergency", "consultation", "ward", "surgery room"]
location_desc = ["門診", "急診", "會診時", "病房(含加護病房)", "手術室"]
for name, desc in zip(location_name, location_desc):
    db.session.add(Location(name=name, desc=desc))


#ReviewSource
review_source_name = ["request", "new"]
review_source_desc = ["請求評核", "直接評核"]
for name, desc in zip(review_source_name, review_source_desc):
    db.session.add(ReviewSource(name=name, desc=desc))


#Reviewdifficulty
review_difficulty_name = ["basic", "advanced"]
review_difficulty_desc = ["基本(常規)", "進階(非常規)"]
for i in range(len(review_difficulty_name)):
    db.session.add(ReviewDifficulty(value=i+1, name=review_difficulty_name[i], desc=review_difficulty_desc[i]))


#ReviewScore
review_score_name = ["viewonly", "direct supervision", "indirect supervision", "distance/no supervision", "supervise others"]
review_score_desc = ["只能觀察，不能操作", "須在教師直接指導下執行(direct supervision)", "需協助時立即找得到教師指導(indirect supervision)", "可獨立執行，僅需事後督導(distance/no supervision)", "可指導別人(supervise others)"]
for i in range(len(review_score_name)):
    db.session.add(ReviewScore(value=i+1, name=review_score_name[i], desc=review_score_desc[i]))

db.session.commit()


#Group
group_name = ["第一間醫院", "第二間醫院"]
group_desc = ["第一間醫院的描述", "第二間醫院的描述"]
for name, desc in zip(group_name, group_desc):
    db.session.add(Group(name=name, desc=desc))
db.session.commit()

# User
# admin
user = User(username="admin", email="epataiwan.official@gmail.com")
user.set_password("admin")
user.role = Role.query.filter(Role.name=="醫院管理者").first()
user.internal_group = Group.query.filter(Group.name=="第一間醫院").first()
user.external_groups.append(Group.query.filter(Group.name=="第二間醫院").first())
db.session.add(user)

#group1
user = User(username="G1R1", email="G1R1@epa.com")
user.set_password("G1R1")
user.role = Role.query.filter(Role.name=="住院醫師-R1").first()
user.internal_group = Group.query.filter(Group.name == "第一間醫院").first()
user.external_groups.append(Group.query.filter(Group.name == "第二間醫院").first())
db.session.add(user)

user = User(username="G1R5",email="G1R5@epa.com")
user.set_password("G1R5")
user.role = Role.query.filter(Role.name=="住院醫師-R5(總醫師)").first()
user.internal_group = Group.query.filter(Group.name == "第一間醫院").first()
db.session.add(user)

user = User(username="G1R6", email="G1R6@epa.com")
user.set_password("G1R6")
user.role = Role.query.filter(Role.name=="主治醫師").first()
user.internal_group = Group.query.filter(Group.name == "第一間醫院").first()
db.session.add(user)

# group2
user = User(username="G2R1", email="G2R1@epa.com")
user.set_password("G2R1")
user.role = Role.query.filter(Role.name=="住院醫師-R1").first()
user.internal_group = Group.query.filter(Group.name == "第二間醫院").first()
db.session.add(user)

user = User(username="G2R5",email="G2R5@epa.com")
user.set_password("G2R5")
user.role = Role.query.filter(Role.name=="住院醫師-R5(總醫師)").first()
user.internal_group = Group.query.filter(Group.name == "第二間醫院").first()
db.session.add(user)

user = User(username="G2R6", email="G2R6@epa.com")
user.set_password("G2R6")
user.role = Role.query.filter(Role.name=="主治醫師").first()
user.internal_group = Group.query.filter(Group.name == "第二間醫院").first()
user.external_groups.append(Group.query.filter(Group.name == "第二間醫院").first())
db.session.add(user)

db.session.commit()

# # use "append" to resolve bridging table

# notifications
for i in range(3):
    notification = Notification(subject=f"test note {i}",msg_body=f'test note body {i}')
    notification.user = User.query.filter(User.username == "admin").first()
    db.session.add(notification)
db.session.commit()

# ask review

all_reviewers = User.query.join(Role).filter(Role.can_create_and_edit_review == True, Role.is_manager == False).all()
all_reviewees = User.query.join(Role).filter(Role.can_request_review == True, Role.is_manager == False).all()

all_locations = Location.query.all()
all_epa = EPA.query.all()
for i in range(20):
    review = Review()
    review.implement_date = datetime.date.fromisoformat('2019-12-04') + datetime.timedelta(days=int(random.random()*(1-random.random())*1000))
    review.review_source = ReviewSource.query.filter(ReviewSource.name=="request").first()
    review.reviewer = all_reviewers[int(random.random()*len(all_reviewers))]
    reviewee_options = [user for user in all_reviewees if user != review.reviewer ]
    review.reviewee = reviewee_options[int(random.random()*len(reviewee_options))]
    review.location = all_locations[int(random.random()*len(all_locations))]
    review.epa = all_epa[int(random.random()*len(all_epa))]
    db.session.add(review)
db.session.commit()