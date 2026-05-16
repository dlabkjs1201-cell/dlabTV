import tkinter as tk
import random


# --- 기능 설정 ---
def start_evade_game():
    # 새로운 게임 창 생성
    game_win = tk.Toplevel(root)
    game_win.title("공 피하기 게임!")
    canvas = tk.Canvas(game_win, width=400, height=400, bg="white")
    canvas.pack()

    # 플레이어 (파란 사각형)
    player = canvas.create_rectangle(180, 350, 220, 390, fill="blue")

    # 장애물 (빨간 원)
    enemy = canvas.create_oval(180, 0, 220, 40, fill="red")
    enemy_speed = 3

    def move_player(event):
        if event.keysym == 'Left': canvas.move(player, -20, 0)
        if event.keysym == 'Right': canvas.move(player, 20, 0)

    game_win.bind("<Left>", move_player)
    game_win.bind("<Right>", move_player)

    def update_game():
        nonlocal enemy_speed
        canvas.move(enemy, 0, enemy_speed)

        # 장애물이 바닥에 닿으면 다시 위로
        if canvas.coords(enemy)[3] > 400:
            canvas.coords(enemy, random.randint(0, 360), 0,
                          random.randint(40, 400), 40)  # 위치 랜덤 재설정
            enemy_speed += 0.5  # 점점 빨라짐

        # 충돌 감지
        p_pos = canvas.coords(player)
        e_pos = canvas.coords(enemy)
        if (p_pos[0] < e_pos[2] and p_pos[2] > e_pos[0] and
                p_pos[1] < e_pos[3] and p_pos[3] > e_pos[1]):
            result_label.config(text="게임오버! 딴짓하지말고 날씨나 뽑으세요")
            game_win.destroy()
            return

        game_win.after(30, update_game)

    # 1. 타이머 제어를 위한 변수 (코드 상단에 추가)
    idle_timer = None

    # 2. 가만히 있을 때 실행할 함수 (start_evade_game 호출용)
    def check_idle():
        global idle_timer
        start_evade_game()  # 게임 실행
        idle_timer = None  # 타이머 초기화

    # 3. 사용자의 움직임을 감지하여 타이머를 초기화하는 함수
    def reset_idle_timer(event=None):
        global idle_timer
        # 이미 돌아가고 있는 타이머가 있다면 취소
        if idle_timer is not None:
            root.after_cancel(idle_timer)

        # 다시 15초(15000ms) 카운트 다운 시작
        idle_timer = root.after(15000, check_idle)

    # --- 아래 설정은 root = tk.Tk() 아래에 넣으세요 ---

    # 4. 마우스 움직임(<Motion>)과 키보드 입력(<Key>) 감지 시 타이머 리셋 설정
    root.bind("<Motion>", reset_idle_timer)
    root.bind("<Key>", reset_idle_timer)

    # 5. 프로그램 시작 시 첫 타이머 가동
    reset_idle_timer()

    update_game()
def pick_weather():
    global day_count, weathers

    # 랜덤 날씨 리스트
    current_weather = random.choice(weathers)

    # 결과 레이블 업데이트 (~일차: 날씨 형식)
    result_label.config(text=f"{day_count}일차: {current_weather}")
    if '비' == current_weather:
        result_label2.config(text="출근길이 매우 막히는군요 :(")
    elif '눈' == current_weather:
        result_label2.config(text="우아! 눈이에요!")
    elif '흐림' == current_weather:
        result_label2.config(text="그냥 그저 그런 날씨네요")
    elif '맑음' == current_weather:
        result_label2.config(text="운동하기 좋은 날씨네요!")
    elif '미세먼지' == current_weather:
        result_label2.config(text="콜록콜록")
    else:
        result_label2.config(text="공습경보 공습경보!!!!")


    # 일차 증가
    day_count += 1


def reset():
    global day_count
    day_count = 1
    result_label.config(text="버튼을 눌러 날씨를 확인하세요!")

weathers = ["맑음", "흐림", "비", "눈", "태풍", "맑음" ,"흐림", "흐림", "미세먼지", "맑음", "흐림"]
# --- 메인 창 설정 ---
root = tk.Tk()
root.title("오늘의 한반도 날씨 뽑기")  # 요청하신 창 제목
root.geometry("350x250")
root.resizable(False, False)

# 전역 변수 (일차 계산용)
day_count = 1

# --- UI 요소 ---
# 제목 안내
title_label = tk.Label(root, text="(천국임)오늘의 한반도 날씨 뽑기", font=("NanumGothic", 16, "bold"), pady=20)
title_label.pack()

# 날씨 결과 표시 창
result_label = tk.Label(root, text="버튼을 눌러 오늘의 한반도 날씨를 확인하세요!", font=("NanumGothic", 12), fg="#333333")
result_label.pack(pady=10)

result_label2 = tk.Label(root, text="", font=("NanumGothic", 12), fg="#333333")
result_label2.pack(pady=10)

# 날씨 뽑기 버튼
pick_btn = tk.Button(root, text="날씨 뽑기", command=pick_weather,
                     width=15, height=2, bg="#4CAF50", fg="white", font=("bold"))
pick_btn.pack(pady=10)

# 초기화 버튼 (작게)
reset_btn = tk.Button(root, text="초기화", command=reset, fg="gray", bd=0)
reset_btn.pack(side="bottom", pady=5)


# 실행
root.after(10000, start_evade_game)
root.mainloop()