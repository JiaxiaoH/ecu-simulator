import os, sys, time
import tkinter as tk

def pushed(btn_name):
 print(f"{btn_name}clicked")

class ButtonPush:
    @classmethod 
    def battery(cls, name):
        print(f"{name}battery")
    @classmethod 
    def send(cls, name):
       print(f"{name}send")

# メインウィンドウ作成
root = tk.Tk()
# メインウィンドウのタイトルを変更
root.title("Tkinter test")
# メインウィンドウを640x480にする
root.geometry("640x480")

# ラベルを追加
#label = tk.Label(root, text="Hello,World")
# 表示
#label.place(relx=0.5, y=10, anchor="center")
a="aa"
battery_button = tk.Button(root, text="ON/OFF", command=lambda: ButtonPush.battery("ON/OFF"))
battery_button.place(relx=0.1, rely=0.1, anchor='w')  # 左侧，垂直居中

entry = tk.Entry(root, width=50)
entry.place(relx=0.5, rely=0.1, anchor='center')     # 中间，垂直居中

send_button = tk.Button(root, text="Send", command=lambda: ButtonPush.send("Send"))
#battery_button.config(command=lambda: pushed(battery_button["text"]))
send_button.place(relx=0.9, rely=0.1, anchor='e')          # 右侧，垂直居中

# 表格区域
table_frame = tk.Frame(root)
table_frame.place(relx=0.1, rely=0.3, relwidth= 0.8, anchor='n')  # 放在下方

canvas = tk.Canvas(table_frame, width=400, height=150)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

v_scroll = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=canvas.yview)
v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
h_scroll = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
h_scroll.place(relx=0.1, rely=0.65, relwidth=1, anchor='n')

canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

table_inner = tk.Frame(canvas)
canvas.create_window((0, 0), window=table_inner, anchor='nw')

# 填充表格内容
for i in range(6):
    for j in range(6):
        lbl = tk.Label(table_inner, width=9, height=2, text=f"R{i+1}C{j+1}", borderwidth=0, highlightthickness=0)
        lbl.grid(row=i, column=j, sticky='nsew')

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))

table_inner.bind('<Configure>', on_configure)
canvas.configure(xscrollcommand=h_scroll.set)
h_scroll.config(command=canvas.xview)

# rootを表示し無限ループ
root.mainloop()

