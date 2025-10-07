import time
from energy import Energy
from power_input import PowerInput
from ecu import ECU
from tester import Tester
from CANmessage import Queue
import threading
def main():
    energy = Energy()
    power_input = PowerInput(energy=energy)
    request_queue = Queue()
    response_queue = Queue()
    ecu = ECU(energy=energy, request_queue=request_queue, response_queue=response_queue)
    tester = Tester(request_queue=request_queue, response_queue=response_queue)
    power_input.register_callback(ecu.on_power_status_changed)
    # 在单独线程运行ECU主循环，避免阻塞
    ecu_thread = threading.Thread(target=ecu.run)
    ecu_thread.start()
    #启动电源模拟
    power_input.start()
    #运行3秒后启动tester模拟
    time.sleep(3)
    tester.start()
    #运行5秒后尝试重置计时
    time.sleep(5)
    print("Main thread: Clearing ECU timer now...")
    ecu.clear_clock()
    #tester结束
    time.sleep(12)
    tester.stop()
    print("Tester test finished.")
    #等待电源线程结束
    power_input.join()
    print("Battery test finished.")
    power_input.stop()
    # 等待ECU线程结束
    ecu.stop()
    ecu_thread.join()

    print("ECU test finished.")

if __name__ == "__main__":
    main()