from rela.lib.crypto import Pubkey, Enckey
from base64 import b64encode


PK_VALS = {
    0, 3, 255, 256, 2897,
    1356938545749799165119972480570561420155507632800475359837393562592731987968}  # noqa:E501


def test_pubkey_init():
    for v in PK_VALS:
        v_bytes = v.to_bytes(32, byteorder='big')
        pk = Pubkey(v_bytes)
        assert bytes(pk) == v_bytes


def test_pubkey_adapt():
    for v in PK_VALS:
        v_bytes = v.to_bytes(32, byteorder='big')
        pk = Pubkey(v_bytes)
        b = Pubkey.sql_adapt(pk)
        assert len(b) == 32
        assert int.from_bytes(b, byteorder='big') == v


def test_pubkey_convert():
    for v in PK_VALS:
        v_bytes = v.to_bytes(32, byteorder='big')
        pk = Pubkey.sql_convert(v_bytes)
        assert pk == Pubkey(v_bytes)


def test_pubkey_str():
    for v in [v.to_bytes(32, byteorder='big') for v in PK_VALS]:
        s = 'Pubkey<%s..%s (%d bytes)>' % (
            b64encode(v[:6]).decode('utf-8'),
            b64encode(v[-6:]).decode('utf-8'),
            len(v))
        assert str(Pubkey(v)) == s


def test_enckey_gen():
    k = Enckey.gen()
    assert len(bytes(k)) == 32
