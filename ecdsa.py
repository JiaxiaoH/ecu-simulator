#ecdsa.py
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256, HMAC
from Crypto.Cipher import AES
import hashlib
from Crypto.Signature import DSS
FixedInfo=b"SessionKDFKey"
# ========= generate ECDHE key pair=========
def gen_ecdhe_keypair():
    '''
    return private_key -> ECC.EccKey, public_key -> ECC.EccKey
    '''
    sk = ECC.generate(curve='P-256')
    pk = sk.public_key()
    return sk, pk

# ========= create ECDHE key pair from AES =========
def derive_key_from_aes(aes_key: bytes, key_id: int):
    """
    """
    key_id_bytes = key_id.to_bytes(16, 'big')
    cipher = AES.new(aes_key, AES.MODE_ECB)
    aes_out = cipher.encrypt(key_id_bytes)
    digest = hashlib.sha256(aes_out).digest()
    sk_int = (int.from_bytes(digest, 'big') % (ECC._curves['P-256'].order - 1)) 
    sk = ECC.construct(curve='P-256', d=sk_int)
    pk = sk.public_key()
    return sk, pk

# ========= generate Kx_Z=========
def gen_kx_z(kx_sk: ECC.EccKey, kx_pk: ECC.EccKey) ->bytes:
    shared_point = kx_pk.pointQ * int(kx_sk.d)
    return int(shared_point.x).to_bytes(32, 'big')

# ========= generate ssk from kdf=========
def gen_ssk_kdf(kx_z: bytes, kdf_key:bytes) ->bytes:
    h = HMAC.new(kdf_key, digestmod=SHA256)
    h.update(kx_z)
    return h.digest()[:16]

# ========= generate ssk from kdf=========
def gen_ssk(kx_sk:ECC.EccKey, kx_pk: ECC.EccKey, data:bytes = FixedInfo):
    kx_z=gen_kx_z(kx_sk, kx_pk)
    #if data==FixedInfo:
    return gen_ssk_kdf(kx_z, data)
    #if data==other:
    #gen_ssk_other()

# ========= generate aes128=========
def aes128_encrypt(hex_list: list[int], key_list: list[int]) -> list[int]:
    if len(hex_list) != 16 or len(key_list) != 16:
        raise ValueError("Error: data is not 16 bytes!")
    data_bytes = bytes(hex_list)
    key_bytes = bytes(key_list)
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    encrypted = cipher.encrypt(data_bytes)
    return list(encrypted)

# ========= create ECC.EccKey from bytes=========
def bytes2Ecckey(b:bytes) ->ECC.EccKey:
    x = int.from_bytes(b[0:32], 'big')
    y = int.from_bytes(b[32:64], 'big')
    return ECC.construct(curve='P-256', point_x=x, point_y=y)

# ========= verify signature=========
def verify_signature(public_key: ECC.EccKey, msg: bytes, sig: bytes) -> bool:
    h = SHA256.new(msg)
    verifier = DSS.new(public_key, 'fips-186-3')
    try:
        verifier.verify(h, sig)
        return True
    except ValueError:
        return False