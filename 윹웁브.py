import tkinter as tk

# 1. 파이썬 창을 '항상 위에' 떠 있게 설정
root = tk.Tk()
root.title("내 마음대로 UI")
root.geometry("800x450")
root.attributes("-topmost", True)  # 항상 영상 위에 떠 있음
root.attributes("-alpha", 0.8)      # 투명도 조절 (0.0~1.0)

# 2. 채팅창 UI (삭제 요청에 따라 심플하게 버튼 위주로)
# 영상 위에서 클릭 가능한 버튼을 만듭니다.
btn = tk.Button(root, text="재생/일시정지", command=lambda: print("유튜브 제어 신호 전송"))
btn.place(x=50, y=50)

# 3. 이제 브라우저를 열고 이 창을 그 위에 겹치면 됩니다.
# 윈도우에서 창 크기를 맞추면 마치 프로그램 내부에 내장된 것처럼 보입니다.
root.mainloop()