import tkinter as tk
def click():
    print("클릭했습니다")

def click2():
    button.comfig(text="성공입니다")

window=tk.Tk()
window.title("rickrill")
window.geometry("500x500+500+150")
window.resizable(False,False)
label=tk.Label(window, text="테스트",width=10,height=5)
label.pack()
button=tk.Button(window, text="버튼",width=10,height=3,command=click)
button.pack()
entry=tk.Entry()
entry.pack()

window.mainloop()
