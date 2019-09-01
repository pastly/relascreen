from ugh.lib.messages import account
from ugh.lib.messages import Message, SignedMessage, EncryptedMessage, Stub
from ugh.lib.user import User
from ugh.lib.crypto import Pubkey, Seckey, Enckey
from base64 import b64encode, b64decode
import time

U = User('Foo', Pubkey((1).to_bytes(32, byteorder='big')), rowid=420)
SK = Seckey((28379873947).to_bytes(32, byteorder='big'))
EK = Enckey.gen()
ALL_ACCRESP_ARG_SETS = [
    (True, EncryptedMessage.enc(
        SignedMessage.sign(account.AccountCred.gen(U, 60), SK), EK), None),
    (False, None, account.AccountRespErr.BadSig),
    (False, None, account.AccountRespErr.BadSig),
    (False, None, account.AccountRespErr.PubkeyExists),
    (False, None, account.AccountRespErr.Malformed),
    (False, None, account.AccountRespErr.WrongPubkey),
]


def test_accountreq_dict_identity():
    first = account.AccountReq(U.nick, U.pk)
    second = Message.from_dict(first.to_dict())
    assert first == second


def test_accountreq_to_dict():
    ar = account.AccountReq(U.nick, U.pk)
    d = ar.to_dict()
    assert d['nick'] == U.nick
    assert Pubkey(b64decode(d['pk'])) == U.pk


def test_accountreq_from_dict():
    d = {
        'nick': U.nick,
        'pk': b64encode(bytes(U.pk)).decode('utf-8'),
    }
    ar = account.AccountReq.from_dict(d)
    assert ar.nick == d['nick']
    assert ar.pk == Pubkey(b64decode(d['pk']))


def test_accountreq_str():
    s = 'AccountReq<%s %s>' % (U.nick, U.pk)
    ar = account.AccountReq(U.nick, U.pk)
    assert str(ar) == s


def test_accountresp_dict_identity():
    for args in ALL_ACCRESP_ARG_SETS:
        first = account.AccountResp(*args)
        second = Message.from_dict(first.to_dict())
        assert first == second


def test_accountresp_to_dict():
    for created, cred, err in ALL_ACCRESP_ARG_SETS:
        ar = account.AccountResp(created, cred, err)
        d = ar.to_dict()
        assert d['created'] == created
        assert d['cred'] == (cred.to_dict() if cred is not None else None)
        assert d['err'] == err


def test_accountresp_from_dict():
    for created, cred, err in ALL_ACCRESP_ARG_SETS:
        d = {
            'created': created,
            'cred': cred.to_dict() if cred is not None else None,
            'err': err
        }
        ar = account.AccountResp.from_dict(d)
        assert ar.created == created
        assert ar.cred == cred
        assert ar.err == err


def test_accountresp_str():
    fmt = 'AccountResp<created={c} err={e} cred={cred}>'
    for created, cred, err in ALL_ACCRESP_ARG_SETS:
        s = fmt.format(c=created, e=err, cred=cred)
        ar = account.AccountResp(created, cred, err)
        assert str(ar) == s


def test_accountcred_dict_identity():
    first = account.AccountCred(U, 1)
    second = Message.from_dict(first.to_dict())
    assert first == second


def test_accountcred_to_dict():
    ac = account.AccountCred(U, 1)
    d = ac.to_dict()
    assert User.from_dict(d['user']) == U
    assert d['expire'] == 1


def test_accountcred_from_dict():
    d = {'user': U.to_dict(), 'expire': 1}
    ac = account.AccountCred.from_dict(d)
    assert ac.user == U
    assert ac.expire == 1


def test_accountcred_str():
    s = 'AccountCred<%s %s>' % (U, 1)
    ac = account.AccountCred(U, 1)
    assert str(ac) == s


def test_authreq_dict_identity():
    first = account.AuthReq(U.pk)
    second = account.AuthReq.from_dict(first.to_dict())
    assert first == second


def test_authreq_dict_no_user():
    d = account.AuthReq(U.pk).to_dict()
    del d['user_pk']
    assert account.AuthReq.from_dict(d) is None


def test_authreq_str():
    ar = account.AuthReq(U.pk)
    s = 'AuthReq<%s>' % (U.pk,)
    assert str(ar) == s


def test_authchallenge_dict_identity():
    u = User(U.nick, U.pk, rowid=1)
    first = account.AuthChallenge(u, time.time())
    second = account.AuthChallenge.from_dict(first.to_dict())
    assert first == second


def test_authchallenge_dict_no_user():
    u = User(U.nick, U.pk, rowid=1)
    d = account.AuthChallenge(u, time.time()).to_dict()
    del d['user']
    assert account.AuthChallenge.from_dict(d) is None


def test_authchallenge_dict_bad_user():
    u = User(U.nick, U.pk, rowid=1)
    d = account.AuthChallenge(u, time.time()).to_dict()
    del d['user']['nick']
    assert account.AuthChallenge.from_dict(d) is None


def test_authchallenge_str():
    u = User(U.nick, U.pk, rowid=1)
    now = time.time()
    s = 'AuthChallenge<%s %f>' % (u, now)
    assert str(account.AuthChallenge(u, now)) == s


def test_authchallenegeresp_dict_identity():
    echal = EncryptedMessage.enc(Stub(1), EK)
    first = account.AuthChallengeResp(echal)
    second = account.AuthChallengeResp.from_dict(first.to_dict())
    assert first == second


def test_authchallengeresp_dict_no_enc_chal():
    echal = EncryptedMessage.enc(Stub(1), EK)
    d = account.AuthChallengeResp(echal).to_dict()
    del d['enc_chal']
    assert account.AuthChallengeResp.from_dict(d) is None


def test_authchallengeresp_dict_bad_enc_chal():
    d = account.AuthChallengeResp(Stub(1)).to_dict()
    assert account.AuthChallengeResp.from_dict(d) is None


def test_authchallengeresp_str():
    echal = EncryptedMessage.enc(Stub(1), EK)
    acr = account.AuthChallengeResp(echal)
    s = 'AuthChallengeResp<%s>' % (echal,)
    assert str(acr) == s
