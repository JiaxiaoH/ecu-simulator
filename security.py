#security.py
#from enum import Enum
class SecurityType:
    FALSE = 0
    #TYPE_IV = 4
    TYPE_V = 5
    TYPE_X = 10

SECURITY_NAME_MAP = {
    0x00: "FALSE",
    0x04: "TYPE_IV",
    0x05: "TYPE_V",
    0x0A: "TYPE_X",
}