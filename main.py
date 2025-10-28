from energy import Energy
from ecu import ECU
import can
from gui import CanGuiApp
def main():
    bus = can.interface.Bus(bustype='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    energy = Energy()
    ecu = ECU(energy=energy, bus=bus)
    app = CanGuiApp(bus=bus, ecu_interface=ecu, energy_interface=energy)
    notifier = can.Notifier(bus, [ecu, app])
    app.run()
    notifier.stop()

if __name__ == "__main__":
    main()