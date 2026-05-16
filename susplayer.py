import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk
import os
import time
import threading
from queue import Queue, Empty
import sys
import av
import miniaudio
import uuid
import glob
import random


class Replayer:
    def __init__(self, root):
        self.root = root
        self.root.title("REPLAYER")
        self.root.geometry("940x820")
        self.root.configure(bg="#d9d9d9")

        self.cap = None
        self.is_playing = False
        self.fps = 60
        self.total_frames = 0
        self.volume_on = True

        self.audio_device = None
        self.audio_stream = None
        self.temp_audio_path = ""
        self.cleanup_old_caches()

        self.frame_queue = Queue(maxsize=2)

        self.start_time = 0
        self.start_frame = 0
        self.seek_target = None

        self.was_playing_before_drag = False
        self.last_scrub_time = 0

        self.idle_anim_id = None

        self.root.bind("<Left>", lambda e: self.skip_time(-10))
        self.root.bind("<Right>", lambda e: self.skip_time(10))

        self.top_frame = tk.Frame(root, bg="#d9d9d9")
        self.top_frame.pack(fill="x", side="top", padx=10, pady=0)

        self.btn_menu = tk.Button(self.top_frame, text="⋮", font=("Arial", 18, "bold"),
                                  bg="#d9d9d9", relief="flat", activebackground="#cccccc",
                                  command=self.toggle_settings, cursor="hand2",
                                  width=1, padx=2, pady=0)
        self.btn_menu.pack(side="right")

        self.btn_quit = tk.Button(self.top_frame, text="나가기", font=("맑은 고딕", 10, "bold"),
                                  bg="#d9d9d9", relief="flat", fg="#cc0000",
                                  activebackground="#ffcccc",
                                  command=self.root.destroy, cursor="hand2")
        self.btn_quit.pack(side="right", padx=(0, 10), pady=5)

        self.divider = tk.Frame(root, bg="#aaaaaa", height=1)
        self.divider.pack(fill="x", side="top")

        self.canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=10, pady=5)
        self.vid_item = self.canvas.create_image(0, 0, anchor=tk.CENTER)
        self.photo = None

        self.progress_frame = tk.Frame(root, bg="#d9d9d9")
        self.progress_frame.pack(fill="x", padx=20, pady=5)
        self.time_label = tk.Label(self.progress_frame, text="00:00/00:00", bg="#d9d9d9",
                                   font=("Courier New", 11, "bold"))
        self.time_label.pack(side="left", padx=(0, 15))
        self.bar_canvas = tk.Canvas(self.progress_frame, bg="white", height=14, highlightthickness=1)
        self.bar_canvas.pack(side="left", expand=True, fill="x")

        self.bar_canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.bar_canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.bar_canvas.bind("<ButtonRelease-1>", self.on_drag_end)

        self.menu_frame = tk.Frame(root, bg="#d9d9d9", bd=2, relief="groove")
        self.menu_frame.pack(fill="x", side="bottom", pady=5)
        btn_container = tk.Frame(self.menu_frame, bg="#d9d9d9")
        btn_container.pack(side="left", padx=5)
        tk.Button(btn_container, text="파일 열기", command=self.load_video, width=10).pack(side="left", padx=5, pady=5)
        self.btn_play = tk.Button(btn_container, text="▶ 재생", command=self.toggle_play, width=8)
        self.btn_play.pack(side="left", padx=2)
        self.btn_stop = tk.Button(btn_container, text="⬛ 정지", command=self.stop_video, width=8)
        self.btn_stop.pack(side="left", padx=2)

        self.btn_replay = tk.Button(btn_container, text="다시보기", command=self.replay_video, width=10, bg="#f0f0f0")
        tk.Button(btn_container, text="📏 비율 맞춤", command=self.match_ratio, width=10).pack(side="left", padx=5)

        self.filename_label = tk.Label(self.menu_frame, text="파일 대기 중...", bg="#d9d9d9", font=("맑은 고딕", 10, "bold"))
        self.filename_label.pack(side="left", expand=True)

        self.settings_popup = None
        self.settings_visible = False
        self.btn_vol_toggle = None

        self.reset_to_initial()

        if len(sys.argv) > 1:
            self.root.after(500, lambda: self.load_video(sys.argv[1]))

    def cleanup_old_caches(self):
        for f in glob.glob("replayer_audio_*.wav"):
            try:
                os.remove(f)
            except:
                pass

    def extract_audio(self, path):
        try:
            container = av.open(path)
            if not container.streams.audio: return False
            audio_stream = container.streams.audio[0]
            output = av.open(self.temp_audio_path, 'w')
            out_stream = output.add_stream('pcm_s16le', rate=audio_stream.rate)
            for frame in container.decode(audio_stream):
                for packet in out_stream.encode(frame): output.mux(packet)
            output.close();
            container.close()
            return True
        except:
            return False

    def toggle_settings(self):
        if self.settings_visible:
            if self.settings_popup: self.settings_popup.destroy()
            self.settings_visible = False
        else:
            self.settings_popup = tk.Toplevel(self.root)
            self.settings_popup.overrideredirect(True)
            x, y = self.btn_menu.winfo_rootx() - 170, self.btn_menu.winfo_rooty() + 40
            self.settings_popup.geometry(f"180x60+{x}+{y}")
            self.settings_popup.configure(bg="#f0f0f0", bd=2, relief="ridge")

            btn_text = "소리 끄기" if self.volume_on else "소리 켜기"
            self.btn_vol_toggle = tk.Button(self.settings_popup, text=btn_text,
                                            command=self.update_volume_toggle, width=15)
            self.btn_vol_toggle.pack(expand=True, pady=10)
            self.settings_visible = True

    def update_volume_toggle(self):
        self.volume_on = not self.volume_on
        new_text = "소리 끄기" if self.volume_on else "소리 켜기"
        self.btn_vol_toggle.config(text=new_text)
        if self.audio_device:
            if self.volume_on:
                curr_f = self.cap.get(cv2.CAP_PROP_POS_FRAMES) if self.cap else 0
                self.sync_audio(curr_f)
            else:
                self.audio_device.stop()

    def sync_audio(self, target_frame):
        if not self.audio_device or not self.temp_audio_path or not self.volume_on: return
        try:
            self.audio_device.stop()
        except:
            pass
        self.audio_stream = miniaudio.stream_file(self.temp_audio_path)
        try:
            sr = miniaudio.get_file_info(self.temp_audio_path).sample_rate
        except:
            sr = 44100
        skip_samples = int((target_frame / self.fps) * sr)
        for _ in range(skip_samples // 1024): next(self.audio_stream, None)
        self.audio_device.start(self.audio_stream)

    def draw_progress_bar(self, percent):
        self.bar_canvas.delete("prog")
        w = self.bar_canvas.winfo_width()
        if w > 1: self.bar_canvas.create_rectangle(0, 0, w * percent, 14, fill="#0078d7", outline="", tags="prog")

    def on_drag_start(self, event):
        if not self.cap or self.btn_replay.winfo_ismapped(): return
        self.was_playing_before_drag = self.is_playing
        if self.is_playing:
            self.toggle_play(force_pause=True)
        self.on_drag_motion(event)

    def on_drag_motion(self, event):
        if not self.cap or self.btn_replay.winfo_ismapped(): return
        percent = max(0, min(event.x / self.bar_canvas.winfo_width(), 1))
        target_f = int(self.total_frames * percent)

        self.draw_progress_bar(percent)
        if self.fps > 0:
            cs, ts = int(target_f / self.fps), int(self.total_frames / self.fps)
            self.time_label.config(text=f"{cs // 60:02}:{cs % 60:02}/{ts // 60:02}:{ts % 60:02}")

        now = time.time()
        if now - self.last_scrub_time > 0.05:
            self.last_scrub_time = now
            with self.frame_queue.mutex: self.frame_queue.queue.clear()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_f)
            self.update_frame(once=True)

    def on_drag_end(self, event):
        if not self.cap or self.btn_replay.winfo_ismapped(): return
        percent = max(0, min(event.x / self.bar_canvas.winfo_width(), 1))
        target_f = int(self.total_frames * percent)

        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_f)
        self.start_time, self.start_frame = time.time(), target_f
        self.update_frame(once=True)

        if self.was_playing_before_drag:
            self.toggle_play(force_play=True)

    def skip_time(self, seconds):
        if not self.cap or not self.is_playing or self.btn_replay.winfo_ismapped():
            return

        current_f = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        if self.seek_target is not None:
            current_f = self.seek_target

        target_f = int(current_f + (seconds * self.fps))
        target_f = max(0, min(target_f, self.total_frames - 1))

        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()
        self.btn_replay.pack_forget()

        self.seek_target = target_f

    def load_video(self, force_path=None):
        path = force_path or filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.mkv")])
        if not path: return
        self.is_playing = False
        if self.cap: self.cap.release()
        self.canvas.delete("info_msg")

        if self.idle_anim_id:
            self.root.after_cancel(self.idle_anim_id)
            self.idle_anim_id = None

        self.temp_audio_path = os.path.abspath(f"replayer_audio_{uuid.uuid4().hex[:8]}.wav")
        if self.extract_audio(path):
            try:
                self.audio_device = miniaudio.PlaybackDevice(buffersize_msec=20)
            except:
                self.audio_device = miniaudio.PlaybackDevice()
            self.audio_stream = miniaudio.stream_file(self.temp_audio_path)
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 60
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.filename_label.config(text=os.path.basename(path))
        self.canvas.config(bg="black");
        self.btn_replay.pack_forget()
        self.toggle_play(force_play=True)

    def stop_video(self):
        self.is_playing = False
        if self.cap: self.cap.release(); self.cap = None
        dev, path = self.audio_device, self.temp_audio_path
        self.audio_device, self.temp_audio_path = None, ""

        def async_clean(d, p):
            if d:
                try:
                    d.stop(); d.close()
                except:
                    pass
            time.sleep(0.5)
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

        threading.Thread(target=async_clean, args=(dev, path), daemon=True).start()
        self.reset_to_initial()

    def replay_video(self):
        if self.cap:
            if self.is_playing:
                self.seek_target = 0
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.start_time, self.start_frame = time.time(), 0
                with self.frame_queue.mutex:
                    self.frame_queue.queue.clear()
                self.btn_replay.pack_forget();
                self.toggle_play(force_play=True)

    def toggle_play(self, force_play=False, force_pause=False):
        if not self.cap: return

        if force_play:
            self.is_playing = True
        elif force_pause:
            self.is_playing = False
        else:
            self.is_playing = not self.is_playing

        self.btn_play.config(text="|| 일시정지" if self.is_playing else "▶ 재생")
        if self.is_playing:
            self.btn_replay.pack_forget()
            self.start_time, self.start_frame = time.time(), self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.sync_audio(self.start_frame)
            threading.Thread(target=self.video_worker, daemon=True).start()
            self.update_frame()
        elif self.audio_device:
            self.audio_device.stop()

    def video_worker(self):
        while self.is_playing and self.cap:
            if self.seek_target is not None:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_target)
                self.start_time, self.start_frame = time.time(), self.seek_target
                self.sync_audio(self.seek_target)
                self.seek_target = None;
                continue
            if self.frame_queue.full(): time.sleep(0.01); continue
            elapsed = time.time() - self.start_time
            target_f = self.start_frame + int(elapsed * self.fps)
            current_f = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            diff = int(target_f - current_f)
            if diff > 1:
                for _ in range(diff - 1): self.cap.grab()
            elif diff < 0:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_f)
            ret, frame = self.cap.read()
            if ret:
                cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
                if cw < 10: cw, ch = 940, 600
                ratio = min(cw / frame.shape[1], ch / frame.shape[0])
                resized = cv2.resize(frame, (int(frame.shape[1] * ratio), int(frame.shape[0] * ratio)))
                img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                self.frame_queue.put((img, target_f))
            else:
                self.frame_queue.put(None); break
            time.sleep(0.005)

    def on_video_end(self):
        self.is_playing = False
        self.btn_play.config(text="▶ 재생")
        if self.audio_device: self.audio_device.stop()
        self.draw_progress_bar(1.0)
        if self.fps > 0:
            ts = int(self.total_frames / self.fps)
            self.time_label.config(text=f"{ts // 60:02}:{ts % 60:02}/{ts // 60:02}:{ts % 60:02}")
        self.btn_replay.pack(side="left", padx=2, after=self.btn_stop)

    def update_frame(self, once=False):
        if self.cap and (self.is_playing or once):
            try:
                if once:
                    ret, frame = self.cap.read()
                    if not ret: return
                    cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
                    ratio = min(cw / frame.shape[1], ch / frame.shape[0])
                    resized = cv2.resize(frame, (int(frame.shape[1] * ratio), int(frame.shape[0] * ratio)))
                    img_data, curr_f = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB), self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                else:
                    item = self.frame_queue.get_nowait()
                    if item is None: self.on_video_end(); return
                    img_data, curr_f = item
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(img_data))
                self.canvas.itemconfig(self.vid_item, image=self.photo)
                self.canvas.coords(self.vid_item, self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2)
                self.draw_progress_bar(curr_f / self.total_frames)
                cs, ts = int(curr_f / self.fps), int(self.total_frames / self.fps)
                self.time_label.config(text=f"{cs // 60:02}:{cs % 60:02}/{ts // 60:02}:{ts % 60:02}")
            except (Empty, Exception):
                pass

            if self.is_playing and not once: self.root.after(16, self.update_frame)

    def match_ratio(self):
        if not self.cap: return
        w, h = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if w > 0: self.root.geometry(f"{940}x{int(920 * (h / w)) + 180}")

    def move_no_file_msg(self):
        if self.cap is not None:
            return

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw > 100 and ch > 100:
            nx = random.randint(80, cw - 80)
            ny = random.randint(50, ch - 50)
            self.canvas.coords("info_msg", nx, ny)

        # 1초(1000ms) 뒤에 호출하도록 수정 완료
        self.idle_anim_id = self.root.after(1000, self.move_no_file_msg)

    def reset_to_initial(self):
        self.canvas.config(bg="white")
        self.canvas.itemconfig(self.vid_item, image='')
        self.canvas.delete("info_msg")

        self.canvas.create_text(470, 300, text="(파일 없음)", fill="#333333", font=("맑은 고딕", 22, "bold"), tags="info_msg")
        self.btn_replay.pack_forget()
        self.draw_progress_bar(0)

        if hasattr(self, 'idle_anim_id') and self.idle_anim_id:
            self.root.after_cancel(self.idle_anim_id)

        # 1초(1000ms) 간격으로 타이머 시작
        self.idle_anim_id = self.root.after(1000, self.move_no_file_msg)


if __name__ == "__main__":
    root = tk.Tk()
    player = Replayer(root)
    root.mainloop()