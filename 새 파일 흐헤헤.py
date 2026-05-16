import tkinter as tk
import random

def check_guess():
    try:
        guess=int(entry.get())
        if guess<target:
            result_label.config(text="너무낮아!")
        elif guess>target:
            result_label.config(text="너무 높아!")
        else:
            result_label.config(text="정답이야 임마")
        if guess==321:
            result_label.config(text="안녕하세요 저는 트위치에서 방송을 하고있는 스트리머 케인입니다 먼저 저의 말과 행동으로 인해 큰 피해롤 끼치고 실망을 드린 샌드백님 시청자분들께 죄송합니다 지금부터는")
    except ValueError:
        result_label.config(text="숫자를 입력해야지")

def reset_game():
    global target
    target=random.randint(1,100)
    result_label.config(text="태초마을로 온걸 환영해~")
    entry.delete(0,tk.END)
root = tk.Tk()
root.title("숫자 추측 게이ㅁ")

target=random.randint(1,100)
tk.Label(root, text="1에서 100 사이의 수ㅅㅈㅏㄹㅡㄹ ㅁㅏㅈㅊㅜㅓㅂㅗㅅㅔ요!").pack()

entry=tk.Entry(root)
entry.pack()

check_btn = tk.Button(root, text="확인",command=check_guess)
check_btn.pack()

check_btn = tk.Button(root, text="재설정",command=reset_game)
check_btn.pack()

result_label=tk.Label(root,text="")
result_label.pack()

root.mainloop()