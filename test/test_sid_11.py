import pytest
def build_request(sid, subfunction=None, length=None):
    """
    构造一个 request：
    - sid: 1 byte
    - subfunction: optional
    - length: 覆盖 boundary test 的任意长度（1 / 2 / 3 / 7 / 4095 bytes）
    """
    if length is None:
        # 标准长度
        if subfunction is None:
            return bytes([sid])
        return bytes([sid, subfunction])

    # Boundary/fuzzing test
    if subfunction is None:
        # 长度 = 1 => 不可能再有 sub-function
        return bytes([sid] + [0x00] * (length - 1))

    # 长度 >=2，则 subfunction 必须被放在第2 byte
    payload = [sid, subfunction]

    # 剩余填充 dummy data
    if length > 2:
        payload += [0xAA] * (length - 2)

    return bytes(payload)


# =============================================
# SID 11 – ECU Reset 测试规范
# =============================================

SUPPORTED_SUBFUNCTIONS = {0x01, 0x02}   # HardReset, KeyOffOnReset

def expected_response(ecu, req: bytes):
    """
    根据 request 自动判断 ECU 期望返回值。
    不依赖 ECU 内部实现，只依据 ISO14229。
    """

    # ---- ① 长度检查 ----
    if len(req) == 1:
        return ("NRC", 0x13)   # Incorrect Message Length

    if len(req) > 2:
        return ("NRC", 0x13)   # 多余参数 => Incorrect Message Length

    subfunc = req[1]

    # ---- ② sub-function 支持性 ----
    if subfunc not in SUPPORTED_SUBFUNCTIONS:
        return ("NRC", 0x12)   # Sub-function Not Supported

    # ---- ③ 正常情况 ----
    # ECU Reset 允许先回 0x78，再回 positive
    # 这里默认只判断最终结果即可
    return ("POSITIVE", subfunc)


# =============================================
# Parameterized Test Cases
# =============================================
test_cases = [

    # --------- 长度 = 1（无 sub-function）---------
    (1, None),

    # --------- 长度 = 2（标准输入 + fuzz subfunction）---------
    (2, 0x00),
    (2, 0x01),
    (2, 0x02),
    (2, 0x80),
    (2, 0x81),
    (2, 0x82),
    (2, 0x7F),
    (2, 0xFF),

    # --------- 长度 = 3（超长）---------
    (3, 0x01),
    (3, 0x81),

    # --------- 长度 = 7（超长）---------
    (7, 0x01),
    (7, 0x81),

    # --------- 长度 = 4095（Boundary Fuzzing）---------
    (4095, 0x01),
    (4095, 0x81),
]


@pytest.mark.parametrize("length, subfunc", test_cases)
def test_sid_11(ecu, length, subfunc):
    """
    SID 0x11 ECU Reset 单元测试（覆盖所有输入组合）

    - 长度 1 → 必定 NRC 13
    - 长度 >2 → 必定 NRC 13
    - 长度 2:
        - subfunc 01/02 → Positive Response
        - 其他 → NRC 12
    """

    req = build_request(0x11, subfunc, length)
    expected_type, expected_value = expected_response(ecu, req)

    resp = ecu.dispatch(req)

    # ========== 判断响应格式 ==========

    # Negative Response
    if expected_type == "NRC":
        assert resp[0] == 0x7F
        assert resp[1] == 0x11
        assert resp[2] == expected_value
        return

    # Positive Response
    if expected_type == "POSITIVE":
        # 注意：ECU Reset 可能先返回 78 再返回 positive，
        # 因此这里只检查最终值
        assert resp[0] == 0x51
        assert resp[1] == expected_value
        return

    # 不可能走到这里
    assert False