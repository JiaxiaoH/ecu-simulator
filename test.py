from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS
SIGNATUREALGORITHM={
    "0x01":{
        "name": "RSASSA-PSS",
        "public_key": {
            "curve": "P-256",
            "point_x": 60788269693578391605701232291496395347516283271159972725498624817650223682989, 
            "point_y": 102998700983441244218412734983691136299552256856023109374897557028854247807763,
        },
        "keyID": [0x00, 0x01],
    },
    "0x02":{
        "name": "ECDSA",
        "public_key": {
            "curve": "P-256",
            "point_x": 60788269693578391605701232291496395347516283271159972725498624817650223682989, 
            "point_y": 102998700983441244218412734983691136299552256856023109374897557028854247807763,
        },
        "keyID": [0xFF, 0xFF],
    }    
}
tester_keys_dict={
    (0x00, 0x01): ECC.construct(curve="P-256", point_x=60788269693578391605701232291496395347516283271159972725498624817650223682989, point_y=102998700983441244218412734983691136299552256856023109374897557028854247807763, d=44645349677068312377741899704457059576941778957474339060687599889300058147639),
    (0xFF, 0xFF): ECC.construct(curve="P-256", point_x=60788269693578391605701232291496395347516283271159972725498624817650223682989, point_y=102998700983441244218412734983691136299552256856023109374897557028854247807763, d=44645349677068312377741899704457059576941778957474339060687599889300058147639),
}
def gen_keypair():
    # 生成一对 P-256 椭圆曲线密钥
    sk = ECC.generate(curve='P-256')
    pk = sk.public_key()
    return sk, pk

def sign_message(private_key: ECC.EccKey, msg: bytes) -> bytes:
    # 做哈希
    h = SHA256.new(msg)
    # 用 FIPS-186-3 模式做 ECDSA
    signer = DSS.new(private_key, 'fips-186-3')
    sig = signer.sign(h)  # 返回 signature bytes
    return sig

def verify_signature(public_key: ECC.EccKey, msg: bytes, sig: bytes) -> bool:
    h = SHA256.new(msg)
    verifier = DSS.new(public_key, 'fips-186-3')
    try:
        verifier.verify(h, sig)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    # 1. 生成密钥对
    #sk, pk = gen_keypair()
    pk_dict = SIGNATUREALGORITHM["0x02"]["public_key"]
    pk = ECC.construct(
        curve=pk_dict["curve"],
        point_x=pk_dict["point_x"],
        point_y=pk_dict["point_y"]
    )
    keyID=[0xFF, 0xFF]
    sk = tester_keys_dict[tuple(keyID)]
    # 2. 待签名数据
    message = b"hello, this is ECDSA test"

    # 3. 签名
    signature = sign_message(sk, message)
    print("Signature (len={}): {}".format(len(signature), signature.hex()))

    # 4. 验证（成功例）
    if verify_signature(pk, message, signature):
        print("verify ok")
    else:
        print("verify failed")

    # 5. 验证（失败例）——故意改一字节
    bad_msg = b"hello, this is ECDSA tesT"
    if verify_signature(pk, bad_msg, signature):
        print("verify ok (should NOT happen!)")
    else:
        print("verify failed as expected")