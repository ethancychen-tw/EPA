import datetime
import random

from app import db, create_app  # 此時db仍沒有連上engine，因為app在  __init__.py 中只有初始化SQLAlchemy空物件而已
app = create_app() # 這裏db也還是沒有連上，只是創造出app 環境而已
app.app_context().push()  # 把環境推入，這時候db就連上了，也可以使用with app.context():裡面再使用query

from app.models.review import Review, Location, EPA, ReviewDifficulty, ReviewScore, ReviewSource, Milestone, CoreCompetence
from app.models.user import User, Group, user_externalgroup, Role

for table_name in ["epa", "role","location",  "review_source", "review_score", "review_difficulty", "users", "groups", "user_externalgroup", "reviews", "corecompetence", 'epa_milestone','milestone']:
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

#EPA
epa_desc = ["EPA1(Airway) 呼吸道評估與處置", "EPA2(FB) 耳鼻喉頭頸部異物評估與處置", "EPA3(Bleeding) 耳鼻喉頭頸部出血評估與處置", "EPA4(Vertigo) 眩暈評估與處置", "EPA5(Infection) 耳鼻喉頭頸部感染症評估與處置", "EPA6(H&N) 耳鼻喉頭頸部(含口腔)腫瘤評估與處置", "EPA7(Ear/Hearing) 耳部與聽力疾病評估與處置", "EPA8(Nose/Sinus) 鼻部與鼻竇疾病評估與處置", "EPA9(Larynx) 咽喉部(音聲、語言、吞嚥)疾病評估與處置", "EPA10(SDB) 睡眠呼吸障礙評估與處置", "EPA11(Plasty) 顏面整形重建評估與處置"]
epa_milestones = [
    ["PC2","PC3","PC5","MK1","MK3","MK4",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#1
    ["PC2","PC5","MK1","MK3",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#2
    ["PC2","PC5","MK1",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#3
    ["PC7","MK2","MKA1",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#4
    ["PC1","PC2","PC8","PCA1","MK1","MK3",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#5
    ["PC1",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#6
    ['SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#7
    ["PC2","PC5","PC6","MK1","MK4",'SBP1','PBLI1','PBLIN2','PROF','ICS1','ICSN2'],#8
    ["PC2", "MK1", "MK3",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#9
    ["PC3","MK4",'SBP1','SBP2','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#10
    ["PC2","PC5","PC6",'SBP1','PBLI1','PBLIN2','PROF','ICS1','ICSN1','ICSN2'],#11

]
for i in range(len(epa_desc)):
    epa = EPA(name=f"EPA{i+1}", desc=epa_desc[i])
    for ms in epa_milestones[i]:
        epa.milestones.append(Milestone.query.filter(Milestone.name==ms).first())
    db.session.add(epa)
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

# # finished review
# review = Review()
# review.review_source = ReviewSource.query.filter(ReviewSource.name=="new").first()
# review.reviewer = User.query.join(Role).filter(Role.name=='主治醫師').first()
# review.reviewee = User.query.get(2)
# review.location = Location.query.get(2)
# review.epa = EPA.query.get(3)
# review.review_compliment = "good job"
# review.review_suggestion = "next time you should..."
# review.review_difficulty = ReviewDifficulty.query.get(2)
# review.review_score = ReviewScore.query.get(4)
# review.complete = True

# db.session.add(review)
# db.session.commit()