import os, sys, time
from energy import Energy
from ecu import ECU
from CANmessage import Queue
import threading
import tkinter as tk
from tkinter import ttk

class ButtonPush:
    @classmethod
    def battery(cls, name, ecu, energy):
        if energy.status == 'POWER_ON':
            energy.status='POWER_OFF'
        else:
            energy.status='POWER_ON'
        ecu.on_power_status_changed(energy.status)
    @classmethod 
    def send(cls, name, entry=None):
       # If an Entry widget is provided, print its current text; otherwise print the name
       try:
           if entry is not None:
               print(entry.get())
           else:
               print(f"{name}send")
       except Exception as e:
           print("Error reading entry:", e)


def main():
    energy = Energy()
    request_queue = Queue()
    response_queue = Queue()
    ecu = ECU(energy=energy, request_queue=request_queue, response_queue=response_queue)
    
    #power_input.register_callback(ecu.on_power_status_changed)

    #准备GUI
    root = tk.Tk()
    root.title("CAN DIAG")
    root.geometry("640x480")
    battery_button = tk.Button(root, text="ON/OFF", command=lambda: ButtonPush.battery("ON/OFF", ecu, energy))
    battery_button.place(relx=0.1, rely=0.1, anchor='w') 
    entry = tk.Entry(root, width=50)
    entry.place(relx=0.5, rely=0.1, anchor='center') 
    send_button = tk.Button(root, text="Send", command=lambda: ButtonPush.send("Send", entry))
    send_button.place(relx=0.9, rely=0.1, anchor='e')          
    tframe = tk.Frame(root)
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