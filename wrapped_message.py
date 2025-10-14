import can
import datetime

class WrappedMessage(can.Message):
    def __init__(self, *, session=None, security=None, **kwargs):
        """
        参数:
            session/security: ECU 的状态信息
            kwargs: 所有传给 can.Message 的参数，如 arbitration_id, data 等
        """
        super().__init__(**kwargs)
        self.session = session
        self.security = security

    @property
    def msg_id_str(self):
        return f"{self.arbitration_id:X}"

    @property
    def data_str(self):
        return " ".join(f"{b:02X}" for b in self.data)

    @property
    def combined(self):
        return f"{self.msg_id_str} {self.data_str}"

    @property
    def direction(self):
        if self.is_rx==False:
            return f"Tx"
        else:
            return f"Rx"
    
    def __str__(self):
        return (f"{self.timestamp} {self.direction} {self.combined} "
                f"{self.session} {self.security}")
    
    @classmethod
    def wrap_from_msg(cls, msg, session=None, security=None):
        if msg is not None:
            base_kwargs = {}
            for attr in dir(msg):
                if not attr.startswith('_') and not callable(getattr(msg, attr)):
                    base_kwargs[attr] = getattr(msg, attr)
            return cls(session=session, security=security, **base_kwargs)