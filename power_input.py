import threading
import time

VOLTAGE_THRESHOLD = 1.0

class PowerInput(threading.Thread):
    def __init__(self, energy):
        super().__init__()
        self.energy = energy
        self._running = False
        self._callbacks=[]
    def register_callback(self, callback):
        self._callbacks.append(callback)
    def notify_callbacks(self):
        for cb in self._callbacks:
            cb(self.energy.status)
    def run(self):
        self._running = True
        voltages = [0.0, 12.0, 12.0, 0.0, 12.0, 12.0, 0.0]  # 模拟电压序列
        intervals = [2, 5, 5, 3, 5, 2, 3] 
        idx = 0
        last_status = None
        while self._running and idx < len(voltages):
            v = voltages[idx]
            self.energy.Voltage = v
            if v >= VOLTAGE_THRESHOLD:
                new_status = "POWER_ON"
            else:
                new_status = "POWER_OFF"
            self.energy.status=new_status
            if new_status != last_status:
                print(f"[PowerInput] Voltage changed to {v}V, status: {new_status}")
                self.notify_callbacks()
                last_status = new_status
                
            time.sleep(intervals[idx])
            idx += 1
        print("[PowerInput] simulation finished.")

    def stop(self):
        self._running = False
