from django.http import response
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse

import datetime as datetime
from urllib.parse import urlencode

from . import models


# ------------------------------便利な関数------------------------------

# getパラメータを加えたurlを作成する
# reverse_url : 遷移先のurl, get_params : getパラメーターを格納した辞書
def add_getparam_to_url(reverse_url, get_params):
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

# 講師が予約可能な授業のリストを作成する
def create_teaching_class_list(teaching_class_list):
    class_list = [] # 半日分の、予約可能な授業のリストのリスト
    halfday_class_list = [] # 半日分の、予約可能な授業のリスト
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) # 今日の0時0分

    # halfday_classリストを作成し、class_listに入れる。その後、class_listを初期化する。これを繰り返す。
    for i in range(today.day, today.day+7):

        # halfday_class_listを作成する
        for j in range(0, 12):

            for teaching_class in teaching_class_list:

                time_interval = datetime.timedelta(hours=9) # 9時間分のずれ
                fixed_teaching_datetime = teaching_class.datetime + time_interval # ずれを修正済みの授業時間
                
                if fixed_teaching_datetime.day == i and fixed_teaching_datetime.hour == j:

                    halfday_class_list.append(teaching_class)
        
        # class_listにhalfday_class_listを追加する
        class_list.append(halfday_class_list)
        halfday_class_list = []

        # halfday_class_listを作成する
        for j in range(12, 24):

            for teaching_class in teaching_class_list:

                time_interval = datetime.timedelta(hours=9) # 9時間分のずれ
                fixed_teaching_datetime = teaching_class.datetime + time_interval # ずれを修正済みの授業時間

                if fixed_teaching_datetime.day == i and fixed_teaching_datetime.hour == j:

                    halfday_class_list.append(teaching_class)
        
        # class_listにhalfcay_class_listを追加する
        class_list.append(halfday_class_list)
        halfday_class_list = []
    
    return class_list

        

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
            learning_class_set = models.ClassModel.objects.filter(student=student.id) # 予約した授業ののセット
            learning_class_list = change_set_to_list(learning_class_set) # 予約した授業のリスト
            learning_class_list = fix_datetime_list(learning_class_list) # 9時間分の時間のずれを修正する
            today_learning_class_list = [] # 今日受ける授業のリスト

            # 予約した授業のうち、今日受ける授業の日付、時刻をリストに入れる
            for learning_class in learning_class_set:

                # now_dateの時刻より前の授業は除外する
                if learning_class.datetime.day == now_date.day and learning_class.datetime.hour >= now_date.hour:
                    learning_class.datetime = learning_class.datetime - datetime.timedelta(hours=9) # 9時間分のずれを元に戻す
                    today_learning_class_list.append(learning_class)
                
            today_learning_class_list.sort(key=lambda x:x.datetime.timestamp()) # 今日受ける授業のリストを古い順に並べ替える

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
            
            now_date -= datetime.timedelta(hours=9) # 9時間分の時間のずれを修正する

            return render(request, "reserve.html", {"today_learning_class_list": today_learning_class_list, "teacher_list" : teacher_list, "now_date" : now_date})
        
        # ユーザーが講師の場合
        elif request.user.user_type == "teacher":
            pass
    
    # ログインしていない場合
    else:
        pass

# 授業の時間を選択する
# teacher_id : 講師のUserModelのid列の値
def choose_learning_datetime_view(request, teacher_id):

    # ユーザーがログインしている場合
    if request.user.is_authenticated:

        # ユーザーが生徒の場合
        if request.user.user_type == "student":

            # GETメソッドの場合
            if request.method == "GET":
                user = request.user # ログイン中のユーザー
                student = models.StudentModel.objects.get(user=user.id) # ログイン中のユーザーの生徒オブジェクト
                teacher = models.TeacherModel.objects.get(user=teacher_id) # 選択した講師

                teaching_class_set = models.ClassModel.objects.filter(teacher=teacher.id) # 選択した講師の、1週間以内の予約可能な授業のセット
                teaching_class_list = [] # 選択した講師の、1週間以内の予約可能な授業のリスト
                now_date = datetime.datetime.now() # 現在時刻

                # 今日から1週間以内のまだ予約されていない授業、または自分が予約した授業をteaching_class_listに入れる
                for teaching_class in teaching_class_set:

                    time_interval = datetime.timedelta(hours=9) # 9時間分のずれ
                    fixed_teaching_datetime = teaching_class.datetime + time_interval # ずれを修正済みの授業時間

                    if now_date.day <= fixed_teaching_datetime.day <= now_date.day+6 and (teaching_class.student.id == 1 or teaching_class.student.id == student.id):

                        teaching_class_list.append(teaching_class)

                teaching_class_list.sort(key=lambda x:x.datetime.timestamp()) # 予約可能な授業を日付、時刻順に並べ替える
                teaching_class_list = create_teaching_class_list(teaching_class_list) # teaching_class_listを扱いやすい形に修正する

                # GETメソッドでerrorパラメーターが送られていれば、error変数に代入
                if request.GET.get("error"):
                    error = request.GET.get("error")

                # 送られていなければ、error変数に空の文字列を代入
                else:
                    error = ""

                return render(request, "choose_learning_datetime.html", {"teaching_class_list" : teaching_class_list, "student" : student, "error" : error})

            # POSTメソッドの場合
            elif request.method == "POST":
                user = request.user # ログイン中のユーザー
                student = models.StudentModel.objects.get(user=user.id) # ログイン中のユーザーの生徒オブジェクト
                teacher = models.TeacherModel.objects.get(user=teacher_id) # 選択した講師
                learning_datetime_text = request.POST["learning_datetime"] # 予約した授業の日付、時刻を表したテキスト
                learning_datetime = datetime.datetime.strptime(learning_datetime_text, "%Y:%m:%d %H:00") # 予約した授業の日付、時刻

                # 生徒が既にその授業を予約しているかどうかを確認
                duplicate = is_duplicate(models.ClassModel.objects.filter(teacher=teacher.id).filter(datetime=learning_datetime).filter(student=student.id))

                # まだ授業を予約していなければ、ClassModelのstudentに生徒を登録する
                if not duplicate:

                    learning_class = models.ClassModel.objects.filter(teacher=teacher.id).get(datetime=learning_datetime) # 予約する授業
                    learning_class.student = student # ClassModelのstudent列にログインしている生徒のオブジェクトを代入
                    learning_class.save()

                    return redirect("choose_learning_datetime", teacher_id=teacher_id)
                
                # 既に授業を予約していれば、登録しない。
                else:
                    reverse_url = reverse("choose_learning_datetime", kwargs={"teacher_id" : teacher_id}) # 遷移先のurl
                    url = add_getparam_to_url(reverse_url, {"error" : "既に予約しています"})

                    return redirect(url)


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

                today_teaching_class_list = [] # 今日行う授業のリスト
                now_date = datetime.datetime.now() # 現在時刻

                # teaching_class_listの内、今日行う授業をtoday_teaching_class_listに代入
                for teaching_class in teaching_class_list:

                    # 生徒が予約していない授業は除外する
                    # now_dateより前の時刻の授業は除外する
                    if teaching_class.datetime.day == now_date.day and teaching_class.datetime.hour >= now_date.hour and teaching_class.student.id != 1:

                        teaching_class.datetime -= datetime.timedelta(hours=9) # 9時間分の時間のずれを元に戻す
                        today_teaching_class_list.append(teaching_class)
                        teaching_class.datetime += datetime.timedelta(hours=9) # 9時間分の時間のずれを修正する

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

                now_date -= datetime.timedelta(hours=9) # 9時間分のずれを修正する

                return render(request, "manage_schedule.html", {"datetime_list" : datetime_list, "today_teaching_class_list" : today_teaching_class_list, "teaching_class_list" : teaching_class_list, "error" : error, "now_date" : now_date})

            # POSTメソッドの場合
            elif request.method == "POST":
                user = request.user # ログインしているユーザー
                teacher = models.TeacherModel.objects.get(user=user.id) # ログイン中のユーザーのTeacherModelインスタンス
                dummy_student = models.StudentModel.objects.get(id=1) # ダミーの生徒
                teaching_datetime_text = request.POST["datetime"] # 個別指導できる日付、時刻を表した文字列
                teaching_datetime = datetime.datetime.strptime(teaching_datetime_text, "%Y:%m:%d %H:00") # 個別指導できる日付、時刻

                # 個別指導できる日付、時刻が既に登録したものと重複していないかを調べる
                duplicate = is_duplicate(models.ClassModel.objects.filter(datetime=teaching_datetime))

                # 日付、時刻が重複していなければ、
                if not duplicate:

                    # 個別指導できる日付、時刻をデータベースに登録
                    models.ClassModel.objects.create(student=dummy_student, teacher=teacher, datetime=teaching_datetime)

                    # スケジュール管理ページに戻る
                    return redirect("manage_schedule")
                
                # 日付、時刻が重複していれば、登録しない。
                else:
                    reverse_url = reverse("manage_schedule") # 遷移先のurl
                    url = add_getparam_to_url(reverse_url, {"error" : "既に登録されています"})

                    # スケジュール管理ページに戻る
                    return  redirect(url)
        

        # ユーザーが生徒の場合
        elif request.user.user_type == "student":
            pass




    # ユーザーがログインしていない場合
    else:
        pass
