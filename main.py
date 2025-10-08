import os, sys, time
from energy import Energy
from ecu import ECU
from CANmessage import Queue
import threading
import tkinter as tk
from tkinter import ttk
import sessiontypes
from CANmessage import RequestMessage, ResponseMessage
class ButtonPush:
    @classmethod
    def battery(cls, name, ecu, energy, button):
        if energy.status == 'POWER_ON':
            energy.status='POWER_OFF'
            button.config(text='POWER_OFF')
        else:
            energy.status='POWER_ON'
            button.config(text='POWER_ON')
        ecu.on_power_status_changed(energy.status)
    @classmethod 
    def send(cls, name, request_queue, entry=None, tree=None):
        if entry is not None and entry.get().strip() != "":
            can_entry= [int(x, 16) for x in entry.get().split()]
            while len(can_entry) < 4:
                can_entry.append(0)
            req = RequestMessage(SID=can_entry[0], subfunction = can_entry[1], dataID=can_entry[2], data=can_entry[3])  # 诊断会话请求
            print(f"[Tester] Sending request to ECU, SID=0x{req.SID:02X}, subfunction=0x{req.subfunction:02X}, subfunction=0x{req.dataID:02X}, data=0x{req.data:02X}")
            request_queue.put(req)
            if tree is not None:
                req.log_to_treeview(tree)
            entry.delete(0, 'end')
def main():
    #准备GUI
    root = tk.Tk()
    root.title("CAN DIAG")
    root.geometry("640x480")
    # --- 6x6 tableview with scrollbars ---
    cols = [f"C{i+1}" for i in range(6)]
    tframe = tk.Frame(root)
    tframe.place(relx=0.1, rely=0.18, relwidth=0.8, relheight=0.7, anchor='nw')
    tree = ttk.Treeview(tframe, columns=cols, show='headings', height=6)       
    
    tree_head=['Time', 'Dir', 'Msg', '...', '...', '...' ]
    for i, c in enumerate(cols):
        tree.heading(c, text=tree_head[i])
        tree.column(c, width=80, anchor='center')
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
    # end table

    energy = Energy()
    request_queue = Queue()
    response_queue = Queue()
    ecu = ECU(energy=energy, request_queue=request_queue, response_queue=response_queue, tree=tree)
    
    battery_button = tk.Button(root, text="ON/OFF", command=lambda: ButtonPush.battery("POWER", ecu, energy, battery_button))
    battery_button.place(relx=0.1, rely=0.1, anchor='w')  

    entry = tk.Entry(root, width=50)
    entry.place(relx=0.5, rely=0.1, anchor='center')   

    send_button = tk.Button(root, text="Send", command=lambda: ButtonPush.send("Send",  request_queue, entry, tree))
    send_button.place(relx=0.9, rely=0.1, anchor='e')

    ecu_thread = threading.Thread(target=ecu.run)
    ecu_thread.start()

    def on_close():
        try:
            ecu.stop()                # 通知 ECU 退出
            ecu_thread.join(timeout=1)
            print("ECU test finished.")
        except Exception as e:
            print("Error stopping ECU:", e)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    # start the GUI event loop immediately so the window appears and is
    # responsive while the simulation runs in the background
    root.mainloop()
if __name__ == "__main__":
    main()