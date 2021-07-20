import datetime
import random
import os
from app import db, create_app  # 此時db仍沒有連上engine，因為app在  __init__.py 中只有初始化SQLAlchemy空物件而已
app = create_app('development') # 這裏db也還是沒有連上，只是創造出app 環境而已
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
    role = Role(name=f"住院醫師-R{i}", desc=f"住院醫師-R{i} desc", can_be_reviewee = True)
    db.session.add(role)
role = Role(name=f"住院醫師-R5(總醫師)", desc="住院醫師-R5 desc", can_be_reviewee=True, can_be_reviewer=True)
db.session.add(role)
role = Role(name=f"主治醫師", desc="主治醫師 desc",  can_be_reviewer=True)
db.session.add(role)
role = Role(name=f"醫院管理者", desc="醫院管理者 desc", is_manager=True)
db.session.add(role)

# #EPA
epa_desc_list = [
    "EPA01 呼吸道評估與處置(Airway)",
    "EPA02 異物評估與處置(FB)",
    "EPA03 出血評估與處置(Bleeding)",
    "EPA04 眩暈評估與處置(Vertigo)",
    "EPA05 感染症評估與處置(Infection)",
    "EPA06 頭頸部(含口腔)腫瘤評估與處置(H&N)",
    "EPA07 耳部與聽力疾病評估與處置(Ear/Hearing)",
    "EPA08 鼻部與鼻竇疾病評估與處置(Nose/Sinus)",
    "EPA09 咽喉部(音聲、語言、吞嚥)疾病評估與處置(Larynx)",
    "EPA10 睡眠呼吸障礙評估與處置(SDB)",
    "EPA11 顏面整形重建評估與處置(Plasty)",
    ]
for epa_desc in epa_desc_list:
    epa = EPA(name=epa_desc.split(" ")[0].replace("A0","A"), desc=epa_desc)
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
    epa_name = epa_name[:3] + epa_name[3:]
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
review_score_desc = ["Level 1  只能觀察，不能操作(老師在場)","Level 2  需在老師直接指導下執行(老師在場)", "Level 3  需協助時立即找得到老師指導(老師在附近)","Level 4  可獨立執行，僅需事後督導","Level 5  可指導別人"]
for i in range(len(review_score_name)):
    db.session.add(ReviewScore(value=i+1, name=review_score_name[i], desc=review_score_desc[i]))

db.session.commit()


#Group
group_names = [
    "基隆長庚紀念醫院(基長)",
"台大醫院(台大)",
"三軍總醫院(三總)",
"臺北榮民總醫院(北榮)",
"馬偕紀念醫院(馬偕)",
"國泰綜合醫院(國泰)",
"臺北市立聯合醫院(北市聯)",
"萬芳醫院(萬芳)",
"新光吳火獅紀念醫院(新光)",
"臺北醫學大學附設醫院(北醫)",
"振興醫院(振興)",
"亞東紀念醫院(亞東)",
"耕莘醫院(耕莘)",
"台北慈濟醫院(北慈)",
"雙和醫院(雙和)",
"林口長庚紀念醫院(林長)",
"臺中榮民總醫院(中榮)",
"中國醫藥大學附設醫院(中國醫)",
"中山醫學大學附設醫院(中山醫)",
"光田綜合醫院(光田)",
"童綜合醫院(童綜合)",
"台中慈濟醫院(中慈)",
"彰化基督教醫院(彰基)",
"台大醫院雲林分院(雲林台大)",
"嘉義長庚紀念醫院(嘉長)",
"成大醫院(成大)",
"奇美醫院(奇美)",
"國軍高雄總醫院(國高總)",
"高雄醫學大學附設醫院(高醫)",
"高雄榮民總醫院(高榮)",
"高雄長庚紀念醫院(高長)",
"義大醫院(義大)",
"羅東博愛醫院 (羅東)",
"花蓮慈濟醫院 (花慈)",
]

for name in group_names:
    db.session.add(Group(name=name, desc=name+"_desc"))
db.session.commit()

# User
# admin
all_groups = Group.query.all()
all_roles = Role.query.filter(Role.is_manager == False).all()
for i in range(200):
    user = User()
    
    user.role = all_roles[int(random.random()*len(all_roles))]
    
    fake_groups = []
    for j in range(int(random.random()*3)+1):
        fake_groups.append(all_groups[int(random.random()*len(all_groups))])
    fake_groups = list(set(fake_groups))
    user.internal_group = fake_groups[0]
    for j in range(1, len(fake_groups)):
        user.external_groups.append(fake_groups[j])
    user.username = fake_groups[0].name+"_"+user.role.name+"_"+str(i)
    user.set_password(user.username)    
    db.session.add(user)

db.session.commit()

# # use "append" to resolve bridging table
all_users = User.query.all()
# notifications
for i in range(10):
    notification = Notification(subject=f"test note {i}",msg_body=f'test note body {i}')
    notification.user = all_users[int(random.random()*len(all_users))]
    db.session.add(notification)
db.session.commit()

# ask review
all_users = User.query.all()

all_locations = Location.query.all()
all_epa = EPA.query.all()
review_source_req = ReviewSource.query.filter(ReviewSource.name=='request').first()
review_source_new = ReviewSource.query.filter(ReviewSource.name=='new').first()
for i in range(20):
    
    user = all_users[int(random.random()*len(all_users))]
    review = Review()
    review.creator = user
    
    if user.can_create_review():
        review.reviewer = user
        reviewee_options = user.get_potential_reviewees()
        if len(reviewee_options) == 0:
            continue
        review.reviewee = reviewee_options[int(random.random()*len(reviewee_options))]
        review.review_source = review_source_new
        review.is_draft = True
    else:
        review.reviewee = user
        reviewer_options = user.get_potential_reviewers()
        if len(reviewer_options) == 0:
            continue
        review.reviewer = reviewer_options[int(random.random()*len(reviewer_options))]
        review.review_source = review_source_req
    
    review.location = all_locations[int(random.random()*len(all_locations))]
    review.epa = all_epa[int(random.random()*len(all_epa))]
    db.session.add(review)
db.session.commit()