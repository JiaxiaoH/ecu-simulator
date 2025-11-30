from energy import Energy
from ecu import ECU
from tester import Tester
import can
from gui import CanGuiApp
def main():
    bus = can.interface.Bus(bustype='virtual', channel='vcan0', bitrate=500000, receive_own_messages=True)
    energy = Energy()
    ecu = ECU(energy=energy, bus=bus)
    tester = Tester(bus=bus)
    app = CanGuiApp(bus=bus, ecu=ecu, energy=energy, tester=tester)
    notifier = can.Notifier(bus, [ecu, tester, app])
    app.run()
    notifier.stop()
if __name__ == "__main__":
    main()