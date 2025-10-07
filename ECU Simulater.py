import threading
import time
from abc import ABC, abstractmethod
from typing import Union
FREQUENCY_HZ=60
VOLTAGE_THRESHOLD = 1.0
class Security:
    def __init__(self, type4=False, type5=False, type10=False):
        self.Type4 = type4
        self.Type5 = type5
        self.Type10 = type10

class RequestMessage:
    def __init__(self, SID=0x00, subfunction=0x00, dataID=0x00, data=0x00):
        self.SID = SID
        self.subfunction = subfunction
        self.dataID = dataID
        self.data = data

class ResponseMessage(ABC):
    @abstractmethod
    def is_positive(self) -> bool:
        pass

class PositiveResponseMessage(ResponseMessage):
    def __init__(self, SID=0x00, subfunction=0x00, dataID=0x00, data=0x00):
        self.SID = SID
        self.subfunction = subfunction
        self.dataID = dataID
        self.data = data
    def is_positive(self) -> bool:
        return True

class NegativeResponseMessage(ResponseMessage):
    def __init__(self, SID: 0x7F, SIDRQ: 0x00, NRC: 0x00):
        super().__init__()  
        self.SID = SID
        self.SIDRQ = SIDRQ
        self.NRC = NRC
    def is_positive(self) -> bool:
        return False
    
class Energy:
    def __init__(self,Voltage=0.0):
        self.Voltage=Voltage
        self.status=None

class PowerInput(threading.Thread):
    def __init__(self, energy: Energy, interval=0.5): 
        super().__init__()
        self.Voltage=0.0
        self.energy = energy
        self.interval = interval
        self._running = False
    def run(self):
        self._running = True
        voltages = [0.0, 3.3, 3.3, 0.0, 3.3, 3.3, 0.0]  # 模拟电压序列
        intervals = [2, 5, 5, 3, 5, 2, 3]  # 每个电压维持时间（秒）
        idx = 0
        while self._running and idx < len(voltages):
            v = voltages[idx]
            self.energy.Voltage = v
            if v >= VOLTAGE_THRESHOLD:
                self.energy.status = "POWER_ON"
            else:
                self.energy.status = "POWER_OFF"
            time.sleep(intervals[idx])
            idx += 1
        print("[PowerInput] simulation is over")
    def start(self):
        if not self.is_alive():
            super().start()
    def stop(self):
        self.running=False

class ECU:
    def __init__(self, energy: Energy ,frequency_hz=FREQUENCY_HZ):
        self.energy=energy
        self.DiagnosticSession = 0x01
        self.Security = Security()
        self.timer=0.0
        self.frequency = frequency_hz
        self.period = 1.0 / frequency_hz
        self.running = False
        self.stop_event = threading.Event()
        self.start_event = threading.Event()

    def run(self):
        print("ECU is ready, waiting for start signal...")
        last_status = None
        while not self.stop_event.is_set():
            current_status = self.energy.status

            if current_status != last_status:
                if current_status == "POWER_ON":
                    print("[ECU] POWER_ON, ECU Start")
                    self.start_event.set()
                    self.running = True
                elif current_status == "POWER_OFF":
                    print("[ECU] POWER_OFF, ECU Stop")
                    self.start_event.clear()
                    self.running = False
                last_status = current_status       

        #self.start_event.wait()  # 等待start信号
        #print("Start signal received. ECU started.")
        #self.running = True

            if self.running:
                start_time = time.time()

                # 这里放置ECU的循环处理逻辑
                self.loop_task()
                elapsed = time.time() - start_time
                sleep_time = self.period - elapsed
                if sleep_time > 0:#如果有剩余的时间，没有剩余的时间的话再说吧
                    time.sleep(sleep_time)
        #print("Stop signal received. ECU stopped.")
        #self.running = False

    def loop_task(self):
        # 模拟ECU每个周期要做的任务
        self.timer += 1
        print(f"[{self.timer}] ECU loop running at {time.time():.4f}")

    def clear_clock(self):
        #清空计时器
        self.timer=0

    def start(self):
        self.start_event.set()

    def stop(self):
        self.stop_event.set()

def main():
    energy = Energy()
    power_input = PowerInput(energy=energy)
    ecu = ECU(energy=energy)
    
    # 在单独线程运行ECU主循环，避免阻塞
    ecu_thread = threading.Thread(target=ecu.run)
    ecu_thread.start()

    #启动电源模拟
    power_input.start()
    # 模拟外部信号，先等待2秒再发start信号
    #time.sleep(2)
    #print("Sending start signal...")
    #ecu.start()

    #运行5秒后尝试重置计时
    time.sleep(5)
    ecu.clear_clock()
    print("Clock has been cleared...")
    #等待电源线程结束
    power_input.join()
    print("Battery test finished.")
    # 运行5秒后发送stop信号
    #time.sleep(5)
    #print("Sending stop signal...")

    # 等待ECU线程结束
    ecu.stop()
    ecu_thread.join()
    print("ECU test finished.")

if __name__ == "__main__":
    main()