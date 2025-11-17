#gui.py
import can
import tkinter as tk
from tkinter import *
from tkinter import ttk
import datetime
import queue
from wrapped_message import WrappedMessage
from dtc import DTCManager, DTC
from tester_create_key import find_secret_key, gen_signature, gen_rid0x111_req
from ecdsa import gen_ecdhe_keypair
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
    @classmethod
    def dtc(cls, name, ecu, root):
        new=Toplevel(root)
        new.geometry("350x200")
        new.title("Create DTC")
        label1 = tk.Label(new, text="Choose a DTC")
        label1.grid(column=0, row=0)
        combo1 = ttk.Combobox(new, values=ecu.dtcstr, state="readonly")
        combo1.grid(column=0, row=1)
        combo1.current(0)

        label2 = tk.Label(new, text="Choose a status")
        label2.grid(column=2, row=0)
        combo2 = ttk.Combobox(new, values=["04", "08", "0C"], state="readonly")
        combo2.grid(column=2, row=1)
        combo2.current(0)

        def send_message():
            dtc=DTC.from_dtc_string(combo1.get(), int(combo2.get(), 16))
            ecu.dtc=ecu.dtc+dtc
        send_button = tk.Button(new, text="Send", command=send_message)
        send_button.grid(column=4, row=1)

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
        self.keyID=(0xFF, 0xFF) #D110
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
        self.entry.bind("<Double-Button-1>", self.show_dropdown)

        self.send_button = tk.Button(self.root, text="Send", command=lambda: ButtonPush.send("Send", self.bus, self.ecu, self.entry, send_callback=self.send_message))
        self.send_button.place(relx=0.9, rely=0.1, anchor='e')

        self.power_button = tk.Button(self.root, text="POWER", command=lambda: ButtonPush.battery("POWER", self.ecu, self.energy, self.power_button))
        self.power_button.place(relx=0.1, rely=0.1, anchor='w')

        self.drive_button = tk.Button(self.root, text="DRIVE", command=lambda: ButtonPush.drive("DRIVE", self.ecu, self.drive_button))
        self.drive_button.place(relx=0.1, rely=0.9, anchor='w')

        self.dtc_button = tk.Button(self.root, text="DTC", command=lambda: ButtonPush.dtc("DTC", self.ecu, self.root))
        self.dtc_button.place(relx=0.5, rely=0.9, anchor='e')

    def run(self):
        self.root.mainloop()

    def disp_msg(self, wmsg):
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
            if msg.arbitration_id==0x7E0:
                wrapped.is_rx = False
            else:
                wrapped.is_rx = True
                if list(msg.data[0:3]) ==[0x62, 0xD1, 0x10]:
                    self.keyID=(msg.data[4], msg.data[5])
            self.disp_msg(wrapped)
    
    def send_message(self, data, arbitration_id=0x7E0):
        msg = can.Message(datetime.datetime.now().timestamp(), arbitration_id=arbitration_id, data=data, is_extended_id=False, is_rx=False)
        msg.is_rx=False
        try:
            self.bus.send(msg)
        except can.CanError:
            print("Message NOT sent")

    def stop(self):
        self.running = False

    def on_close(self):
        try:
            if self.ecu is not None:
                self.ecu.stop()                
                #self.ecu.ecu_thread.join(timeout=1)
            print("ECU test finished.")
        except Exception as e:
            print("Error stopping ECU:", e)
        self.stop()
        self.root.destroy()

    def show_dropdown(self, event):
        options = self.get_options()
        self.hex_line=" ".join(f"{b:02X}" for b in options)
        if len(options)<16:
            hex_line_disp = self.hex_line
        else:
            hex_line_disp = " ".join(f"{b:02X}" for b in options[0:16])+" ..."
        if hasattr(self, "dropdown_listbox"):
            self.dropdown_listbox.destroy()
        self.dropdown_listbox = tk.Listbox(self.root, height=3)
        self.dropdown_listbox.insert(tk.END, hex_line_disp)
        x = self.entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.entry.winfo_rooty() - self.root.winfo_rooty() + self.entry.winfo_height()
        self.dropdown_listbox.place(x=x, y=y, width=self.entry.winfo_width())
        self.dropdown_listbox.bind("<<ListboxSelect>>", self.on_option_selected)
        self.root.bind("<Button-1>", self.hide_dropdown_outside)

    def on_option_selected(self, event):
        widget = event.widget
        if not widget.curselection():
            return

        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.hex_line)

        self.dropdown_listbox.destroy()
        self.root.unbind("<Button-1>")

    def hide_dropdown_outside(self, event):
        widget = event.widget
        if widget is not self.dropdown_listbox:
            self.dropdown_listbox.destroy()
            self.root.unbind("<Button-1>")

    def get_options(self):
        kx_sk1, kx_pk1=gen_ecdhe_keypair()
        secret_key=find_secret_key(self.keyID)
        signature=gen_signature(secret_key, kx_pk1)
        rid_0x111_req=gen_rid0x111_req(kx_pk1,signature)
        return rid_0x111_req
