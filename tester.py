# tester.py
import can
from typing import List, Optional
from tester_create_key import find_secret_key, gen_signature, gen_rid0x111_req
from keys import ALGORITHMINDICATOR, AES_KEY, XOR_MASK
from ecdsa import gen_ecdhe_keypair, gen_ssk, aes128_encrypt, bytes2Ecckey

class TesterError(Exception):
    pass

class Tester(can.Listener):
    def __init__(self, bus: can.Bus):
        self.reset()
        self.bus=bus

    def reset(self): 
        # keyID is from ecu answer of DID 0xD110
        # default to invalid value
        self.keyID = (0xFF, 0xFF)
        # ECDHE keys
        self.kx_sk1 = None
        self.kx_pk2 = None
        self.ssk = None
        # authentication result
        self.authenticator = None
        # SecurityAccess keys
        self.key_TypeV = None
        self.key_TypeX = None
        # arbitration ID
        self.arbitration_id = 0x18DABAF1

    # ========= updated by response message =========
    def on_message_received(self, msg)->None:
        data = list(msg.data)
        # DID 0xD110 → keyID
        if data[0:3] == [0x62, 0xD1, 0x10]:
            self.keyID = (data[4], data[5])
            return
        # RID 0xD111 → ssk
        if data[0:6] == [0x71, 0x01, 0xD1, 0x11, 0x00, 0x00]:
            raw_pk = data[6:]
            self.kx_pk2 = bytes2Ecckey(raw_pk)
            self.ssk = gen_ssk(self.kx_sk1, self.kx_pk2)
            return
        # SID 0x29 0x06 → authenticator
        if data[0:3]==[0x69, 0x05, 0x00]:
            challengeServer=msg.data[21:37]
            self.authenticator=aes128_encrypt(challengeServer, self.ssk)
            self.ssk=None    
        # SID 0x27 0x07 → request seed of TypeV
        if data[0:2] == [0x67, 0x07] and data[2:]!=[0x00]*4:
            rn2=data[2:4]
            self.key_TypeV=[b ^ m for b, m in zip(rn2, XOR_MASK)] 
            return
        # SID 0x27 0x31 → request seed of TypeX
        if data[0:2] == [0x67, 0x31] and data[2:]!=[0x00]*16:
            securitySeed=data[2:18]
            self.key_TypeX=aes128_encrypt(securitySeed, AES_KEY)
            return

    # ========= Request Generation API =========
    def generate(self, cmd: str) -> List[int]:
        """Generate request message data based on command string."""
        mapping = {
            "RID_D111": self.generate_rid0xd111_request,
            "SID_29_05": self.generate_sid0x29_0x05_request,
            "SID_29_06": self.generate_sid0x29_0x06_request,
            "SID_27_08": self.generate_sid0x27_0x08_request,
            "SID_27_32": self.generate_sid0x27_0x32_request,
        }
        if cmd not in mapping:
            raise TesterError(f"Unknown command: {cmd}")
        return mapping[cmd]()
    
    def available_commands(self) -> List[str]:
        '''Return a list of available command strings.'''
        return [
            "RID_D111",
            "SID_29_05",
            "SID_29_06",
            "SID_27_08",
            "SID_27_32",
        ]
    
    # ========= Message generation function for GUI =========
    def generate_rid0xd111_request(self) -> list[int]:
        self.kx_sk1, kx_pk1 = gen_ecdhe_keypair()
        secret_key = find_secret_key(self.keyID)
        signature = gen_signature(secret_key, kx_pk1)
        return gen_rid0x111_req(kx_pk1, signature)
    
    def generate_sid0x29_0x05_request(self) ->list[int]:
        return [0x29, 0x05, 0x00] + ALGORITHMINDICATOR
    
    def generate_sid0x29_0x06_request(self) -> list[int]:
        if self.authenticator is None:
            return []
        return [0x29, 0x06] + ALGORITHMINDICATOR + [0x00, 0x10] + \
            list(self.authenticator) + [0x00] * 4

    def generate_sid0x27_0x08_request(self) -> list[int]:
        return [0x27, 0x08] + self.key_TypeV if self.key_TypeV is not None else []

    def generate_sid0x27_0x32_request(self) -> list[int]:
        return [0x27, 0x32] + self.key_TypeX if self.key_TypeX is not None else []
    
    #========= Send message to bus =========
    def send_message(self, data: List[int], arbitration_id:int=None) -> None:
        """Send CAN message with given data and arbitration ID."""
        if arbitration_id is None:
            arbitration_id=self.arbitration_id
        msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=True)
        try:
            self.bus.send(msg)
            print(f"[Tester] Sent message: {msg}")
        except can.CanError as e:
            raise TesterError(f"Failed to send message: {e}")