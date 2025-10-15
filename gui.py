#gui.py
import can
import threading
import tkinter as tk
from tkinter import ttk
import datetime
import queue
from wrapped_message import WrappedMessage
from can import Notifier
class ButtonPush:
    #temp method for reporting. will be deleted when creating SID$27
    @classmethod
    def security(cls, name, ecu):
        if ecu.security==False:
            ecu.security=True
        elif ecu.security==True:
            ecu.security=False
        else:
            ecu.security=False
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
    def drive(cls, name, ecu, button):
        if ecu.moving == False:
            ecu.moving=True
            button.config(text='Move')
        else:
            ecu.moving=False
            button.config(text='Stop')
    @classmethod 
    def send(cls, name, bus, ecu, entry=None, send_callback=None):
        #print(f"ECU.session = {ecu.session}")
        if entry is not None and entry.get().strip() != "":
            try:
                can_entry= [int(x, 16) for x in entry.get().split()]
            except ValueError:
                entry.delete(0, 'end')
                entry.insert(0, '[Error] please input hexadecimal numbers')
                return
            if send_callback:
                send_callback(data=can_entry)
            entry.delete(0, 'end')

class CanGuiApp(can.Listener):
    def __init__(self, bus, ecu_interface, energy_interface):
        self.bus = bus
        self.ecu = ecu_interface 
        self.energy = energy_interface
        self.root = tk.Tk()
        self.root.title("CAN DIAG")
        self.root.geometry("640x480")
        self.msg_queue=queue.Queue()
        self.running=True
        self.setup_table()
        self.setup_controls()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(1, self.process_queue)

        print(f"bus.channel_info = {self.bus.channel_info}")

    def setup_table(self):
        cols = [f"C{i+1}" for i in range(6)]
        self.tframe = tk.Frame(self.root)
        self.tframe.place(relx=0.1, rely=0.18, relwidth=0.8, relheight=0.7, anchor='nw')

        self.tree = ttk.Treeview(self.tframe, columns=cols, show='headings', height=6)
        tree_head = ['Time', 'Dir', 'Msg', 'Session', 'Security', '...']
        for i, c in enumerate(cols):
            self.tree.heading(c, text=tree_head[i])
            self.tree.column(c, width=80, anchor='center')
        v_scroll = ttk.Scrollbar(self.tframe, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(self.tframe, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.tframe.grid_rowconfigure(0, weight=1)
        self.tframe.grid_columnconfigure(0, weight=1)

    def setup_controls(self):
        self.entry = tk.Entry(self.root, width=50)
        self.entry.place(relx=0.5, rely=0.1, anchor='center')
        self.entry.bind("<Return>", lambda event: ButtonPush.send("Send", self.bus, self.ecu, self.entry, send_callback=self.send_message))

        self.send_button = tk.Button(self.root, text="Send", command=lambda: ButtonPush.send("Send", self.bus, self.ecu, self.entry, send_callback=self.send_message))
        self.send_button.place(relx=0.9, rely=0.1, anchor='e')

        self.power_button = tk.Button(self.root, text="POWER", command=lambda: ButtonPush.battery("POWER", self.ecu, self.energy, self.power_button))
        self.power_button.place(relx=0.1, rely=0.1, anchor='w')
        
        self.security_button = tk.Button(self.root, text="Security", command=lambda: ButtonPush.security("Security", self.ecu))
        self.security_button.place(relx=0.9, rely=0.9, anchor='e')

        self.drive_button = tk.Button(self.root, text="DRIVE", command=lambda: ButtonPush.drive("DRIVE", self.ecu, self.drive_button))
        self.drive_button.place(relx=0.1, rely=0.9, anchor='w')

    def run(self):
        self.root.mainloop()

    def disp_msg(self, wmsg):
        #formatted = trans_msg(wmsg)
        formatted = wmsg
        if formatted:
            self.msg_queue.put(formatted)
    
    def process_queue(self):
        while not self.msg_queue.empty():
            wrapped_msg = self.msg_queue.get()
            self.tree.insert("", "end", values=[datetime.datetime.fromtimestamp(wrapped_msg.timestamp), wrapped_msg.direction, wrapped_msg.data_str, wrapped_msg.session, wrapped_msg.security])
            self.tree.see(self.tree.get_children()[-1])
        self.root.after(100, self.process_queue)  

    def on_message_received(self, msg):
        if msg is not None:
            wrapped = WrappedMessage.wrap_from_msg(
                msg,
                session=self.ecu.session,
                security=self.ecu.security
            )
            if msg.arbitration_id==0x001:
                wrapped.is_rx = False
            else:
                wrapped.is_rx = True
            self.disp_msg(wrapped)
    
    def send_message(self, data, arbitration_id=0x001):
        msg = can.Message(datetime.datetime.now().timestamp(), arbitration_id=arbitration_id, data=data, is_extended_id=False, is_rx=False)
        msg.is_rx=False
        try:
            self.bus.send(msg)
        except can.CanError:
            print("Message NOT sent")

    def stop(self):
        self.running = False
        #self.recv_thread.join(timeout=1)

    def on_close(self):
        try:
            if self.ecu is not None:
                self.ecu.stop()                # 通知 ECU 退出
                self.ecu.ecu_thread.join(timeout=1)
            print("ECU test finished.")
        except Exception as e:
            print("Error stopping ECU:", e)
        self.stop()
        self.root.destroy()
