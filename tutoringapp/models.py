from django.db import models
from django.contrib.auth.models import AbstractUser

# ------------------------定数の定義--------------------------

# UserModelの定数

# user_typeを制限
USER_TYPE_CHOICES = [("teacher", "teacher"), ("student", "student")]

# ------------------------モデルの定義--------------------------

# ユーザーのモデル。
# ユーザーは、講師ユーザーと生徒ユーザーの二種類に分類される。
# StudentModel, TeacherModelと1対1のリレーションがある
# id=1のユーザーは、ダミーユーザー。ClassModelにおいて、生徒がまだ決まっていないことを示す。
class UserModel(AbstractUser):
    user_type = models.TextField(choices=USER_TYPE_CHOICES, default="student") # ユーザーが講師か生徒かを示す
    first_name = models.TextField(default="") # ユーザーの名前
    last_name = models.TextField(default="") # ユーザーの苗字
    profile_image = models.ImageField(upload_to="", default="ProfileImage.png") # ユーザーのプロフィール画像

# 生徒のモデル
# UserModelと1対1のリレーションがある
# ClassModelと1対多のリレーションがある
class StudentModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)

# 講師のモデル
# UserModelと1対1のリレーションがある
# ClassModelと1対多のリレーションがある
class TeacherModel(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE) 

# 授業のモデル
# StudentModel, TeacherModelと1対多のリレーションがある
class ClassModel(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE) # 生徒ユーザー
    teacher = models.ForeignKey(TeacherModel, on_delete=models.CASCADE) # 講師ユーザー
    datetime = models.DateTimeField() # 授業の日付、時刻


