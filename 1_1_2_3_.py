import tkinter as tk
import webbrowser
from tkinter import messagebox
import random

# ----------------------------
# 사용자 고정 문제 (항상 포함)
# ----------------------------
FIXED_QUESTIONS = [
    {'q': '갤럭시 S시리즈를 공개하는 달은?', 'choices': ['1월', '2월', '3월', '4월'], 'answer': '2월'},
    {'q': '한컴타자연습 2005~2007버전에 있던 이스터에그 음악 원본 파일은?', 'choices': ['gmusic1.mid', 'gmusic2.mid', 'easter.mid', 'hkmusic.mid'], 'answer': 'gmusic2.mid'},
]

# ----------------------------
# 기본 문제 은행 (쉬운~쉬운 난이도)
# ----------------------------
OTHER_QUESTIONS = [
    {'q': '파이썬 파일 확장자는?', 'choices': ['.py', '.txt', '.doc', '.jpg'], 'answer': '.py'},
    {'q': '한국의 수도는?', 'choices': ['부산', '대구', '서울', '광주'], 'answer': '서울'},
    {'q': '태양계에서 가장 큰 행성은?', 'choices': ['지구', '화성', '목성', '금성'], 'answer': '목성'},
    {'q': '물의 끓는점(섭씨)은?', 'choices': ['0', '50', '100', '200'], 'answer': '100'},
    {'q': '원주율 π의 근삿값은?', 'choices': ['2.14', '3.14', '4.14', '1.41'], 'answer': '3.14'},
    {'q': '이진수 1010은 십진수로?', 'choices': ['8', '9', '10', '11'], 'answer': '10'},
    {'q': 'HTML 문서의 기본 태그는?', 'choices': ['<html>', '<head>', '<body>', '<div>'], 'answer': '<html>'},
    {'q': '이미지 무손실 포맷은?', 'choices': ['JPEG', 'PNG', 'GIF', 'BMP'], 'answer': 'PNG'},
    {'q': '인터넷의 약자 IP는?', 'choices': ['Internet Program', 'Internet Protocol', 'Internal Program', 'Internal Protocol'], 'answer': 'Internet Protocol'},
    {'q': 'CPU의 약자는?', 'choices': ['Central Processing Unit', 'Computer Processing Unit', 'Central Program Unit', 'Control Processing Unit'], 'answer': 'Central Processing Unit'},
    {'q': '지구의 위성은?', 'choices': ['화성', '달', '태양', '금성'], 'answer': '달'},
    {'q': '음악 파일 확장자 중 하나는?', 'choices': ['.mp3', '.exe', '.zip', '.txt'], 'answer': '.mp3'},
    {'q': '웹 주소에서 https의 s는?', 'choices': ['speed', 'secure', 'server', 'simple'], 'answer': 'secure'},
    {'q': '문서 편집 프로그램의 대표는?', 'choices': ['Word', 'Chrome', 'Photoshop', 'VLC'], 'answer': 'Word'},
    {'q': '계산기에서 더하기 기호는?', 'choices': ['-', '+', '*', '/'], 'answer': '+'},
    {'q': '사과의 영어 단어는?', 'choices': ['Banana', 'Apple', 'Grape', 'Orange'], 'answer': 'Apple'},
    {'q': '하늘이 파란 이유는?', 'choices': ['중력', '대기 산란', '지구 자전', '태양 온도'], 'answer': '대기 산란'},
]

# ----------------------------
# 추가 라운드 문제 (조금 어려운 수준)
# ----------------------------
HARD_QUESTIONS = [
    {'q': 'GPU 성능 단위로 흔히 쓰이는 TFLOPS는 무엇을 의미하나?', 'choices': ['테라플롭스', '테라바이트', '테라헤르츠', '테라볼트'], 'answer': '테라플롭스'},
    {'q': 'MIDI 파일의 확장자는?', 'choices': ['.mid', '.mp3', '.wav', '.ogg'], 'answer': '.mid'},
    {'q': '그래픽카드에서 레이트레이싱 전용 유닛은?', 'choices': ['RT Core', 'Tensor Core', 'Shader Core', 'Raster Core'], 'answer': 'RT Core'},
]

# ----------------------------
# 설정값
# ----------------------------
TOTAL_QUESTIONS = 10
PASS_THRESHOLD = 7
FINAL_URL = "https://sliding.toys/mystic-square/8-puzzle/daily/"  # 마지막 OK에서 이동할 주소로 바꿔주세요

HARD_TOTAL = 3
HARD_PASS_THRESHOLD = 2  # 추가 라운드에서 3문제 중 2문제 이상 맞추면 통과

# 최종 메시지들 (사용자가 원하는 문구로 바꿔 쓰세요)
FINAL_MESSAGES = [
    "여긴 왜왔어",
    "감히 이 자리를 도전하다니",
    "대단한걸"
]

# ----------------------------
# 메인 퀴즈 앱 클래스
# ----------------------------
class QuizApp:
    def __init__(self, master):
        self.master = master
        master.title("도전하기")
        master.resizable(False, False)

        self.score = 0
        self.current_index = 0
        self.selected_questions = []

        # UI
        self.lbl_score = tk.Label(master, text=f"점수: {self.score}", font=("Arial", 12))
        self.lbl_score.pack(pady=(10,0))

        self.lbl_progress = tk.Label(master, text="", font=("Arial", 10))
        self.lbl_progress.pack(pady=(0,10))

        self.lbl_question = tk.Label(master, text="", wraplength=600, font=("Arial", 14))
        self.lbl_question.pack(padx=20, pady=10)

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(padx=20, pady=(0,10))

        self.choice_buttons = []
        for i in range(4):
            btn = tk.Button(self.buttons_frame, text="", width=50, anchor="w",
                            command=lambda idx=i: self.check_answer(idx))
            btn.grid(row=i, column=0, pady=4)
            self.choice_buttons.append(btn)

        self.lbl_feedback = tk.Label(master, text="", font=("Arial", 11))
        self.lbl_feedback.pack(pady=(5,10))

        self.btn_next = tk.Button(master, text="다음 문제", state="disabled", command=self.next_question)
        self.btn_next.pack(pady=(0,10))

        self.btn_restart = tk.Button(master, text="다시 시작", command=self.restart)
        self.btn_restart.pack(pady=(0,10))

        self.prepare_questions()
        self.start_quiz()

    def prepare_questions(self):
        pool = OTHER_QUESTIONS.copy()
        needed = TOTAL_QUESTIONS - len(FIXED_QUESTIONS)
        if needed <= 0:
            self.selected_questions = FIXED_QUESTIONS[:TOTAL_QUESTIONS]
        else:
            extra = random.sample(pool, needed)
            self.selected_questions = FIXED_QUESTIONS + extra
        random.shuffle(self.selected_questions)

    def start_quiz(self):
        self.score = 0
        self.current_index = 0
        self.update_score_label()
        self.lbl_feedback.config(text="")
        self.show_question()

    def show_question(self):
        qdata = self.selected_questions[self.current_index]
        self.lbl_question.config(text=qdata['q'])
        choices = qdata['choices'].copy()
        random.shuffle(choices)
        for btn, choice in zip(self.choice_buttons, choices):
            btn.config(text=choice, state="normal", bg="SystemButtonFace")
        self.lbl_progress.config(text=f"문제 {self.current_index+1} / {TOTAL_QUESTIONS}")
        self.btn_next.config(state="disabled")
        self.lbl_feedback.config(text="")

    def check_answer(self, idx):
        # 중복 클릭 방지
        for btn in self.choice_buttons:
            btn.config(state="disabled")

        chosen_text = self.choice_buttons[idx].cget('text')
        correct = self.selected_questions[self.current_index]['answer']

        if chosen_text == correct:
            self.score += 1
            self.lbl_feedback.config(text="정답! +1점", fg="green")
            self.choice_buttons[idx].config(bg="#b6f0b6")
        else:
            self.score = max(0, self.score - 1)
            self.lbl_feedback.config(text=f"오답! 정답: {correct}  -1점", fg="red")
            self.choice_buttons[idx].config(bg="#f0b6b6")
            for btn in self.choice_buttons:
                if btn.cget('text') == correct:
                    btn.config(bg="#b6f0b6")
                    break

        self.update_score_label()
        self.btn_next.config(state="normal")

    def next_question(self):
        self.current_index += 1
        if self.current_index >= TOTAL_QUESTIONS:
            self.finish_quiz()
        else:
            self.show_question()

    def update_score_label(self):
        self.lbl_score.config(text=f"점수: {self.score}")

    def finish_quiz(self):
        # 기본 퀴즈 종료 판정
        if self.score >= PASS_THRESHOLD:
            # 추가 라운드 시작
            self.start_hard_round()
        else:
            title = "패배"
            msg = f"오랜만에 도전해서 잘하는줄 알았더니 {self.score}점밖에 안돼네"
            messagebox.showinfo(title, msg)
            for btn in self.choice_buttons:
                btn.config(state="disabled")
            self.btn_next.config(state="disabled")

    # ----------------------------
    # 추가 라운드 관련
    # ----------------------------
    def start_hard_round(self):
        # 새 창으로 추가 라운드 진행
        hard_win = tk.Toplevel(self.master)
        hard_win.title("추가 라운드")
        hard_win.resizable(False, False)
        HardRound(hard_win, HARD_QUESTIONS, HARD_PASS_THRESHOLD, self.on_hard_round_result)

    def on_hard_round_result(self, passed):
        # 추가 라운드 결과 콜백
        if passed:
            # 통과하면 최종 메시지 창 띄우기
            self.show_final_messages()
        else:
            messagebox.showinfo("추가 라운드 결과", "추가 라운드를 통과하지 못했습니다.")

    # ----------------------------
    # 최종 메시지 창
    # ----------------------------
    def show_final_messages(self):
        final_win = tk.Toplevel(self.master)
        final_win.title("메시지")
        final_win.resizable(False, False)

        idx = {'value': 0}
        lbl = tk.Label(final_win, text=FINAL_MESSAGES[idx['value']], wraplength=400, font=("Arial", 12))
        lbl.pack(padx=20, pady=20)

        def on_ok():
            idx['value'] += 1
            if idx['value'] < len(FINAL_MESSAGES):
                lbl.config(text=FINAL_MESSAGES[idx['value']])
            else:
                # 마지막 메시지의 OK를 누르면 지정한 URL로 이동 후 창 닫기
                if 'FINAL_URL' in globals() and FINAL_URL:
                    webbrowser.open(FINAL_URL)
                final_win.destroy()

        btn_ok = tk.Button(final_win, text="OK", width=10, command=on_ok)
        btn_ok.pack(pady=(0, 20))

    def restart(self):
        self.prepare_questions()
        self.start_quiz()

# ----------------------------
# 추가 라운드 전용 클래스
# ----------------------------
class HardRound:
    def __init__(self, master, questions, pass_threshold, callback):
        self.master = master
        self.questions = questions.copy()
        random.shuffle(self.questions)
        self.questions = self.questions[:HARD_TOTAL]
        self.pass_threshold = pass_threshold
        self.callback = callback

        self.score = 0
        self.index = 0

        # UI
        self.lbl_info = tk.Label(master, text=f"추가 라운드: {len(self.questions)}문제 중 {self.pass_threshold}문제 이상 맞추면 통과", font=("Arial", 11))
        self.lbl_info.pack(pady=(10,0))

        self.lbl_question = tk.Label(master, text="", wraplength=500, font=("Arial", 13))
        self.lbl_question.pack(padx=20, pady=8)

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(padx=20, pady=(0,10))

        self.choice_buttons = []
        for i in range(4):
            btn = tk.Button(self.buttons_frame, text="", width=45, anchor="w",
                            command=lambda idx=i: self.check_answer(idx))
            btn.grid(row=i, column=0, pady=4)
            self.choice_buttons.append(btn)

        self.lbl_feedback = tk.Label(master, text="", font=("Arial", 11))
        self.lbl_feedback.pack(pady=(5,10))

        self.btn_next = tk.Button(master, text="다음", state="disabled", command=self.next_q)
        self.btn_next.pack(pady=(0,10))

        self.show_q()

    def show_q(self):
        q = self.questions[self.index]
        self.lbl_question.config(text=q['q'])
        choices = q['choices'].copy()
        random.shuffle(choices)
        for btn, c in zip(self.choice_buttons, choices):
            btn.config(text=c, state="normal", bg="SystemButtonFace")
        self.lbl_feedback.config(text="")
        self.btn_next.config(state="disabled")

    def check_answer(self, idx):
        for btn in self.choice_buttons:
            btn.config(state="disabled")

        chosen = self.choice_buttons[idx].cget('text')
        correct = self.questions[self.index]['answer']
        if chosen == correct:
            self.score += 1
            self.lbl_feedback.config(text="정답!", fg="green")
            self.choice_buttons[idx].config(bg="#b6f0b6")
        else:
            self.lbl_feedback.config(text=f"오답. 정답: {correct}", fg="red")
            self.choice_buttons[idx].config(bg="#f0b6b6")
            for btn in self.choice_buttons:
                if btn.cget('text') == correct:
                    btn.config(bg="#b6f0b6")
                    break

        self.btn_next.config(state="normal")

    def next_q(self):
        self.index += 1
        if self.index >= len(self.questions):
            passed = (self.score >= self.pass_threshold)
            # 창 닫고 콜백 호출
            self.master.destroy()
            self.callback(passed)
        else:
            self.show_q()
print("실행중...")
print("시작!")
# ----------------------------
# 실행
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
