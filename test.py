# import tkinter as tk
# from tkinter import ttk

# # 创建主窗口
# app = tk.Tk()
# app.geometry("200x100")

# # 添加标签
# label = tk.Label(app, text="请选择一个月份：")
# label.grid(column=0, row=0)

# # 创建下拉选择框
# combo = ttk.Combobox(app, values=["一月", "二月", "三月", "四月"], state="readonly")
# combo.grid(column=0, row=1)
# combo.current(0) # 设置默认选项为第一个

# # 绑定事件
# def on_select(event):
#     print(f"选择了: {combo.get()}")

# combo.bind("<<ComboboxSelected>>", on_select)

# app.mainloop()
    

# 导入tkinter库
from tkinter import *
from tkinter import ttk
import tkinter as tk
# 创建tkinter框架或窗口的实例
win= Tk()
# 设置tkinter框架的几何形状
win.geometry("750x250")
# 定义打开窗口的新函数
def open_win():
    new= Toplevel(win)
    new.geometry("750x250")
    new.title("新的窗口")
    # 在新窗口中创建一个标签
    #Label(new, text="嗨，你好吗？", font=('Helvetica 17 bold')).pack(pady=30)
    # 添加标签
    label = tk.Label(new, text="请选择一个月份：")
    label.grid(column=0, row=0)

    # 创建下拉选择框
    combo = ttk.Combobox(new, values=["一月", "二月", "三月", "四月"], state="readonly")
    combo.grid(column=0, row=1)
    combo.current(0) # 设置默认选项为第一个

    # 绑定事件
    def on_select(event):
        print(f"选择了: {combo.get()}")

    combo.bind("<<ComboboxSelected>>", on_select)
# 创建一个标签
Label(win, text= "单击下面的按钮来打开新窗口", font= ('Helvetica 17 bold')).pack(pady=30)
# 创建一个按钮以打开新窗口
ttk.Button(win, text="打开", command=open_win).pack()
win.mainloop()
