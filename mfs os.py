import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # 프로그레스바를 위한 ttk 추가
import random


class MFS_OS:
    def __init__(self, root):
        self.root = root
        self.root.title("MFS OS")
        self.root.geometry("1000x700")
        self.root.configure(bg="white")

        self.menu_visible = False
        self.score = 0
        self.d_playing = False
        self.username = "사용자"

        self.installed = {"game": False, "notepad": False, "calc": False}
        self.dynamic_taskbar_btns = []
        self.dynamic_menu_btns = []

        self.taskbar = tk.Frame(root, bg="#333333", width=100)
        self.taskbar.pack(side=tk.LEFT, fill=tk.Y)
        self.display_area = tk.Frame(root, bg="#1a2a6c")
        self.display_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.setup_ui()

        # [변경] 처음 켤 때: 1. BIOS 부팅 오버레이 띄우기
        self.bios_overlay.place(relwidth=1, relheight=1)
        self.root.after(2000, self.show_install_screen)  # 2초 뒤 설치 화면으로 넘어감

    def setup_ui(self):
        self.create_all_views()

        self.start_button = tk.Button(self.taskbar, text="시작", command=self.toggle_start_menu, bg="#555555", fg="white",
                                      font=("Arial", 11, "bold"))
        self.start_button.pack(side=tk.TOP, pady=(20, 10), padx=10, fill=tk.X)

        self.internet_btn = tk.Button(self.taskbar, text="MFS\n인터넷", command=self.show_internet, bg="#4a90e2",
                                      fg="white", font=("Arial", 10))
        self.internet_btn.pack(side=tk.TOP, pady=5, padx=10, fill=tk.X)

        self.file_btn = tk.Button(self.taskbar, text="파일\n관리자", command=self.show_file_manager, bg="#e67e22",
                                  fg="white", font=("Arial", 10))
        self.file_btn.pack(side=tk.TOP, pady=5, padx=10, fill=tk.X)

        self.game_btn = tk.Button(self.taskbar, text="클릭\n게임", command=self.show_game, bg="#27ae60", fg="white",
                                  font=("Arial", 10))
        self.game_btn.pack(side=tk.TOP, pady=5, padx=10, fill=tk.X)

        tk.Button(self.taskbar, text="바탕화면", command=self.show_desktop, bg="#7f8c8d", fg="white",
                  font=("Arial", 10)).pack(side=tk.BOTTOM, pady=20, padx=10, fill=tk.X)

        self.start_menu = tk.Frame(self.root, bg="#f0f0f0", width=400, height=350, bd=2, relief="raised")
        tk.Frame(self.start_menu, bg="#cccccc", width=2).place(x=215, y=10, height=330)
        tk.Label(self.start_menu, text="모든 프로그램", font=("Arial", 11, "bold"), bg="#f0f0f0").place(x=20, y=20)

        self.update_start_menu_list()

        self.user_label = tk.Label(self.start_menu, text="👤 사용자", font=("Arial", 12, "bold"), bg="#f0f0f0",
                                   fg="#2c3e50")
        self.user_label.place(x=235, y=190)

        tk.Button(self.start_menu, text="다시 시작", command=self.trigger_restart, bg="#f39c12", fg="white",
                  font=("Arial", 10, "bold")).place(x=235, y=230, width=145, height=45)
        tk.Button(self.start_menu, text="전원 끄기", command=self.root.destroy, bg="#ff4d4d", fg="white",
                  font=("Arial", 10, "bold")).place(x=235, y=285, width=145, height=45)

        # ==========================================
        # --- [신규/변경] 초기 부팅 & 설치 오버레이들 ---
        # ==========================================

        # 1. BIOS 부팅 화면
        self.bios_overlay = tk.Frame(self.root, bg="black")
        bios_text = "MFS BIOS v1.02.4\nCopyright (C) 2026 MFS Corp.\n\nChecking System Memory... OK\nInitializing Hardware... OK\nBooting from primary disk...\nStarting MFS Installer..."
        tk.Label(self.bios_overlay, text=bios_text, font=("Consolas", 12), bg="black", fg="lightgray",
                 justify=tk.LEFT).place(x=10, y=10)

        # 2. 설치 안내 화면
        self.install_overlay = tk.Frame(self.root, bg="#2980b9")
        tk.Label(self.install_overlay, text="MFS OS 설치 마법사", font=("Arial", 30, "bold"), bg="#2980b9", fg="white").pack(
            pady=(200, 20))
        tk.Label(self.install_overlay, text="새로운 MFS 환경을 구성합니다.\n계속하려면 다음을 누르세요.", font=("Arial", 14), bg="#2980b9",
                 fg="#ecf0f1", justify="center").pack(pady=20)
        tk.Button(self.install_overlay, text="다음 (Next) >", font=("Arial", 12, "bold"), bg="#f1c40f", fg="#333",
                  command=self.show_setup_screen, padx=20, pady=5).pack(pady=30)

        # 3. 초기 설정(이름 입력) 화면
        self.setup_overlay = tk.Frame(self.root, bg="#2c3e50")
        tk.Label(self.setup_overlay, text="환영합니다!", font=("Arial", 30, "bold"), bg="#2c3e50", fg="white").pack(
            pady=(200, 20))
        tk.Label(self.setup_overlay, text="MFS OS에서 사용할 이름을 입력해주세요.", font=("Arial", 15), bg="#2c3e50",
                 fg="#bdc3c7").pack(pady=10)
        self.name_entry = tk.Entry(self.setup_overlay, font=("Arial", 18), justify="center", width=15)
        self.name_entry.pack(pady=10)
        self.name_entry.bind("<Return>", lambda e: self.start_10s_loading())
        tk.Button(self.setup_overlay, text="설치 시작", font=("Arial", 12, "bold"), bg="#f1c40f", fg="#333",
                  command=self.start_10s_loading, padx=20, pady=5).pack(pady=20)

        # 4. 10초 로딩 화면
        self.loading_overlay = tk.Frame(self.root, bg="#34495e")
        tk.Label(self.loading_overlay, text="MFS OS 설치 중...", font=("Arial", 24, "bold"), bg="#34495e",
                 fg="white").pack(pady=(250, 20))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.loading_overlay, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(pady=10)

        self.loading_pct_label = tk.Label(self.loading_overlay, text="0%", font=("Consolas", 14), bg="#34495e",
                                          fg="#ecf0f1")
        self.loading_pct_label.pack()

        # ==========================================
        # --- [기존] 로그인 및 시스템 오버레이들 ---
        # ==========================================

        self.login_overlay = tk.Frame(self.root, bg="#2c3e50")
        self.login_welcome_label = tk.Label(self.login_overlay, text="환영합니다!", font=("Arial", 30, "bold"), bg="#2c3e50",
                                            fg="white")
        self.login_welcome_label.pack(pady=(250, 20))
        tk.Button(self.login_overlay, text="다시 로그인", font=("Arial", 14, "bold"), bg="#3498db", fg="white",
                  command=self.perform_login, padx=40, pady=10).pack(pady=20)

        self.reboot_overlay = tk.Frame(self.root, bg="black")
        self.reboot_logo = tk.Label(self.reboot_overlay, text="MFS", font=("Arial", 50, "bold"), bg="black", fg="white")
        self.booting_label = tk.Label(self.reboot_overlay, text="부팅 중...", font=("Arial", 15), bg="black", fg="#888888")

        self.error_overlay = tk.Frame(self.root, bg="black")
        self.error_label = tk.Label(self.error_overlay, text="MFS는 읽을 수 있는 파일이 아닙니다. 강제 종료 중...", font=("Consolas", 18),
                                    bg="black", fg="white")

        self.hack_overlay = tk.Frame(self.root, bg="black")
        self.hack_label = tk.Label(self.hack_overlay, text="당신의 컴퓨터는 해킹당했습니다!", font=("Consolas", 24, "bold"),
                                   bg="black", fg="red")

    # --- [신규] 초기 부팅 로직 제어 ---
    def show_install_screen(self):
        self.bios_overlay.place_forget()
        self.install_overlay.place(relwidth=1, relheight=1)

    def show_setup_screen(self):
        self.install_overlay.place_forget()
        self.setup_overlay.place(relwidth=1, relheight=1)
        self.name_entry.focus_set()

    def start_10s_loading(self):
        name = self.name_entry.get().strip()
        if name: self.username = name

        # 이름 세팅 동기화
        self.user_label.config(text=f"👤 {self.username}")
        self.login_welcome_label.config(text=f"{self.username}님, 환영합니다!")

        # 셋업 화면 끄고 로딩 화면 켜기
        self.setup_overlay.place_forget()
        self.loading_overlay.place(relwidth=1, relheight=1)

        # 10초 = 10000ms. 100%로 나누면 1%당 100ms
        self.progress_var.set(0)
        self.update_loading_progress(0)

    def update_loading_progress(self, val):
        if val <= 100:
            self.progress_var.set(val)
            self.loading_pct_label.config(text=f"{val}%")
            self.root.after(100, lambda: self.update_loading_progress(val + 1))  # 100ms 마다 1% 증가 (총 10초)
        else:
            self.loading_overlay.place_forget()
            self.show_desktop()

    def perform_login(self):
        self.login_overlay.place_forget()
        self.show_desktop()

    # --- 기존 OS 로직 완벽 유지 ---
    def update_start_menu_list(self):
        apps = [("MFS 인터넷", "#4a90e2", self.show_internet), ("파일 관리자", "#e67e22", self.show_file_manager),
                ("클릭 게임", "#27ae60", self.show_game), ("명령 프롬프트", "#2c3e50", self.show_terminal)]
        for i, (name, color, cmd) in enumerate(apps):
            tk.Button(self.start_menu, text=name, command=lambda c=cmd: [c(), self.toggle_start_menu()],
                      bg=color, fg="white", font=("Arial", 10, "bold"), relief="flat", anchor="w", padx=10).place(x=20,
                                                                                                                  y=60 + (
                                                                                                                              i * 35),
                                                                                                                  width=175,
                                                                                                                  height=30)

    def create_file_manager_view(self):
        self.file_frame = tk.Frame(self.display_area, bg="#ecf0f1")
        tk.Button(self.file_frame, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white",
                  relief="flat").place(relx=1.0, x=-10, y=10, anchor="ne")
        tk.Label(self.file_frame, text="MFS 시스템 관리 도구", font=("Arial", 20, "bold"), bg="#ecf0f1").pack(pady=40)
        tk.Button(self.file_frame, text="MFS 인터넷 삭제", command=self.delete_internet_action, bg="#34495e", fg="white",
                  font=("Arial", 12), width=25, pady=10).pack(pady=10)
        tk.Button(self.file_frame, text="파일 모두 삭제", command=self.trigger_system_error, bg="#c0392b", fg="white",
                  font=("Arial", 12, "bold"), width=25, pady=10).pack(pady=10)
        tk.Label(self.file_frame, text="주의: 시스템 파일이 삭제될 수 있습니다.", font=("Arial", 10), bg="#ecf0f1", fg="#7f8c8d").pack(
            pady=5)

    def delete_internet_action(self):
        if messagebox.askyesno("확인", "정말로 MFS 인터넷을 삭제하시겠습니까?"):
            messagebox.showinfo("진행 중", "MFS 인터넷 구성 요소를 제거하고 있습니다...")
            self.root.after(3000, self.finalize_internet_deletion)

    def finalize_internet_deletion(self):
        self.internet_btn.pack_forget()
        messagebox.showinfo("완료", "MFS 인터넷이 성공적으로 삭제되었습니다.")
        self.show_desktop()

    def create_internet_view(self):
        self.internet_frame = tk.Frame(self.display_area, bg="#f9f9f9")
        self.internet_content = tk.Frame(self.internet_frame, bg="#f9f9f9")
        self.internet_content.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.internet_content, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white",
                  relief="flat").place(relx=1.0, x=-10, y=10, anchor="ne")
        tk.Label(self.internet_content, text="MFS 인터넷 검색", font=("Arial", 20, "bold"), bg="#f9f9f9").pack(pady=30)

        sc = tk.Frame(self.internet_content, bg="#f9f9f9");
        sc.pack(pady=10)
        self.search_entry = tk.Entry(sc, width=50, font=("Arial", 14), bd=2);
        self.search_entry.pack(side=tk.LEFT, padx=10, ipady=8)
        tk.Button(sc, text="검색", width=15, bg="#4a90e2", fg="white", font=("Arial", 11, "bold"),
                  command=self.show_dino_game).pack(side=tk.LEFT, ipady=5)

        dl_f = tk.LabelFrame(self.internet_content, text="MFS 인터넷 다운로더", bg="#f9f9f9", padx=20, pady=20)
        dl_f.pack(side=tk.BOTTOM, fill=tk.X, padx=50, pady=30)
        dls = [("게임 다운로드", "game", "#9b59b6"), ("메모장 다운로드", "notepad", "#34495e"), ("계산기 다운로드", "calc", "#16a085")]
        for t, k, c in dls: tk.Button(dl_f, text=t, bg=c, fg="white", font=("Arial", 10, "bold"),
                                      command=lambda key=k: self.install_app(key)).pack(side=tk.LEFT, padx=15,
                                                                                        expand=True, fill=tk.X)

        self.dino_bg = tk.Frame(self.internet_frame, bg="white")

    def show_dino_game(self):
        self.search_entry.delete(0, tk.END);
        self.internet_content.pack_forget();
        self.dino_bg.pack(fill=tk.BOTH, expand=True)
        for w in self.dino_bg.winfo_children(): w.destroy()
        tk.Button(self.dino_bg, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white", relief="flat").place(
            relx=1.0, x=-10, y=10, anchor="ne")
        tk.Label(self.dino_bg, text="인터넷 연결 없음", font=("Arial", 24, "bold"), bg="white", fg="#555").pack(pady=(50, 10))
        tk.Label(self.dino_bg, text="ERR_INTERNET_DISCONNECTED\n스페이스바를 눌러 게임을 시작하세요.", font=("Arial", 12), bg="white",
                 fg="#888").pack()
        self.d_canvas = tk.Canvas(self.dino_bg, width=600, height=200, bg="white", highlightthickness=0);
        self.d_canvas.pack(pady=30)
        self.d_canvas.create_line(0, 180, 600, 180, fill="#555", width=2)
        self.dino = self.d_canvas.create_rectangle(50, 150, 80, 180, fill="#555")
        self.cactus = self.d_canvas.create_rectangle(600, 150, 620, 180, fill="#27ae60")
        self.d_score_txt = self.d_canvas.create_text(500, 20, text="00000", font=("Consolas", 14), fill="#555")
        self.d_y, self.d_vy, self.d_score = 150, 0, 0
        self.d_is_jumping, self.d_game_over, self.d_playing = False, False, False
        self.root.bind("<space>", self.dino_jump)

    def dino_jump(self, event=None):
        if self.d_game_over:
            self.d_game_over = False;
            self.d_score = 0
            self.d_canvas.coords(self.cactus, 600, 150, 620, 180)
            self.d_canvas.itemconfig(self.dino, fill="#555");
            self.d_canvas.delete("gameover")
            self.d_playing = True;
            self.dino_loop()
        elif not self.d_playing:
            self.d_playing = True; self.dino_loop()
        elif not self.d_is_jumping:
            self.d_vy = -15; self.d_is_jumping = True

    def dino_loop(self):
        if not self.d_playing or self.d_game_over or not self.dino_bg.winfo_ismapped(): return
        self.d_vy += 1.5;
        self.d_y += self.d_vy
        if self.d_y > 150: self.d_y = 150; self.d_is_jumping = False; self.d_vy = 0
        self.d_canvas.coords(self.dino, 50, self.d_y, 80, self.d_y + 30)
        self.d_canvas.move(self.cactus, -10, 0)
        cx1, cy1, cx2, cy2 = self.d_canvas.coords(self.cactus)
        if cx2 < 0: self.d_canvas.move(self.cactus, 600 + random.randint(50, 300), 0)
        dx1, dy1, dx2, dy2 = self.d_canvas.coords(self.dino)
        if (dx1 < cx2 and dx2 > cx1 and dy1 < cy2 and dy2 > cy1):
            self.d_game_over = True;
            self.d_canvas.itemconfig(self.dino, fill="red")
            self.d_canvas.create_text(300, 100, text="GAME OVER", font=("Arial", 24, "bold"), fill="red",
                                      tags="gameover")
            return
        self.d_score += 1;
        self.d_canvas.itemconfig(self.d_score_txt, text=f"{self.d_score // 5:05d}")
        self.root.after(30, self.dino_loop)

    def install_app(self, key):
        if self.installed[key]: return
        messagebox.showinfo("다운로드 시작", "다운로드를 시작합니다. 5초만 기다려 주세요...")
        self.root.after(5000, lambda: self.finalize_install(key))

    def finalize_install(self, key):
        self.installed[key] = True
        messagebox.showinfo("다운로드 완료", "다운로드가 완료되었습니다!")
        if key == "game":
            self.add_to_ui("숫자 게임", "#9b59b6", self.show_new_game, 200)
        elif key == "notepad":
            self.add_to_ui("MFS 메모장", "#34495e", self.show_notepad, 235)
        elif key == "calc":
            self.add_to_ui("MFS 계산기", "#16a085", self.show_calc, 270)

    def add_to_ui(self, name, color, cmd, menu_y):
        btn = tk.Button(self.taskbar, text=name.replace(" ", "\n"), command=cmd, bg=color, fg="white",
                        font=("Arial", 9))
        btn.pack(side=tk.TOP, pady=5, padx=10, fill=tk.X);
        self.dynamic_taskbar_btns.append(btn)
        m_btn = tk.Button(self.start_menu, text=name, command=lambda: [cmd(), self.toggle_start_menu()],
                          bg=color, fg="white", font=("Arial", 10, "bold"), relief="flat", anchor="w", padx=10)
        m_btn.place(x=20, y=menu_y, width=175, height=30)
        self.update_start_menu_list()

    def trigger_restart(self):
        if self.menu_visible: self.toggle_start_menu()
        self.root.after(2000, self.step1_black_out)

    def step1_black_out(self):
        self.reboot_overlay.place(relwidth=1, relheight=1);
        self.root.after(1500, self.step2_show_logo)

    def step2_show_logo(self):
        self.reboot_logo.place(relx=0.5, rely=0.45, anchor="center");
        self.root.after(2000, self.step3_show_booting)

    def step3_show_booting(self):
        self.booting_label.place(relx=0.5, rely=0.6, anchor="center");
        self.root.after(3000, self.finalize_restart)

    def finalize_restart(self):
        self.search_entry.delete(0, tk.END)
        self.score = 0
        self.score_lbl.config(text="점수: 0")

        self.terminal_entry.config(state=tk.NORMAL)
        self.terminal_log.config(state=tk.NORMAL)
        self.terminal_log.delete('1.0', tk.END)
        self.terminal_log.insert(tk.END, "MFS OS Terminal [Version 1.0.0]\n(c) 2026 MFS Corporation.\n")
        self.terminal_log.config(state=tk.DISABLED)

        self.hide_all()
        self.reboot_overlay.place_forget()

        # 재부팅 시 다시 설치 안하고 로그인 화면으로 직행
        self.login_overlay.place(relwidth=1, relheight=1)

    def create_terminal_view(self):
        self.terminal_frame = tk.Frame(self.display_area, bg="black")
        tb = tk.Frame(self.terminal_frame, bg="#333", height=30);
        tb.pack(fill=tk.X)
        tk.Button(tb, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white", relief="flat").pack(
            side=tk.RIGHT)
        self.terminal_log = tk.Text(self.terminal_frame, bg="black", fg="#00ff00", font=("Consolas", 11),
                                    state=tk.DISABLED);
        self.terminal_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ic = tk.Frame(self.terminal_frame, bg="black");
        ic.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(ic, text="MFS://command/:", bg="black", fg="#00ff00", font=("Consolas", 11)).pack(side=tk.LEFT)
        self.terminal_entry = tk.Entry(ic, bg="black", fg="white", font=("Consolas", 11), relief="flat",
                                       insertbackground="white");
        self.terminal_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.terminal_entry.bind("<Return>", self.process_command)
        self.write_to_terminal("MFS OS Terminal [Version 1.0.0]\n(c) 2026 MFS Corporation.\n")

    def process_command(self, event):
        cmd = self.terminal_entry.get().strip();
        self.write_to_terminal(f"MFS://command/:{cmd}");
        self.terminal_entry.delete(0, tk.END)

        if cmd == "ending":
            self.trigger_ending()
        elif cmd == "download virus":
            self.trigger_virus_hack()
        elif cmd == "rickroll":
            self.write_to_terminal("Never gonna give you up, never gonna let you down")
        elif cmd == "/c rd /s /q c":
            self.trigger_destruction()
        elif cmd == "help":
            self.write_to_terminal("사용 가능한 명령어: help, cls, exit, ver, ending, download virus")
        elif cmd == "ver":
            self.write_to_terminal("MFS OS [Version 1.0.0.42]")
        elif cmd == "cls":
            self.terminal_log.config(state=tk.NORMAL); self.terminal_log.delete('1.0',
                                                                                tk.END); self.terminal_log.config(
                state=tk.DISABLED)
        elif cmd == "exit":
            self.show_desktop()
        else:
            self.write_to_terminal(f"'{cmd}'은(는) 유효하지 않습니다.")

    def trigger_ending(self):
        self.terminal_entry.config(state=tk.DISABLED)
        self.write_to_terminal("이건 사실 가짜 os야!")
        self.root.after(3000, self.ending_part2)

    def ending_part2(self):
        self.write_to_terminal("잘 봤으면 고마워~")
        self.root.after(4000, self.root.destroy)

    def trigger_virus_hack(self):
        self.terminal_entry.config(state=tk.DISABLED)
        v_list = [f"MFS://malware_payload_{i:02d}.exe" for i in range(1, 31)]

        def log_v(i):
            if i < len(v_list):
                self.write_to_terminal(f"다운로드 중: {v_list[i]} ... 완료"); self.root.after(20, lambda: log_v(i + 1))
            else:
                self.root.after(1000, lambda: [self.hack_overlay.place(relwidth=1, relheight=1),
                                               self.hack_label.place(relx=0.5, rely=0.5, anchor="center")])

        log_v(0)

    def trigger_destruction(self):
        self.terminal_entry.config(state=tk.DISABLED)
        f_list = [f"C:/MFS_OS/sys_{i:03d}.dll" for i in range(1, 71)] + [f"MFS://file:{i}.exe" for i in range(1, 31)]

        def log_d(i):
            if i < len(f_list):
                self.write_to_terminal(f"삭제 중: {f_list[i]} ... 완료"); self.root.after(random.randint(10, 100),
                                                                                     lambda: log_d(i + 1))
            else:
                self.root.after(500, lambda: [self.error_overlay.place(relwidth=1, relheight=1),
                                              self.error_label.place(relx=0.5, rely=0.5, anchor="center"),
                                              self.root.after(4000, self.root.destroy)])

        log_d(0)

    def write_to_terminal(self, txt):
        self.terminal_log.config(state=tk.NORMAL);
        self.terminal_log.insert(tk.END, txt + "\n");
        self.terminal_log.see(tk.END);
        self.terminal_log.config(state=tk.DISABLED)

    def create_game_view(self):
        self.game_frame = tk.Frame(self.display_area, bg="#2ecc71")
        tk.Button(self.game_frame, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white",
                  relief="flat").place(relx=1.0, x=-10, y=10, anchor="ne")
        tk.Label(self.game_frame, text="가벼운 클릭게임!", font=("Arial", 24, "bold"), bg="#2ecc71", fg="white").pack(pady=20)
        self.score_lbl = tk.Label(self.game_frame, text="점수: 0", font=("Arial", 15), bg="#2ecc71", fg="white")
        self.score_lbl.pack(pady=10)
        self.target = tk.Button(self.game_frame, text="나를 눌러봐!", command=self.hit, bg="#f1c40f",
                                font=("Arial", 10, "bold"), padx=10, pady=5)
        self.target.place(x=300, y=300)

    def hit(self):
        self.score += 1;
        self.score_lbl.config(text=f"점수: {self.score}");
        self.target.place(x=random.randint(50, 700), y=random.randint(150, 500))

    def create_calc_view(self):
        self.calc_frame = tk.Frame(self.display_area, bg="#ecf0f1")
        tk.Button(self.calc_frame, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white",
                  relief="flat").place(relx=1.0, x=-10, y=10, anchor="ne")
        tk.Label(self.calc_frame, text="MFS 계산기", font=("Arial", 20, "bold"), bg="#ecf0f1").pack(pady=20)
        self.calc_ent = tk.Entry(self.calc_frame, font=("Arial", 24), justify="right", bd=10);
        self.calc_ent.pack(pady=10, padx=20, fill=tk.X)
        btn_f = tk.Frame(self.calc_frame, bg="#ecf0f1");
        btn_f.pack()
        for i, b in enumerate(['7', '8', '9', '/', '4', '5', '6', '*', '1', '2', '3', '-', 'C', '0', '=', '+']):
            tk.Button(btn_f, text=b, width=5, height=2, font=("Arial", 12, "bold"),
                      command=lambda x=b: self.calc_press(x)).grid(row=i // 4, column=i % 4, padx=5, pady=5)

    def calc_press(self, char):
        if char == '=':
            try:
                res = eval(self.calc_ent.get()); self.calc_ent.delete(0, tk.END); self.calc_ent.insert(0, res)
            except:
                self.calc_ent.delete(0, tk.END); self.calc_ent.insert(0, "Error")
        elif char == 'C':
            self.calc_ent.delete(0, tk.END)
        else:
            self.calc_ent.insert(tk.END, char)

    def create_notepad_view(self):
        self.notepad_frame = tk.Frame(self.display_area, bg="white")
        title = tk.Frame(self.notepad_frame, bg="#34495e", height=30);
        title.pack(fill=tk.X)
        tk.Button(title, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white", relief="flat").pack(
            side=tk.RIGHT)
        tk.Text(self.notepad_frame, font=("Arial", 12)).pack(fill=tk.BOTH, expand=True)

    def create_new_game_view(self):
        self.new_game_frame = tk.Frame(self.display_area, bg="#9b59b6")
        tk.Button(self.new_game_frame, text=" X ", command=self.show_desktop, bg="#ff4d4d", fg="white",
                  relief="flat").place(relx=1.0, x=-10, y=10, anchor="ne")
        tk.Label(self.new_game_frame, text="숫자 맞추기 (1~50)", font=("Arial", 20, "bold"), bg="#9b59b6", fg="white").pack(
            pady=30)
        self.ans = random.randint(1, 50);
        self.num_ent = tk.Entry(self.new_game_frame, font=("Arial", 18));
        self.num_ent.pack(pady=10)
        tk.Button(self.new_game_frame, text="확인", command=self.check_num, font=("Arial", 12)).pack(pady=10)
        self.res_lbl = tk.Label(self.new_game_frame, text="1~50 입력", bg="#9b59b6", fg="white", font=("Arial", 14));
        self.res_lbl.pack()

    def check_num(self):
        try:
            v = int(self.num_ent.get())
            if v == self.ans:
                self.res_lbl.config(text="정답!"); self.ans = random.randint(1, 50)
            else:
                self.res_lbl.config(text="UP" if v < self.ans else "DOWN")
        except:
            pass

    def create_all_views(self):
        self.desktop_frame = tk.Frame(self.display_area, bg="#1a2a6c")
        tk.Label(self.desktop_frame, text="MFS OS", font=("Arial", 30, "bold"), bg="#1a2a6c", fg="white").place(
            relx=0.5, rely=0.5, anchor="center")
        self.create_internet_view();
        self.create_file_manager_view();
        self.create_terminal_view()
        self.create_game_view();
        self.create_notepad_view();
        self.create_calc_view();
        self.create_new_game_view()

    def hide_all(self):
        try:
            self.root.unbind("<space>"); self.d_playing = False
        except:
            pass
        self.desktop_frame.pack_forget()
        for f in [self.internet_frame, self.file_frame, self.game_frame, self.terminal_frame, self.notepad_frame,
                  self.calc_frame, self.new_game_frame]: f.pack_forget()

    def show_desktop(self):
        self.hide_all(); self.desktop_frame.pack(fill=tk.BOTH, expand=True)

    def show_internet(self):
        self.hide_all(); self.dino_bg.pack_forget(); self.internet_content.pack(fill=tk.BOTH,
                                                                                expand=True); self.internet_frame.pack(
            fill=tk.BOTH, expand=True)

    def show_file_manager(self):
        self.hide_all(); self.file_frame.pack(fill=tk.BOTH, expand=True)

    def show_game(self):
        self.hide_all(); self.game_frame.pack(fill=tk.BOTH, expand=True)

    def show_terminal(self):
        self.hide_all(); self.terminal_frame.pack(fill=tk.BOTH, expand=True); self.terminal_entry.focus_set()

    def show_notepad(self):
        self.hide_all(); self.notepad_frame.pack(fill=tk.BOTH, expand=True)

    def show_calc(self):
        self.hide_all(); self.calc_frame.pack(fill=tk.BOTH, expand=True)

    def show_new_game(self):
        self.hide_all(); self.new_game_frame.pack(fill=tk.BOTH, expand=True)

    def trigger_system_error(self):
        messagebox.showwarning("경고", "시스템 파일을 삭제합니다.");
        self.root.after(5000, lambda: [messagebox.showerror("에러", "MFS_OS.exe 없음"), self.root.destroy()])

    def toggle_start_menu(self):
        if self.menu_visible:
            self.start_menu.place_forget(); self.menu_visible = False
        else:
            self.start_menu.place(x=100, y=20); self.menu_visible = True


if __name__ == "__main__":
    root = tk.Tk()
    app = MFS_OS(root)
    root.mainloop()