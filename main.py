from energy import Energy
from ecu import ECU
import threading
import tkinter as tk
from tkinter import ttk
import can
from gui import CanGuiApp
# class BusBridge(can.Listener):
#     def __init__(self, bus_to):
#         self.bus_to = bus_to

#     def on_message_received(self, msg):
#         print(f"[Bridge] Received message on source bus: {msg}")
#         try:
#             self.bus_to.send(msg)
#             print(f"[Bridge] Forwarded message to destination bus")
#         except can.CanError as e:
#             print(f"[Bridge] Failed to forward message: {e}")
def main():
    #stop_event = threading.Event()
    bus = can.interface.Bus(bustype='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    # GUI 使用的总线
    #bus_gui = can.interface.Bus(channel='vcan0', interface='virtual', bitrate=500000)
    # ECU 使用的总线
    #bus_ecu = can.interface.Bus(channel='vcan1', interface='virtual', bitrate=500000)
    energy = Energy()
    ecu = ECU(energy=energy, bus=bus)
    #ecu = ECU(energy=energy, bus=bus_ecu)
    app = CanGuiApp(bus=bus, ecu_interface=ecu, energy_interface=energy)
    #app = CanGuiApp(bus=bus_gui, ecu_interface=ecu, energy_interface=energy)
    notifier = can.Notifier(bus, [ecu, app])
    # bridge_ecu = BusBridge(bus_to=bus_ecu)
    # notifier_gui = can.Notifier(bus_gui, [bridge_ecu])  # 
    # bridge_gui = BusBridge(bus_to=bus_gui)
    # notifier_ecu = can.Notifier(bus_ecu, [bridge_gui])  # 
    ecu_thread = threading.Thread(target=ecu.run)
    ecu_thread.start()
    app.run()
    notifier.stop()
    # stop_event.set()
    # notifier_ecu.stop()
    # notifier_gui.stop()

if __name__ == "__main__":
    main()