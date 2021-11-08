from django.http import response
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse

import datetime as datetime
from urllib.parse import urlencode

from . import models


# ------------------------------便利な関数------------------------------

# getパラメータを加えたurlを作成する
# reverse_name : 遷移先のページの名前, get_params : getパラメーターを格納した辞書
def add_getparam_to_url(reverse_name, get_params):
    reverse_url = reverse(reverse_name) # 遷移先のurl
    parameters = urlencode(get_params) # クエリ文字列を作る
    url = f"{reverse_url}?{parameters}" # クエリ文字列を含めたurlを作る

    return url


# 行のセットをリストに変換する
def change_set_to_list(record_set):

    record_list = [] # 行のリスト

    # 行のリストに行を入れていく
    for record in record_set:
        record_list.append(record)
    
    return record_list

# filter関数の戻り値をrecord_setに渡す。filter関数の条件に一致した行があれば(重複があれば)Trueを、
# 条件に一致した行がなければ(重複がなければ)Falseを返す。
def is_duplicate(record_set):

    record_list = change_set_to_list(record_set) # 行のリスト
    
    # リストの要素数が0であればFalse、0でなければTrueを返す
    if len(record_list):
        return True
    else:
        return False

# 一週間分の日付と時刻のリストを作成する
def create_datetime_list():
    datetime_list = [] # 一週間分の日付、時刻のリスト
    time_list = [] # 半日分の時刻のリスト

    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) # 今日の0時0分

    # time_listをdate_listに入れる。その後、time_listを初期化する。これを繰り返す。
    for i in range(0, 7):

        # time_listに半日分の時刻を入れる
        for j in range(0, 12):
            time_list.append(today + datetime.timedelta(days=i, hours=j))
        
        datetime_list.append(time_list)
        time_list = []

        # time_listに半日分の時刻を入れる
        for j in range(12, 24):
            time_list.append(today + datetime.timedelta(days=i, hours=j))

        datetime_list.append(time_list)
        time_list = []

    
    return datetime_list

# データベースから取得した時刻の、9時間分のずれを修正する
def fix_datetime_list(datetime_list):
    time_interval = datetime.timedelta(hours=9) # 9時間という時間間隔

    # 時刻を修正して、datetime_listへ代入
    for i, time in enumerate(datetime_list):

        datetime_list[i].datetime = time.datetime + time_interval
    
    return datetime_list




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

# 個別指導予約ページ
# どの先生の授業を予約するかを決める
def reserve_view(request):

    # ユーザーがログインしている場合
    if request.user.is_authenticated:

        # ユーザーが生徒の場合
        if request.user.user_type == "student":

            user = request.user # ログインしているユーザー
            student = models.StudentModel.objects.get(user=user.id) # 現在ログイン中のユーザーのStudentModelオブジェクト
            now_date = datetime.datetime.now() # 現在時刻
            learning_class_set = models.ClassModel.objects.filter(user=student.id) # 予約した授業ののセット
            learning_class_list = change_set_to_list(learning_class_set) # 予約した授業のリスト
            learning_class_list = fix_datetime_list(learning_class_list) # 9時間分の時間のずれを修正する
            today_learning_datetime_list = [] # 今日受ける授業の日付、時刻のリスト

            # 予約した授業のうち、今日受ける授業の日付、時刻をリストに入れる
            for learning_class in learning_class_set:

                if learning_class.datetime.day == now_date.day:
                    learning_class.datetime = learning_class.datetime - datetime.timedelta(hours=9) # 9時間分のずれを元に戻す
                    today_learning_datetime_list.append(learning_class.datetime)
                
            today_learning_datetime_list.sort(key=lambda x:x.timestamp()) # 今日受ける授業のリストを古い順に並べ替える

            teacher_set = models.TeacherModel.objects.all() # 講師のセット
            teacher_list = [] # 予約可能な講師のリスト

            # 予約可能な講師をteacher_listに追加する
            for teacher in teacher_set:
                teaching_class_set = models.ClassModel.objects.filter(teacher=teacher.id) # 講師の個別指導可能(予約可能)な授業のセット
                teaching_class_list = change_set_to_list(teaching_class_set) # 講師の個別指導可能な授業のリスト
                teaching_class_list = fix_datetime_list(teaching_class_list) # 9時間分の時間のずれを修正する
                now_date = datetime.datetime.now() # 現在時刻


                for teaching_class in teaching_class_list:

                    # 個別指導可能な授業の日付が今日から6日後以内であれば
                    if now_date.day <= teaching_class.datetime.day <= now_date.day+6:
                        teacher_list.append(teacher) # teacherをteacher_listに追加する
                        break

            return render(request, "reserve.html", {"today_learning_datetime_list": today_learning_datetime_list, "teacher_list" : teacher_list})
        
        # ユーザーが講師の場合
        elif request.user.user_type == "teacher":
            pass
    
    # ログインしていない場合
    else:
        pass

# 授業の時間を選択する
def choose_learning_datetime_view(request, teacher_id):

    # ユーザーがログインしている場合
    if request.user.is_authenticated:

        # ユーザーが生徒の場合
        if request.user.user_type == "student":

            # GETメソッドの場合
            if request.method == "GET":

                

                return render(request, )

            # POSTメソッドの場合
            elif request.method == "POST":
                pass

        # ユーザーが講師の場合
        elif request.user.user_type == "teacher":
            pass

    # ログインしていない場合
    else:
        pass








# ---------------------------講師専用のページ----------------------------

# 講師アカウント作成ページ
def signup_teacheraccount_view(request):

    # GETメソッドの場合
    if request.method == "GET":
        return render(request, "signup_teacheraccount.html")
    
    # POSTメソッドの場合
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


# スケジュール管理ページ
def manage_schedule_view(request):

    # ユーザーがログインしている場合
    if request.user.is_authenticated:

        # ユーザーが講師の場合
        if request.user.user_type == "teacher":

            # GETメソッドの場合
            if request.method == "GET":
                user = request.user # ログイン中のユーザー
                teacher = models.TeacherModel.objects.get(user=user.id) # ログイン中のユーザーのTeacherModelインスタンス
                datetime_list = create_datetime_list() # 一週間分の日付と時刻のリスト
                teaching_class_set = models.ClassModel.objects.filter(teacher=teacher.id) # 既に登録された、個別指導可能な授業のセット
                teaching_class_list = change_set_to_list(teaching_class_set) # 既に登録された、個別指導可能な授業のリスト
                teaching_class_list = fix_datetime_list(teaching_class_list) # 9時間分の時間のずれを修正する

                # time_list : 半日分の時間のリスト time : 1時間刻みの時間
                # datetime_listの中で、teaching_class_listの日付、時刻と一致しているものがあれば、
                # datetime_list内のdatetimeオブジェクトをClassModelオブジェクトに入れ替える
                for i, time_list in enumerate(datetime_list):

                    for j, time in enumerate(time_list):


                        for teaching_class in teaching_class_list:
                            
                            # timeとteaching_class.datetimeの年、月、日、時間、分情報が一致していれば、
                            # datetime_listにClassModelオブジェクトを代入する
                            if time.year == teaching_class.datetime.year and time.month == teaching_class.datetime.month and time.day == teaching_class.datetime.day and time.hour == teaching_class.datetime.hour and time.minute == teaching_class.datetime.minute:
                                teaching_class.datetime = teaching_class.datetime - datetime.timedelta(hours=9) # 9時間分のずれを元に戻す
                                datetime_list[i][j] = teaching_class
                    

                # getメソッドでerrorパラメーターが送られていれば、error変数に代入
                if request.GET.get("error"):
                    error = request.GET.get("error")
                
                # 送られていなければ、errorに空の文字列を代入
                else:
                    error = ""

                return render(request, "manage_schedule.html", {"datetime_list" : datetime_list, "teaching_class_list" : teaching_class_list, "error" : error})

            # POSTメソッドの場合
            elif request.method == "POST":
                user = request.user # ログインしているユーザー
                teacher = models.TeacherModel.objects.get(user=user.id) # ログイン中のユーザーのTeacherModelインスタンス
                teaching_datetime_text = request.POST["datetime"] # 個別指導できる日付、時刻を表した文字列
                teaching_datetime = datetime.datetime.strptime(teaching_datetime_text, "%Y:%m:%d %H:00") # 個別指導できる日付、時刻

                # 個別指導できる日付、時刻が既に登録したものと重複していないかを調べる
                duplicate = is_duplicate(models.ClassModel.objects.filter(datetime=teaching_datetime))

                # 日付、時刻が重複していなければ、
                if not duplicate:

                    # 個別指導できる日付、時刻をデータベースに登録
                    models.ClassModel.objects.create(teacher=teacher, datetime=teaching_datetime)

                    # スケジュール管理ページに戻る
                    return redirect("manage_schedule")
                
                # 日付、時刻が重複していれば、登録しない。
                else:
                    url = add_getparam_to_url("manage_schedule", {"error" : "既に登録されています"})

                    # スケジュール管理ページに戻る
                    return  redirect(url)
        

        # ユーザーが生徒の場合
        elif request.user.user_type == "student":
            pass




    # ユーザーがログインしていない場合
    else:
        pass
