#最低限必要な機能
#出退勤者の名前時刻を記録し保存（ループか再起関数で入力を呼び出し続ける→終了するためのコマンドが必要）
#管理者による記録呼び出し
#まずは出退勤者の名前時刻を記録し保存する部分から
import datetime #datetimeモジュールの取得
import sched, time
import csv

loop = True #global宣言する
count = 0  #管理者システムの認証回数は打刻システムに戻っても継続させたいのでこっちで定義する。global宣言する。
#state_listを作ってstateとstatusを対応させた方がいい?

def main(attendance_list = []):
    while loop :
        status = "エラーを発見" #上手く出退勤記録出来なかった時のためにエラーを初期設定にする
        name = input("出退勤者の名前を入力してください: ") #出退勤者よりも相応しい言葉がありそう
        state = state_repeat()

        #inputが数字以外だった時の処理（int(input()）の形になっているやつは全部要注意)state_repeatで定義
        #ここで該当する名前の最新の状態を呼び出し、出退勤が対応しているかを確認する
        #対応していない場合、本当にこのまま記録していいかを聞く
        #関数作って後で付け足す
        if state == 0 :
            status = "出勤"
        elif state == 1 :
            status = "退勤"
        elif state == 2 :
            status = "管理システムを起動" #以下管理システムを実装する予定
            manage_certification(attendance_list)
        else :
            state = -1 #それ以外は全部エラーとして-1を振り当てる

        if state == -1 :
            print("管理者に報告してください") #エラー発生メッセージ。数字の入力ミスと内部エラーを分けれるようにしたい。未実装
        if state == 0 or state == 1 : #出退勤の時だけ確認#記録する前に最終確認する。
            missed_attendance = -1
            if attendance_list != [] :
                reversed_AL = sorted(attendance_list, reverse=True, key=lambda x:x[1]) #出退勤氷を最新の方から順番に並べていく
                for i in range(len(reversed_AL)) :
                    if reversed_AL[i][0] == name and reversed_AL[i][3] == state : #最新の出退勤と同じ状態を入力した場合に確認する
                         latest_personal = reversed_AL[i]
                         print("あなたの現在の状態は[" + status + "]です")
                         print("本当にこのまま[" + status + "]の記録を続けますか？")
                         missed_attendance = missed_attendance_repeat()
                         break

            if missed_attendance == 1 :
                continue #main()最初からやり直す

            print("[名前 → " + name + ", 状態 → " + status + "] でよろしいでしょうか？")
            confirm = confirm_repeat()
            if confirm == 1 :
                print("出退勤入力をキャンセルします。始めからやり直してください")
                continue #1はやり直し

        time = datetime.datetime.now() #現在時間を取得
        latest_list = [name, time, status, state]

        attendance_list.append(latest_list) #名前、時刻、出退勤を記録
        print("【" + name + "は" + time.strftime('%Y-%m-%d %H:%M:%S') + "に" + status + "しました】")
        #最後に誰々は"当該時刻"に出退勤しました、と表示する。時間はstr型に変換
        #年月日時分にしようと思ったけどエンコードエラーになったので保留

    else :
        #履歴のバックアップを取るための機能を実装する。ここに実装すると最後の管理システム起動時間を履歴に入れれる。
        csv_path = r"C:\Users\user\Desktop\test.csv" #今はデスクトップを指定している
        with open(csv_path, 'a', newline = "") as file :
            writer = csv.writer(file)
            writer.writerows(attendance_list)
        print("打刻履歴のバックアップ完了しました")
        print("打刻システムを終了します")

def manage_certification(attendance_list = [],menu = -1, password = 9999):  #パスワード設定 ,countは回数制限,以下5回と仮定
    if input("パスワードを入力して下さい: ") != str(password) : #間違ったパスワードを入力した場合の措置
        global count
        count += 1
        print("認証失敗しました")
        if count >= 5 :
            print("一定回数以上認証に失敗したため、管理システムを一定時間ロックします")
            print("しばらく経ってから再度ご確認ください")
            count = 0
            #sched.scheduler(300, 1, count_reset) #5分のロックのつもり 上手くいかないので保留
            #ロックする機能は未実装。後回し。一定時間経つとcountを0に戻すのがよさそう。あとロックするならcountは時間経過でリセットされる機能も欲しい。
            return
        else :
            print("残り入力回数は" + str(5 - count) + "回です")
            menu = menu_repeat() #入力に失敗したときここのメニュー表示を繰り返すため、関数化

            if menu == 0 :
                manage_certification(attendance_list)
            elif menu == 1 :
                print("わかりました。打刻システムに戻ります")
                return
            else :
                print("エラーが発生しました。打刻システムに戻ります")
                return
    else :
        print("認証成功しました")
        count = 0
        manage(attendance_list) #管理メニューを表示
        return

def manage(attendance_list = []): #管理メニューを表示。とりあえず必要そうな機能は履歴閲覧、システムの終了、打刻システムに戻る機能
    menu = -1 #初期値は-1
    menu = input("全ての打刻履歴を表示する場合は0を、システムを終了させる場合は1を、打刻システムに戻る場合は2を入力して下さい: ")
    try :
        menu = int(menu)
    except ValueError :
        print("入力を間違えています。もう一度やり直してください")
        manage(attendance_list)
    if menu == 0:
        for i in range(len(attendance_list)) :
            name = attendance_list[i][0]
            time = attendance_list[i][1].strftime('%Y-%m-%d %H:%M:%S')
            status = attendance_list[i][2]
            print(name, time, status)
        print("【履歴ここまで】")
        manage(attendance_list) #管理メニューに戻る
    elif menu == 1:
        global loop
        loop = False #打刻システムのループを止める
        return
    elif menu == 2:
        return
    else :
        print("エラーが発生しました。申し訳ありませんがもう一度やり直してください")
        manage(attendance_list) #もう一度管理メニューの選択からやり直す
    return

def state_repeat() :
    state = input("出勤の場合は0を、退勤の場合は1を、管理システムを起動する場合は2を入力してください: ")
    try :
        state = int(state)
        if state == 0 or state == 1 or state == 2 :
            return state
        else :
            print("入力を間違えています。もう一度やり直してください")
            state = state_repeat()
            return state
    except ValueError :
        print("入力を間違えています。もう一度やり直してください")
        state = state_repeat()
        return state

def menu_repeat() :
    menu = input("再度パスワードを入力する場合は0を、打刻システムに戻る場合は1を入力して下さい: ")
    try :
        menu = int(menu)
        if menu == 0 or menu == 1 :
            return menu
        else :
            print("入力を間違えています。もう一度やり直してください")
            menu = menu_repeat()
            return menu
    except ValueError :
        print("入力を間違えています。もう一度やり直してください")
        menu = menu_repeat()
        return menu

def confirm_repeat() :
    confirm = input("正しい場合は0を、間違っている場合は1を入力して下さい: ")
    try :
        confirm = int(confirm)
        if confirm == 0 or confirm == 1 :
            return confirm
        else :
            print("入力を間違えています。もう一度やり直してください")
            confirm = confirm_repeat() #0か1以外の数字でも繰り返す
            return confirm
    except ValueError :
        print("入力を間違えています。もう一度やり直してください")
        confirm = confirm_repeat()
        return confirm

def missed_attendance_repeat() :
    missed_attendance = input("続ける場合は0を、取り消す場合は1を入力して下さい : " )
    try :
        missed_attendance = int(missed_attendance)
        if missed_attendance == 0 or missed_attendance == 1 :
            return missed_attendance
        else :
            print("入力を間違えています。もう一度やり直してください")
            missed_attendance = missed_attendance_repeat() #0か1以外の数字でも繰り返す
            return missed_attendance
    except ValueError :
        print("入力を間違えています。もう一度やり直してください")
        missed_attendance = missed_attendance_repeat()
        return missed_attendance

def count_reset() :
    global count
    count = 0 #ロック解除のメッセージを出したいが入力中だった時にどういう挙動になるか？
    print("ロックが解除されました") #それ以前で上手くいってないので要検討

main()



#1年以上経ったデータは消去？
#取り消し変更する際に上書きしない
#ループを終了するコマンド
#終了する際にバックアップ
#管理者システムを起動するときにパスワードを要求
