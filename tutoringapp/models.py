from django.db import models
from django.contrib.auth.models import AbstractUser

import datetime


# ------------------------定数の定義--------------------------

# UserModelの定数

# user_typeを制限
USER_TYPE_CHOICES = [("teacher", "teacher"), ("student", "student")]

USERS_RANK_CHOICES = [("bronze", "bronze"), ("silver", "silver"), ("gold", "gold"), ("diamond", "diamond")]

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
    start_datetime = models.DateTimeField(auto_now_add=True)
    self_introduction = models.TextField(default="")
    spent_time = models.IntegerField(default=0) # 費やした時間(学習時間or授業をした時間)
    rank = models.TextField(choices=USERS_RANK_CHOICES, default="bronze")
    class_start_datetime = models.DateTimeField(default=datetime.datetime(2000, 1, 1)) # 最後に授業に参加した時間
    class_ending_datetime = models.DateTimeField(default=datetime.datetime(2000, 1, 1)) # 最後に授業を終了した時間

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


