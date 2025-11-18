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
from keys import ALGORITHMINDICATOR
from ecdsa import gen_ecdhe_keypair, gen_ssk, aes128_encrypt, bytes2Ecckey
from PIL import Image, ImageTk 
class ButtonPush:
    @classmethod
    def battery(cls, name, ecu, energy, button, led_canvas, led_item):
        if energy.status == 'POWER_ON':
            energy.status='POWER_OFF'
            button.config(text='OFF', bg='red', fg='white')
            led_canvas.itemconfig(led_item, fill='grey')
        else:
            energy.status='POWER_ON'
            button.config(text='ON', bg='green', fg='white')
            led_canvas.itemconfig(led_item, fill='lime')
        ecu.on_power_status_changed(energy.status)
    @classmethod
    def drive(cls, name, ecu, button, icon_anim_callback):
        if ecu.moving == False:
            ecu.moving=True
            button.config(text='Move', bg="green", fg="white")
            icon_anim_callback()
        else:
            ecu.moving=False
            button.config(text='Stop', bg="red", fg="white")
    @classmethod 
    def send(cls, name, bus, ecu, entry=None, send_callback=None):
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
            feedback = tk.Label(new, text="DTC Added!", fg="green")
            feedback.grid(column=4, row=2)
            feedback.after(500, feedback.destroy)
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
        self.keyID=(0xFF, 0xFF) #DID0xD110、tester
        self.kx_sk1=None #RID0xD111、tester
        self.kx_pk2=None #RID0xD111、tester
        self.ssk=None#tester
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

        self.power_frame = tk.Frame(self.root)
        self.power_frame.place(relx=0.05, rely=0.05)
        self.power_button = tk.Button(
            self.power_frame, 
            text="OFF",
            width=8,
            bg="red",
            fg="white",
            command=lambda: ButtonPush.battery(
                "POWER",
                self.ecu,
                self.energy,
                self.power_button,
                self.power_led,
                self.power_led_circle
            )
        )
        self.power_button.grid(row=0, column=0, padx=5)

        self.drive_frames = self.load_gif_frames("picture/wheel.gif", size=(40, 40)) 
        self.drive_frame_index = 0
        self.drive_frame = tk.Frame(self.root)
        self.drive_frame.place(relx=0.05, rely=0.90, anchor='w')
        self.drive_icon = tk.Label(self.drive_frame, image=self.drive_frames[0])
        self.drive_icon.grid(row=0, column=1, padx=5)

        self.drive_button = tk.Button(
            self.drive_frame,
            text="STOP",
            bg="red",
            fg="white",
            width=8,
            command=lambda: ButtonPush.drive(
                "DRIVE",
                self.ecu,
                self.drive_button,
                self.animate_drive_icon  
            )
        )
        self.drive_button.grid(row=0, column=0, padx=5)

        self.dtc_button = tk.Button(self.root, text="DTC", command=lambda: ButtonPush.dtc("DTC", self.ecu, self.root))
        self.dtc_button.place(relx=0.5, rely=0.9, anchor='e')

        self.power_led = tk.Canvas(self.power_frame, width=20, height=20, highlightthickness=0)
        self.power_led_circle = self.power_led.create_oval(2, 2, 18, 18, fill="grey")
        self.power_led.grid(row=0, column=1, padx=5)

    def run(self):
        self.root.mainloop()

    def disp_msg(self, wmsg):
        formatted = wmsg
        if formatted:
            self.msg_queue.put(formatted)
    
    def process_queue(self):
        while not self.msg_queue.empty():
            wrapped_msg = self.msg_queue.get()
            self.tree.insert("", "end", values=[datetime.datetime.fromtimestamp(wrapped_msg.timestamp), wrapped_msg.direction, wrapped_msg.data_str, wrapped_msg.session_name, wrapped_msg.security_name])
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
                if list(msg.data[0:6]) ==[0x71, 0x01, 0xD1, 0x11, 0x00, 0x00]:
                    raw_pk=(msg.data[6:])
                    self.kx_pk2 = bytes2Ecckey(raw_pk)
                    self.ssk=gen_ssk(self.kx_sk1, self.kx_pk2)
                if list(msg.data[0:3])==[0x69, 0x05, 0x00]:
                    challengeServer=msg.data[21:37]
                    self.authenticator=aes128_encrypt(challengeServer, self.ssk)
                    self.ssk=None
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
        if hasattr(self, "dropdown_listbox"):
            self.dropdown_listbox.destroy()
        self.dropdown_listbox = tk.Listbox(self.root, height=3)
        self.dropdown_display_map = []
        for opt in options:
            if not opt or opt==[]:
                continue
            else:
                if len(opt) < 16:
                    line = " ".join(f"{b:02X}" for b in opt)
                else:
                    line = " ".join(f"{b:02X}" for b in opt[:16]) + " ..."
            self.dropdown_listbox.insert(tk.END, line)
            self.dropdown_display_map.append(opt)
        x = self.entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.entry.winfo_rooty() - self.root.winfo_rooty() + self.entry.winfo_height()
        self.dropdown_listbox.place(x=x, y=y, width=self.entry.winfo_width())
        self.dropdown_listbox.bind("<<ListboxSelect>>", self.on_option_selected)
        self.root.bind("<Button-1>", self.hide_dropdown_outside)
        self.dropdown_full_options=options

    def on_option_selected(self, event):
        widget = event.widget
        if not widget.curselection():
            return
        index=widget.curselection()[0]
        opt = self.dropdown_display_map[index]
        #full_msg=self.dropdown_full_options[index]
        self.hexline=" ".join(f"{b:02X}" for b in opt)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.hexline)
        self.dropdown_listbox.destroy()
        self.root.unbind("<Button-1>")

    def hide_dropdown_outside(self, event):
        widget = event.widget
        if widget is not self.dropdown_listbox:
            self.dropdown_listbox.destroy()
            self.root.unbind("<Button-1>")

    def get_options(self) ->list:
        return [self.generate_rid0xd111_request(), self.generate_sid0x29_0x06_request(), self.generate_sid0x29_0x05_request()]
    
    def generate_rid0xd111_request(self) ->list[int]:
        self.kx_sk1, kx_pk1=gen_ecdhe_keypair()
        secret_key=find_secret_key(self.keyID)
        signature=gen_signature(secret_key, kx_pk1)
        rid_0x111_req=gen_rid0x111_req(kx_pk1,signature)
        return rid_0x111_req

    def generate_sid0x29_0x06_request(self) ->list[int]:
        if not hasattr(self, "authenticator") or self.authenticator is None:
            return []
        return [0x29, 0x06] + ALGORITHMINDICATOR + [0x00, 0x10] + self.authenticator + [0x00] * 4
    
    def generate_sid0x29_0x05_request(self) ->list[int]:
        return [0x29, 0x05, 0x00] + ALGORITHMINDICATOR
    
    # ========= gif animate =========
    def load_gif_frames(self, path, size=(20, 20)):
        img = Image.open(path)
        frames = []
        try:
            while True:
                frame = img.copy().resize(size, Image.LANCZOS)
                frame = ImageTk.PhotoImage(frame)
                frames.append(frame)
                img.seek(len(frames))
        except EOFError:
            pass
        return frames

    def animate_drive_icon(self):
        if not self.ecu.moving:
            return  
        self.drive_frame_index = (self.drive_frame_index + 1) % len(self.drive_frames)
        self.drive_icon.config(image=self.drive_frames[self.drive_frame_index])
        self.root.after(80, self.animate_drive_icon)