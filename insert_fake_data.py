from twittor import db, create_app  # 此時db仍沒有連上engine，因為twittor在  __init__.py 中只有初始化SQLAlchemy空物件而已
app = create_app() # 這裏db也還是沒有連上，只是創造出app 環境而已
app.app_context().push()  # 把環境推入，這時候db就連上了，也可以使用with app.context():裡面再使用query

from twittor.models.tweet import Review
from twittor.models.user import User, Group, user_group
from twittor.models.fact import Location, EPA, ReviewDifficulty, ReviewScore, ReviewSource

for table_name in ["epa", "location", "user", "review_source", "review_score", "review_difficulty", "group", "user_group", "review"]:
    db.session.execute(f"DELETE from `{table_name}`;")

#EPA
epa_desc = ["EPA1(Airway) 呼吸道評估與處置", "EPA2(FB) 耳鼻喉頭頸部異物評估與處置", "EPA3(Bleeding) 耳鼻喉頭頸部出血評估與處置", "EPA4(Vertigo) 眩暈評估與處置", "EPA5(Infection) 耳鼻喉頭頸部感染症評估與處置", "EPA6(H&N) 耳鼻喉頭頸部(含口腔)腫瘤評估與處置", "EPA7(Ear/Hearing) 耳部與聽力疾病評估與處置", "EPA8(Nose/Sinus) 鼻部與鼻竇疾病評估與處置", "EPA9(Larynx) 咽喉部(音聲、語言、吞嚥)疾病評估與處置", "EPA10(SDB) 睡眠呼吸障礙評估與處置", "EPA11(Plasty) 顏面整形重建評估與處"]
for i in range(len(epa_desc)):
    db.session.add(EPA(name=f"EPA{i+1}", desc=epa_desc[i]))


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
group_name = ["耕莘醫院", "第二間醫院"]
group_desc = ["耕莘醫院的老師和學生", "第二間醫院的描述"]
for name, desc in zip(group_name, group_desc):
    db.session.add(Group(name=name, desc=desc))
db.session.commit()


# User
# use "append" to resolve bridging table
std_name = ["R1卓筱茜", "R2陳佩欣", "R3廖晨竹", "R4謝易達", "R5余瑞彬"]
for name in std_name:
    user = User(username=name, line_userId=f"line {name}", role="student")
    user.groups.append(Group.query.get(1))
    db.session.add(user)


tea_name = ["林凱南", "劉嘉銘", "梁家光", "陳正文", "王守仁", "林世倉", "張淳翔", "李嘉欣", "蘇家弘", "陳一嘉", "余瑞彬"]
for name in tea_name:
    user = User(username=name, line_userId=f"line {name}", role="teacher")
    user.groups.append(Group.query.get(1))
    user.groups.append(Group.query.get(2))
    db.session.add(user)


for name in ["only2"+name for name in std_name]:
    user = User(username=name, line_userId=f"line {name}", role="student")
    user.groups.append(Group.query.get(2))
    db.session.add(user)


for name in ["only2"+name for name in tea_name]:
    user = User(username=name, line_userId=f"line {name}", role="teacher")
    user.groups.append(Group.query.get(2))
    db.session.add(user)

db.session.commit()


# ask review
all_teachers = User.query.filter(User.role=='teacher').all()
all_users = User.query.all()
import random
all_locations = Location.query.all()
all_epa = EPA.query.all()
for i in range(1000):
    review = Review()
    review.review_source = ReviewSource.query.filter(ReviewSource.name=="request").first()
    review.reviewer = all_teachers[int(random.random()*len(all_teachers))]
    review.reviewee = all_users[int(random.random()*len(all_users))]
    review.location = all_locations[int(random.random()*len(all_locations))]
    review.epa = all_epa[int(random.random()*len(all_epa))]
    db.session.add(review)
db.session.commit()

# finished review
review = Review()
review.review_source = ReviewSource.query.filter(ReviewSource.name=="new").first()
review.reviewer = User.query.filter(User.role=='teacher').first()
review.reviewee = User.query.get(2)
review.location = Location.query.get(2)
review.epa = EPA.query.get(3)
review.review_compliment = "good job"
review.review_suggestion = "next time you should..."
review.review_difficulty = ReviewDifficulty.query.get(2)
review.review_score = ReviewScore.query.get(4)
review.complete = True

db.session.add(review)
db.session.commit()