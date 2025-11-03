class Energy:
    def __init__(self):
        self._voltage = 0.0
        self._status = 'POWER_OFF'
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        self._status = value
        if value == 'POWER_ON':
            self._voltage=12.0
        if value == 'POWER_OFF':
            self._voltage=0.0
    @property
    def voltage(self):
        return self._voltage

    #@Voltage.setter
    #def Voltage(self, value):
    #    self._Voltage = value
