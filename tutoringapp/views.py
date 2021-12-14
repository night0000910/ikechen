from django.http import response
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from django.utils import timezone

import datetime as datetime
from urllib.parse import urlencode

from . import models

# *** views.pyで扱う時刻はUTCに統一する ***

# --------------------------------関数-------------------------------

# getパラメータを加えたurlを作成する
# reverse_url : 遷移先のurl, get_params : getパラメーターを格納した辞書
def add_getparam_to_url(reverse_url, get_params):
    parameters = urlencode(get_params) 
    url = f"{reverse_url}?{parameters}" 

    return url

# "true", "false"といった文字列をbool値へ変換する
def change_str_to_bool(str):
    if str == "true":
        return True
    elif str == "false":
        return False

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

# StudentModelのid=1の列に、ダミーの生徒を作成する
def create_dummy_student():
    student_set = models.StudentModel.objects.filter(id=1)
    student_list = change_set_to_list(student_set)
    username = "dummy_student"
    password = "password"

    if student_list:
        return
    
    else:
        user = get_user_model().objects.create_user(username, "", password)
        user.last_name = "dummy"
        user.first_name = "student"
        user.user_type = "student"
        user.save()

        models.StudentModel.objects.create(user=user)

# 重複した時刻の授業を返す
def return_datetime_duplicate_class(class_list, year, month, day, hour):

    duplicate_class = None

    for this_class in class_list:

        if this_class.datetime.year == year and this_class.datetime.month == month and this_class.datetime.day == day and this_class.datetime.hour == hour:
            duplicate_class = this_class
    
    return duplicate_class

# 引数に渡された時刻が、昨日の15時0分(JSTにおける、今日の0時0分)から一日以内の時刻かどうかを判定する
def judge_datetime_is_within_today(this_datetime):
    jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
    one_days_after = today + datetime.timedelta(days=1)

    if today <= this_datetime < one_days_after:
        return True
    else:
        return False

# 引数に渡された時刻が、現在時刻より前の時刻かどうかを判定する
def judge_datetime_is_before_now(this_datetime):
    now = timezone.now().replace(minute=0, second=0, microsecond=0)

    if this_datetime >= now:
        return True
    else:
        return False

# 今日の、講師が行う予定の授業のリストを作成する
# teacher_id : 講師のUserModelにおけるid
def create_todays_teachers_class_list(teacher_id):
    teacher = models.TeacherModel.objects.get(user=teacher_id)
    teachers_class_set = models.ClassModel.objects.filter(teacher=teacher.id)
    teachers_class_list = change_set_to_list(teachers_class_set)
    todays_teachers_class_list = []
    now = timezone.now()

    # 今日行う授業をリストに入れる
    for teachers_class in teachers_class_list:

        # StudentModelのid=1の生徒はダミー
        if judge_datetime_is_within_today(teachers_class.datetime) and judge_datetime_is_before_now(teachers_class.datetime) and teachers_class.student.id != 1:

            if teachers_class.datetime.hour == now.hour and now.minute >= 50:
                continue

            todays_teachers_class_list.append(teachers_class)
    
    todays_teachers_class_list.sort(key=lambda x:x.datetime.timestamp())
    
    return todays_teachers_class_list

# 生徒が予約した授業のうち、今日行われる授業のリストを作成する
# student_id : 生徒のUserModelにおけるid
def create_todays_reserved_class_list(student_id):
    student = models.StudentModel.objects.get(user=student_id)
    reserved_class_set = models.ClassModel.objects.filter(student=student.id)
    reserved_class_list = change_set_to_list(reserved_class_set)
    todays_reserved_class_list = []
    now = timezone.now()

    # 今日行う授業をリストに入れる
    for reserved_class in reserved_class_list:

        # StudentModelのid=1の生徒はダミー
        if judge_datetime_is_within_today(reserved_class.datetime) and judge_datetime_is_before_now(reserved_class.datetime):

            if reserved_class.datetime.hour == now.hour and now.minute >= 50:
                continue

            todays_reserved_class_list.append(reserved_class)
    
        todays_reserved_class_list.sort(key=lambda x:x.datetime.timestamp())
    
    return todays_reserved_class_list

# 一週間分の日付と時刻のリストを作成する
# teacher_id : 講師のUserModelにおけるid
def create_weekly_datetime_list(teacher_id):
    teacher = models.TeacherModel.objects.get(user=teacher_id)
    teachers_class_set = models.ClassModel.objects.filter(teacher=teacher.id)
    teachers_class_list = change_set_to_list(teachers_class_set)
    weekly_datetime_list = [] 
    halfday_time_list = [] # 半日分の時刻のリスト
    jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
    zero_oclock = 0
    three_oclock = 3
    fifteen_oclock = 15
    twenty_four_oclock = 24
    zero_days_after = 0
    seven_days_after = 7

    # 半日分の時刻のリストを作成し、一週間分の日付、時刻リストに入れる。これを繰り返す。
    for i in range(zero_days_after, seven_days_after):

        # 半日分の時刻(15時〜2時)のリストを作成
        # 重複した時刻の授業がある場合は、代わりにその授業のClassModelインスタンスをリストに入れる
        for j in range(fifteen_oclock, twenty_four_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=i)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class:
                halfday_time_list.append(duplicate_class)
            else:
                halfday_time_list.append(added_datetime)

        for j in range(zero_oclock, three_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class:
                halfday_time_list.append(duplicate_class)
            else:
                halfday_time_list.append(added_datetime)
        
        weekly_datetime_list.append(halfday_time_list)
        halfday_time_list = []

        # 半日分の時刻(3時〜14時)のリストを作成
        # 重複した時刻の授業がある場合は、代わりにその授業のClassModelインスタンスをリストに入れる
        for j in range(three_oclock, fifteen_oclock):
            added_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, added_datetime.year, added_datetime.month, added_datetime.day, added_datetime.hour)

            if duplicate_class:
                halfday_time_list.append(duplicate_class)
            else:
                halfday_time_list.append(added_datetime)

        weekly_datetime_list.append(halfday_time_list)
        halfday_time_list = []


    return weekly_datetime_list

# 引数に渡された時刻が、昨日の15時0分(JSTにおける、今日の0時0分)から一週間以内の時刻かどうかを判定する
def judge_datetime_is_within_oneweek(this_datetime):
    jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
    seven_days_after = today + datetime.timedelta(days=7)

    if today <= this_datetime < seven_days_after:
        return True
    else:
        return False

# 引数に渡された時刻が、現在時刻の1時間後より前の時刻かどうかを判定する
def judge_datetime_is_before_one_hour(this_datetime):
    one_hour_later = timezone.now().replace(minute=30, second=0, microsecond=0) + datetime.timedelta(hours=1)

    if this_datetime < one_hour_later:
        return True
    else:
        return False

# ある講師の、一週間分の授業のリストを作成する
# student_id : 生徒のUserModelにおけるid teacher_id : 講師のUserModelにおけるid
def create_weekly_teachers_class_list(student_id, teacher_id):
    student = models.StudentModel.objects.get(user=student_id)
    teacher = models.TeacherModel.objects.get(user=teacher_id)
    teachers_class_set = models.ClassModel.objects.filter(teacher=teacher.id)
    teachers_class_list = [] 

    # 今日から1週間以内のまだ予約されていない授業、または自分が予約した授業をリストに入れる
    for teachers_class in teachers_class_set:

        # StudentModelのid=1の生徒はダミー
        if judge_datetime_is_within_oneweek(teachers_class.datetime) and (teachers_class.student.id == 1 or teachers_class.student.id == student.id):

            # 現在時刻の1時間後より前の時刻の授業は除外する
            if judge_datetime_is_before_one_hour(teachers_class.datetime):
                continue

            teachers_class_list.append(teachers_class)

    teachers_class_list.sort(key=lambda x:x.datetime.timestamp())
    jst_today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    today = timezone.now().replace(day=jst_today.day, hour=15, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1) # UTCにおける15時0分(JSTにおける0時0分)
    weekly_teachers_class_list = []
    halfday_teachers_class_list = [] 
    zero_oclock = 0
    three_oclock = 3
    fifteen_oclock = 15
    twenty_four_oclock = 24
    zero_days_after = 0
    seven_days_after = 7

    # 半日分の授業を束ねたリストを作成し、一週間分の授業リストに入れる。これを繰り返す。
    for i in range(zero_days_after, seven_days_after):

        # 半日分の授業のリストを作成
        for j in range(fifteen_oclock, twenty_four_oclock):
            this_datetime = today.replace(hour=j) + datetime.timedelta(days=i)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, this_datetime.year, this_datetime.month, this_datetime.day, this_datetime.hour)

            if duplicate_class:
                halfday_teachers_class_list.append(duplicate_class)
            
        for j in range(zero_oclock, three_oclock):
            this_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, this_datetime.year, this_datetime.month, this_datetime.day, this_datetime.hour)

            if duplicate_class:
                halfday_teachers_class_list.append(duplicate_class)

        
        weekly_teachers_class_list.append(halfday_teachers_class_list)
        halfday_teachers_class_list = []

        # 半日分の授業のリストを作成
        for j in range(three_oclock, fifteen_oclock):
            this_datetime = today.replace(hour=j) + datetime.timedelta(days=i+1)
            duplicate_class = return_datetime_duplicate_class(teachers_class_list, this_datetime.year, this_datetime.month, this_datetime.day, this_datetime.hour)

            if duplicate_class:
                halfday_teachers_class_list.append(duplicate_class)
        
        weekly_teachers_class_list.append(halfday_teachers_class_list)
        halfday_teachers_class_list = []
    
    return weekly_teachers_class_list


# -------------------------講師・生徒共通のページ-------------------------


# ホームページ
def home_page_view(request):
    
    if request.user.is_authenticated:
        user = request.user

        if user.user_type == "student":
            return redirect("reserve")

        elif user.user_type == "teacher":
            return redirect("manage_schedule")

    else:
        
        return render(request, "home_page.html")

# ログインページ
def login_view(request):

    if request.method == "GET":

        if request.GET.get("error"):
            error = request.GET.get("error")
        else:
            error = ""

        return render(request, "login.html", {"error" : error})

    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            if user.user_type == "student":
                return redirect("reserve")
            
            elif user.user_type == "teacher":
                return redirect("manage_schedule")
        
        else:
            redirect_url = reverse("login")
            get_params = {"error" : "ログインに失敗しました"}
            url = add_getparam_to_url(redirect_url, get_params)
            return redirect(url)

# ログアウトページ
def logout_view(request):
    logout(request)
    return redirect("home_page")

# ユーザーのプロフィールを表示する
def profile_view(request, user_id):

    if request.user.is_authenticated:
        referred_user = get_user_model().objects.get(id=user_id)
        now_date = datetime.datetime.now(datetime.timezone.utc)
        elapsed_time = relativedelta(now_date, referred_user.start_datetime)

        if elapsed_time.year is not None:
            elapsed_year = f"{elapsed_time.year}年"
        else:
            elapsed_year = "1年未満"

        return render(request, "profile.html", {"referred_user" : referred_user, "elapsed_year" : elapsed_year})
    
    else:
        return redirect("login")

# アカウントを設定する
def setup_account_view(request):
    
    if request.user.is_authenticated:

        if request.method == "GET":
            
            return render(request, "setup_account.html")
        
        elif request.method == "POST":
            user = request.user

            # request.POST["setup"]には値が格納されていない
            
            # プロフィール画像を変更する場合
            if request.POST["setup"] == "change_profile_image":

                profile_image = request.FILES["profile_image"]
                user.profile_image = profile_image
                user.save()

                return redirect("setup_account")

            # 名前を変更する場合
            elif request.POST["setup"] == "change_name":

                first_name = request.POST["first_name"]
                last_name = request.POST["last_name"]
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                return redirect("setup_account")

            # 自己紹介を編集する場合
            elif request.POST["setup"] == "edit_self_introduction":

                self_introduction = request.POST["self_introduction"]
                user.self_introduction = self_introduction
                user.save()

                return redirect("setup_account")

    else:
        return redirect("login")  

# 条件を満たしていれば、ビデオチャットを始める
# 条件 : urlに含まれるclass_idの授業が授業時間内であり、リクエスト元のユーザーがその授業の生徒または講師
def tutoring_view(request, class_id):

    if request.user.is_authenticated:
        user = request.user
        reserved_class_set = models.ClassModel.objects.filter(id=class_id)
        reserved_class_list = change_set_to_list(reserved_class_set)
        now_date = datetime.datetime.utcnow()

        if reserved_class_list:
            reserved_class = reserved_class_list[0]

            if reserved_class.datetime.day == now_date.day and reserved_class.datetime.hour == now_date.hour and now_date.minute < 50 and (reserved_class.student.user.id == user.id or reserved_class.teacher.user.id == user.id):
                
                return render(request, "tutoring.html", {"username" : user.username})
        
        return redirect("manage_schedule")
    
    else:
        return redirect("login")


# ---------------------------生徒専用のページ----------------------------

# 生徒アカウント作成ページ
def signup_studentaccount_view(request):
    
    if request.method == "GET":

        if request.GET.get("error"):
            error = request.GET.get("error")
        else:
            error = ""

        return render(request, "signup_studentaccount.html", {"error" : error})

    elif request.method == "POST":

        # ダミーの生徒を作成する
        create_dummy_student()

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        password = request.POST["password"]
        type = "student"

        user_set = get_user_model().objects.filter(username=username) # ユーザーモデルの、ユーザー名と一致した行のセット
        
        # ユーザー名の重複を調べる
        duplicate = is_duplicate(user_set)

        # ユーザー名の重複がなければ、登録する。その後、ログイン画面へ遷移する。
        if not duplicate:
            user = get_user_model().objects.create_user(username, "", password)
            user.first_name = first_name
            user.last_name = last_name
            user.user_type = type
            user.save()

            models.StudentModel.objects.create(user=user)

            return redirect("login")

        # 重複があれば、登録しない。アカウント登録画面へ戻る。
        else:
            redirect_url = reverse("signup_studentaccount")
            get_params = {"error" : "既に同じ名前のユーザーが存在しています"}
            url = add_getparam_to_url(redirect_url, get_params)
            return redirect(url)

# 予約した授業を表示
# どの先生の授業を予約するかを決める
def reserve_view(request):

    # 生徒の場合
    if request.user.is_authenticated and request.user.user_type == "student":

        user = request.user
        student = models.StudentModel.objects.get(user=user.id)
        now = timezone.now() 

        todays_reserved_class_list = create_todays_reserved_class_list(user.id) # 今日行われる授業のリストを作成する

        # --------予約可能な講師の表示--------
        teacher_set = models.TeacherModel.objects.all()
        teacher_list = []

        # 予約可能な講師をteacher_listに追加する
        for teacher in teacher_set:
            teachers_class_set = models.ClassModel.objects.filter(teacher=teacher.id) 
            teachers_class_list = change_set_to_list(teachers_class_set) 

            for teachers_class in teachers_class_list:

                if now.day <= teachers_class.datetime.day <= now.day+6:
                    teacher_list.append(teacher)
                    break

        return render(request, "reserve.html", {"todays_reserved_class_list": todays_reserved_class_list, "teacher_list" : teacher_list, "now" : now})
    
    # 講師の場合
    elif request.user.is_authenticated and request.user.user_type == "teacher":
        return redirect("manage_schedule")

    # ログインしていない場合
    else:
        return redirect("login")

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

            weekly_teachers_class_list = create_weekly_teachers_class_list(user.id, teacher_id) # 選択した講師の、一週間分の授業のリストを作成する

            if request.GET.get("error"):
                error = request.GET.get("error")
            else:
                error = ""

            now = timezone.now()
            elapsed_time = relativedelta(now, teacher.user.start_datetime)

            if elapsed_time.year is not None:
                elapsed_year = f"{elapsed_time.year}年"
            else:
                elapsed_year = "1年未満"

            return render(request, "choose_reserved_class_datetime.html", {"weekly_teachers_class_list" : weekly_teachers_class_list, "student" : student, "teacher" : teacher.user, "elapsed_year" : elapsed_year, "error" : error})

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

                reserved_class = models.ClassModel.objects.filter(teacher=teacher.id).get(datetime=reserved_class_datetime) # 予約する授業
                return redirect("add_reserved_class", teacher_id=teacher_id, class_id=reserved_class.id)
            
            # 既に授業を予約していれば、登録しない。
            else:
                reverse_url = reverse("choose_reserved_class_datetime", kwargs={"teacher_id" : teacher_id})
                url = add_getparam_to_url(reverse_url, {"error" : "既に予約しています"})

                return redirect(url)
    
    # 講師の場合
    elif request.user.is_authenticated and request.user.user_type == "teacher":
        return redirect("manage_schedule")

    # ログインしていない場合
    else:
        return redirect("login")

# teacher_id : 講師のUserModelのid, class_id : 予約する授業のClassModelのid
def add_reserved_class_view(request, teacher_id, class_id):

    if request.user.is_authenticated:

        if request.method == "GET":
            reserved_class = models.ClassModel.objects.get(id=class_id)
            return render(request, "add_reserved_class.html", {"reserved_class" : reserved_class})

        elif request.method == "POST":
            user = request.user
            student = models.StudentModel.objects.get(user=user.id)
            add = change_str_to_bool(request.POST["add"])

            if add:
                reserved_class = models.ClassModel.objects.get(id=class_id)
                reserved_class.student = student
                reserved_class.save()
            
            return redirect("choose_reserved_class_datetime", teacher_id=teacher_id)

    else:
        return redirect("home_page")


# ---------------------------講師専用のページ----------------------------

# 講師アカウント作成ページ
def signup_teacheraccount_view(request):

    if request.method == "GET":

        if request.GET.get("error"):
            error = request.GET.get("error")
        else:
            error = ""

        return render(request, "signup_teacheraccount.html", {"error" : error})
    
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
            user.user_type = type
            user.save()

            models.TeacherModel.objects.create(user=user)

            return redirect("login")

        # 重複があれば、登録しない。アカウント登録画面へ戻る。
        else:
            redirect_url = reverse("signup_teacheraccount")
            get_params = {"error" : "既に同じ名前のユーザーが存在しています"}
            url = add_getparam_to_url(redirect_url, get_params)
            return redirect(url)

# 今日行う予定の授業を表示
# スケジュールを管理する
# 注意点 : DBから取り出されるDatetimeインスタンスのタイムゾーンはUTC
def manage_schedule_view(request):

    # 講師の場合
    if request.user.is_authenticated and request.user.user_type == "teacher":

        if request.method == "GET":

            user = request.user
            teacher = models.TeacherModel.objects.get(user=user.id)
            weekly_datetime_list = create_weekly_datetime_list(user.id) # 一週間分の日付、時刻のリストを作成(UTCに準拠)
            todays_teachers_class_list = create_todays_teachers_class_list(user.id) # 今日行われる授業のリストを作成する
            now = timezone.now()
                
            if request.GET.get("error"):
                error = request.GET.get("error")
            else:
                error = ""

            return render(request, "manage_schedule.html", {"weekly_datetime_list" : weekly_datetime_list, "todays_teachers_class_list" : todays_teachers_class_list, "error" : error, "now" : now})

        elif request.method == "POST":

            # ダミーの生徒を作成する
            create_dummy_student()

            user = request.user
            teacher = models.TeacherModel.objects.get(user=user.id) 
            dummy_student = models.StudentModel.objects.get(id=1) 
            teachers_class_datetime_text = request.POST["teachers_class_datetime"]
            teachers_class_datetime = datetime.datetime.strptime(teachers_class_datetime_text, "%Y:%m:%d %H:00") 

            # 個別指導できる日付、時刻が既に登録したものと重複していないかを調べる
            duplicate = is_duplicate(models.ClassModel.objects.filter(teacher=teacher.id).filter(datetime=teachers_class_datetime))

            # 日付、時刻が重複していなければ、ClassModelに登録
            if not duplicate:

                return redirect("add_teachers_class", teachers_class_datetime_text=teachers_class_datetime_text)
            
            # 日付、時刻が重複していれば、登録しない。
            else:
                reverse_url = reverse("manage_schedule")
                url = add_getparam_to_url(reverse_url, {"error" : "既に登録されています"})

                return  redirect(url)

    # ユーザーが生徒の場合
    elif request.user.user_type == "student":
        return redirect("reserve")
    
    # ログインしていない場合
    else:
        return redirect("login")

# スケジュールを更新する
# teachers_class_datetime_text : 追加する授業の時刻を表現したテキスト
def add_teachers_class_view(request, teachers_class_datetime_text):

    if request.user.is_authenticated:

        if request.method == "GET":
            teachers_class_datetime = datetime.datetime.strptime(teachers_class_datetime_text, "%Y:%m:%d %H:00") 
            return render(request, "add_teachers_class.html", {"teachers_class_datetime" : teachers_class_datetime})

        elif request.method == "POST":
            user = request.user
            teacher = models.TeacherModel.objects.get(user=user.id) 
            add = change_str_to_bool(request.POST["add"])
            dummy_student = models.StudentModel.objects.get(id=1) 
            teachers_class_datetime = datetime.datetime.strptime(teachers_class_datetime_text, "%Y:%m:%d %H:00") 

            if add:
                models.ClassModel.objects.create(student=dummy_student, teacher=teacher, datetime=teachers_class_datetime)
            
            return redirect("manage_schedule")            

    else:
        return redirect("home_page")
