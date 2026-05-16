import tkinter as tk
from time import strftime


def update_time():
    time=strftime("%H:%M:%S")
    label.config(text=time)
    label.after(1000,update_time)

root = tk.Tk()
root.title("디지털 시계")

label=tk.Label(root,font=("Helvetica",48),bg="white",fg="black")
label.pack()

update_time()
root.mainloop()
