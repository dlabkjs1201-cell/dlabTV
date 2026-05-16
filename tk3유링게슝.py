import tkinter
import tkinter.font
import random

ln=range(1,46)

def buttonClick():
    for i in range(5):
        lottoPick=map(str,random.sample(ln,6))
        lottoPick=','.join(lottoPick)
        lottoPick=str(i+1)+'회: ' + lottoPick
        print(lottoPick)
        listbox.insert(i,lottoPick)
    listbox.pack()

window=tkinter.Tk()
window.title("로또로 돈을 벌어서 억만장자가 될거야!")
window.geometry("400x200+800+300")
window.resizable(False,False)

button = tkinter.Button(window, overrelief="solid", text="지옥의 로또 결과 확인하기",
                        width=25, command=buttonClick, repeatdelay=1000,
                        repeatinterval=100)
button.pack()


font=tkinter.font.Font(size=20)
listbox=tkinter.Listbox(window, selectmode="extended",
                        height=5,font=font)
listbox.insert(0,"1회:")
listbox.insert(0,"2회:")
listbox.insert(0,"3회:")
listbox.insert(0,"4회:")
listbox.insert(0,"5회:")
listbox.pack()

window.mainloop()