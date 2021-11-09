from django.http import response
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse

import datetime as datetime
from urllib.parse import urlencode

from . import models


# --------------------------------関数-------------------------------

# --------バリデーション用の関数--------


# --------機能を抽出した関数--------

# getパラメータを加えたurlを作成する
# reverse_url : 遷移先のurl, get_params : getパラメーターを格納した辞書
def add_getparam_to_url(reverse_url, get_params):
    parameters = urlencode(get_params) 
    url = f"{reverse_url}?{parameters}" 

    return url


# 行のセットをリストに変換する
def change_set_to_list(record_set):

    record_list = []

    for record in record_set:
        record_list.append(record)
    
    return record_list

# filter関数の戻り値をrecord_setに渡す。filter関数の条件に一致した行があれば(重複があれば)Trueを、
# 条件に一致した行がなければ(重複がなければ)Falseを返す。
def is_duplicate(record_set):

    record_list = change_set_to_list(record_set)
    
    # リストの要素数が0であればFalse、0でなければTrueを返す
    if len(record_list):
        return True
    else:
        return False

# 一週間分の日付と時刻のリストを作成する
def create_weekly_datetime_list():
    weekly_datetime_list = [] 
    halfday_time_list = [] # 半日分の時刻のリスト

    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) # 今日の0時0分
    zero_oclock = 0
    twelve_oclock = 12
    twenty_four_oclock = 24
    zero_days_after = 0
    seven_days_after = 7

    # 半日分の時刻のリストを作成し、一週間分の日付、時刻リストに入れる。これを繰り返す。
    for i in range(zero_days_after, seven_days_after):

        # 半日分の時刻のリストを作成
        for j in range(zero_oclock, twelve_oclock):
            halfday_time_list.append(today + datetime.timedelta(days=i, hours=j))
        
        weekly_datetime_list.append(halfday_time_list)
        halfday_time_list = []

        # 半日分の時刻のリストを作成
        for j in range(twelve_oclock, twenty_four_oclock):
            halfday_time_list.append(today + datetime.timedelta(days=i, hours=j))

        weekly_datetime_list.append(halfday_time_list)
        halfday_time_list = []

    
    return weekly_datetime_list

# 元のリストから半日分の授業を束ねたリストを含むリストを作成する
def fix_weekly_teachers_class_list(weekly_teachers_class_list):
    weekly_teachers_class_list.sort(key=lambda x:x.datetime.timestamp())
    new_weekly_teachers_class_list = []
    halfday_teachers_class_list = [] 
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) # 今日の0時0分
    zero_oclock = 0
    twelve_oclock = 12
    twenty_four_oclock = 24

    # 半日分の授業を束ねたリストを作成し、一週間分の授業リストに入れる。これを繰り返す。
    for i in range(today.day, today.day+7):

        # 半日分の授業のリストを作成
        for j in range(zero_oclock, twelve_oclock):

            for teachers_class in weekly_teachers_class_list:
                
                if teachers_class.datetime.day == i and teachers_class.datetime.hour == j:

                    halfday_teachers_class_list.append(teachers_class)
        
        new_weekly_teachers_class_list.append(halfday_teachers_class_list)
        halfday_teachers_class_list = []

        # 半日分の授業のリストを作成
        for j in range(twelve_oclock, twenty_four_oclock):

            for teachers_class in weekly_teachers_class_list:

                if teachers_class.datetime.day == i and teachers_class.datetime.hour == j:

                    halfday_teachers_class_list.append(teachers_class)
        
        new_weekly_teachers_class_list.append(halfday_teachers_class_list)
        halfday_teachers_class_list = []
    
    return new_weekly_teachers_class_list

        

# -------------------------講師・生徒共通のページ-------------------------

# ホームページ
def home_page_view(request):
    pass

# ログインページ
def login_view(request):
    pass



# ---------------------------生徒専用のページ----------------------------

# 生徒アカウント作成ページ
def signup_studentaccount_view(request):
    pass

# 予約した授業を表示
# どの先生の授業を予約するかを決める
def reserve_view(request):

    # 生徒の場合
    if request.user.is_authenticated and request.user.user_type == "student":

        # --------予約した授業の表示--------
        user = request.user
        student = models.StudentModel.objects.get(user=user.id)
        now_date = datetime.datetime.utcnow() 
        reserved_class_set = models.ClassModel.objects.filter(student=student.id)
        reserved_class_list = change_set_to_list(reserved_class_set)
        todays_reserved_class_list = [] 

        # 予約した授業のうち、今日受ける授業をリストに入れる
        for reserved_class in reserved_class_set:

            if reserved_class.datetime.day == now_date.day and reserved_class.datetime.hour >= now_date.hour:
                todays_reserved_class_list.append(reserved_class)
            
        todays_reserved_class_list.sort(key=lambda x:x.datetime.timestamp())

        # --------予約可能な講師の表示--------
        teacher_set = models.TeacherModel.objects.all()
        teacher_list = []

        # 予約可能な講師をteacher_listに追加する
        for teacher in teacher_set:
            teachers_class_set = models.ClassModel.objects.filter(teacher=teacher.id) 
            teachers_class_list = change_set_to_list(teachers_class_set) 
            now_date = datetime.datetime.now()

            for teachers_class in teachers_class_list:

                if now_date.day <= teachers_class.datetime.day <= now_date.day+6:
                    teacher_list.append(teacher)
                    break
        
        now_date = datetime.datetime.utcnow() # 9時間分の時間のずれを修正

        return render(request, "reserve.html", {"todays_reserved_class_list": todays_reserved_class_list, "teacher_list" : teacher_list, "now_date" : now_date})
    
    # 講師の場合
    elif request.user.is_authenticated and request.user.user_type == "teacher":
        pass

    # ログインしていない場合
    else:
        pass

# 授業の時間を選択する
# teacher_id : 講師のUserModelのid列の値
# 注意点 : DBから取り出されるDatetimeインスタンスのタイムゾーンはUTC
def choose_reserved_class_datetime_view(request, teacher_id):

    # 生徒の場合
    if request.user.is_authenticated and request.user.user_type == "student":

        if request.method == "GET":
            user = request.user
            student = models.StudentModel.objects.get(user=user.id) 
            teacher = models.TeacherModel.objects.get(user=teacher_id) 

            weekly_teachers_class_set = models.ClassModel.objects.filter(teacher=teacher.id)
            weekly_teachers_class_list = [] 
            now_date = datetime.datetime.now() 

            # 今日から1週間以内のまだ予約されていない授業、または自分が予約した授業をリストに入れる
            for teachers_class in weekly_teachers_class_set:

                fixed_datetime = teachers_class.datetime + datetime.timedelta(hours=9) # 9時間分の時間のずれを修正

                # StudentModelのid=1の生徒はダミー
                if now_date.day <= teachers_class.datetime.day <= now_date.day+6 and (teachers_class.student.id == 1 or teachers_class.student.id == student.id):

                    weekly_teachers_class_list.append(teachers_class)

            weekly_teachers_class_list = fix_weekly_teachers_class_list(weekly_teachers_class_list) # weekly_teachers_class_listを扱いやすい形に修正

            if request.GET.get("error"):
                error = request.GET.get("error")
            else:
                error = ""

            return render(request, "choose_reserved_class_datetime.html", {"weekly_teachers_class_list" : weekly_teachers_class_list, "student" : student, "error" : error})

        elif request.method == "POST":
            user = request.user 
            student = models.StudentModel.objects.get(user=user.id) 
            teacher = models.TeacherModel.objects.get(user=teacher_id)
            reserved_class_datetime_text = request.POST["reserved_class_datetime"]
            reserved_class_datetime = datetime.datetime.strptime(reserved_class_datetime_text, "%Y:%m:%d %H:00")

            # 生徒が既にその授業を予約しているかどうかを確認
            duplicate = is_duplicate(models.ClassModel.objects.filter(teacher=teacher.id).filter(datetime=reserved_class_datetime).filter(student=student.id))

            # まだ授業を予約していなければ、ClassModelに生徒を登録する
            if not duplicate:

                learning_class = models.ClassModel.objects.filter(teacher=teacher.id).get(datetime=reserved_class_datetime) # 予約する授業
                learning_class.student = student
                learning_class.save()

                return redirect("choose_reserved_class_datetime", teacher_id=teacher_id)
            
            # 既に授業を予約していれば、登録しない。
            else:
                reverse_url = reverse("choose_reserved_class_datetime", kwargs={"teacher_id" : teacher_id})
                url = add_getparam_to_url(reverse_url, {"error" : "既に予約しています"})

                return redirect(url)
    
    # 講師の場合
    elif request.user.is_authenticated and request.user.user_type == "teacher":
        pass

    # ログインしていない場合
    else:
        pass



# ---------------------------講師専用のページ----------------------------

# 講師アカウント作成ページ
def signup_teacheraccount_view(request):

    if request.method == "GET":
        return render(request, "signup_teacheraccount.html")
    
    elif request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        password = request.POST["password"]
        type = "teacher"

        user_set = get_user_model().objects.filter(username=username) # ユーザーモデルの、ユーザー名と一致した行のセット
        
        # ユーザー名の重複を調べる
        duplicate = is_duplicate(user_set)

        # ユーザー名の重複がなければ、登録する。その後、ログイン画面へ遷移する。
        if not duplicate:
            user = get_user_model().objects.create_user(username, "", password)
            user.first_name = first_name
            user.last_name = last_name
            user.type = type
            user.save()

            models.TeacherModel.objects.create(user=user)

            return redirect("login")

        # 重複があれば、登録しない。アカウント登録画面へ戻る。
        else:
            return render(request, "signup_teacheraccount.html")

# 今日行う予定の授業を表示
# スケジュールを管理する
# 注意点 : DBから取り出されるDatetimeインスタンスのタイムゾーンはUTC
def manage_schedule_view(request):

    # 講師の場合
    if request.user.is_authenticated and request.user.user_type == "teacher":

        if request.method == "GET":

            # --------今日の授業を表示--------
            user = request.user
            teacher = models.TeacherModel.objects.get(user=user.id)
            weekly_datetime_list = create_weekly_datetime_list() # 一週間分の日付、時刻のリストを作成
            teachers_class_set = models.ClassModel.objects.filter(teacher=teacher.id)
            teachers_class_list = change_set_to_list(teachers_class_set)
            todays_teachers_class_list = [] 
            now_date = datetime.datetime.utcnow()

            # 今日行う授業をリストに入れる
            for teachers_class in teachers_class_list:

                # StudentModelのid=1の生徒はダミー
                if teachers_class.datetime.day == now_date.day and teachers_class.datetime.hour >= now_date.hour and teachers_class.student.id != 1:

                    todays_teachers_class_list.append(teachers_class)
            
            # --------スケジュール用リストの作成--------
            for i, halfday_time_list in enumerate(weekly_datetime_list):

                for j, time in enumerate(halfday_time_list):

                    for teachers_class in teachers_class_list:

                        fixed_datetime = teachers_class.datetime + datetime.timedelta(hours=9) # 9時間分のずれを修正した時刻
                        
                        # timeとteaching_class.datetimeの年、月、日、時間、分情報が一致していれば、
                        # weekly_datetime_listにClassModelオブジェクトを代入する
                        if time.year == fixed_datetime.year and time.month == fixed_datetime.month and time.day == fixed_datetime.day and time.hour == fixed_datetime.hour and time.minute == fixed_datetime.minute:
                            weekly_datetime_list[i][j] = teachers_class
                
            if request.GET.get("error"):
                error = request.GET.get("error")
            else:
                error = ""

            return render(request, "manage_schedule.html", {"weekly_datetime_list" : weekly_datetime_list, "todays_teachers_class_list" : todays_teachers_class_list, "teachers_class_list" : teachers_class_list, "error" : error, "now_date" : now_date})

        elif request.method == "POST":
            user = request.user
            teacher = models.TeacherModel.objects.get(user=user.id) 
            dummy_student = models.StudentModel.objects.get(id=1) 
            teachers_class_datetime_text = request.POST["teachers_class_datetime"]
            teachers_class_datetime = datetime.datetime.strptime(teachers_class_datetime_text, "%Y:%m:%d %H:00") 

            # 個別指導できる日付、時刻が既に登録したものと重複していないかを調べる
            duplicate = is_duplicate(models.ClassModel.objects.filter(datetime=teachers_class_datetime))

            # 日付、時刻が重複していなければ、ClassModelに登録
            if not duplicate:

                models.ClassModel.objects.create(student=dummy_student, teacher=teacher, datetime=teachers_class_datetime)

                return redirect("manage_schedule")
            
            # 日付、時刻が重複していれば、登録しない。
            else:
                reverse_url = reverse("manage_schedule")
                url = add_getparam_to_url(reverse_url, {"error" : "既に登録されています"})

                return  redirect(url)

        # ユーザーが生徒の場合
        elif request.user.user_type == "student":
            pass

    # ユーザーがログインしていない場合
    else:
        pass
