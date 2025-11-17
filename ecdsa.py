#ecdsa.py
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256, HMAC
from Crypto.Cipher import AES
import hashlib
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
    # x = int.from_bytes(kx_pk[0:32], 'big')
    # y = int.from_bytes(kx_pk[32:], 'big')
    # public = ECC.construct(curve="P-256", point_x=x, point_y=y)
    #d = int.from_bytes(kx_sk, 'big')
    shared_point = kx_pk.pointQ * int(kx_sk.d)
    return int(shared_point.x).to_bytes(32, 'big')

# ========= generate ssk from kdf=========
def gen_ssk_kdf(kx_z: bytes, kdf_key:bytes) ->bytes:
    h = HMAC.new(kdf_key, digestmod=SHA256)
    h.update(kx_z)
    return h.digest()

# ========= generate ssk from kdf=========
def gen_ssk(kx_sk:ECC.EccKey, kx_pk: ECC.EccKey, data:bytes = b"SessionKDFKey"):
    kx_z=gen_kx_z(kx_sk, kx_pk)
    return gen_ssk_kdf(kx_z, data)
    #gen_ssk_other()