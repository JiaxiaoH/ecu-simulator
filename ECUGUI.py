import os, sys, time
import tkinter as tk
from tkinter import ttk
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
tframe = tk.Frame(root)
# place the table frame under the top controls and align left/right with the two buttons
# buttons are at relx=0.1 (left) and relx=0.9 (right), so start at relx=0.1 and width 0.8
# use anchor='nw' so the left edge aligns with the left button position
tframe.place(relx=0.1, rely=0.18, relwidth=0.8, relheight=0.7, anchor='nw')

# --- 6x6 tableview with scrollbars ---
cols = [f"C{i+1}" for i in range(6)]
tree = ttk.Treeview(tframe, columns=cols, show='headings', height=6)
for i, c in enumerate(cols):
    tree.heading(c, text=f"Col {i+1}")
    tree.column(c, width=90, anchor='center')

# vertical and horizontal scrollbars
v_scroll = ttk.Scrollbar(tframe, orient=tk.VERTICAL, command=tree.yview)
h_scroll = ttk.Scrollbar(tframe, orient=tk.HORIZONTAL, command=tree.xview)
tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

# layout - tree in grid so scrollbars can align
tree.grid(row=0, column=0, sticky='nsew')
v_scroll.grid(row=0, column=1, sticky='ns')
h_scroll.grid(row=1, column=0, columnspan=2, sticky='ew')

# allow expansion
tframe.grid_rowconfigure(0, weight=1)
tframe.grid_columnconfigure(0, weight=1)

# populate 6x6 sample data
for r in range(6):
    values = [f"R{r+1}C{c+1}" for c in range(6)]
    tree.insert('', 'end', values=values)

# end table

# rootを表示し無限ループ
root.mainloop()

