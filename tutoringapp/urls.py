from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"), # ログインページ
    path("logout/", views.logout_view, name="logout"), # ログアウトページ
    path("tutoring/<int:class_id>/", views.tutoring_view, name="tutoring"), # 授業ページ
    path("signup_studentaccount/", views.signup_studentaccount_view, name="signup_studentaccount"), # 生徒アカウントを作成するページ
    path("reserve/", views.reserve_view, name="reserve"), # どの先生を予約するかを決めるページ
    path("choose_learning_datetime/<int:teacher_id>/", views.choose_reserved_class_datetime_view, name="choose_reserved_class_datetime"), # 授業の時間を選択するページ。teacher_idには予約する先生のユーザーidが入る。
    path("signup_teacheraccount/", views.signup_teacheraccount_view, name="signup_teacheraccount"), # 講師アカウントを作成するページ
    path("manage_schedule/", views.manage_schedule_view, name="manage_schedule"), # 講師のスケジュールを管理するページ
]