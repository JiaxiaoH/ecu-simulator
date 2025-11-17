#tester_create_key.py
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

tester_keys_dict={
    (0x00, 0x01): ECC.construct(curve="P-256", point_x=60788269693578391605701232291496395347516283271159972725498624817650223682989, point_y=102998700983441244218412734983691136299552256856023109374897557028854247807763, d=44645349677068312377741899704457059576941778957474339060687599889300058147639),
    (0xFF, 0xFF): ECC.construct(curve="P-256", point_x=60788269693578391605701232291496395347516283271159972725498624817650223682989, point_y=102998700983441244218412734983691136299552256856023109374897557028854247807763, d=44645349677068312377741899704457059576941778957474339060687599889300058147639),
}

def find_secret_key(keyID)->ECC.EccKey:
    return tester_keys_dict[tuple(keyID)]

def gen_signature(secret_key: ECC.EccKey, kx_pk1: ECC.EccKey) -> bytes:
    kx_pk1_bytes_for_hash = int(kx_pk1.pointQ.x).to_bytes(32, 'big') + int(kx_pk1.pointQ.y).to_bytes(32, 'big')
    h=SHA256.new(kx_pk1_bytes_for_hash)
    signer = DSS.new(secret_key, 'fips-186-3')
    signature = signer.sign(h)
    # print("[Tester] SIGNATURE:", signature.hex())
    # print("[Tester] SIGNATURE LENGTH:", len(signature))
    print(f"[Tester] kx_pk1: {kx_pk1}")
    return signature

def gen_rid0x111_req(kx_pk1: ECC.EccKey, signature: bytes):
    x = int(kx_pk1.pointQ.x).to_bytes(32, 'big')
    y = int(kx_pk1.pointQ.y).to_bytes(32, 'big')
    #msglist=[0x31, 0x01, 0xD1, 0x11]+list(kx_pk1)+list(signature) 这一行是kx_pk1是bytes的时候的
    msglist = [0x31, 0x01, 0xD1, 0x11] + list(x + y + signature) #这一行是kx_pk1换成EccKey的
    if len(msglist)<452:
        msglist.extend([0x00] * (452 - len(msglist)))
    return msglist
