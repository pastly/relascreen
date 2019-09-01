from base64 import b64encode, b64decode
from ..user import User
from ..crypto import Pubkey
from . import Message, EncryptedMessage
import logging
from typing import Optional
from enum import Enum
import time

log = logging.getLogger(__name__)


class AccountReq(Message):
    def __init__(self, nick: str, pk: Pubkey):
        self.nick = nick
        self.pk = pk

    def __str__(self):
        return 'AccountReq<{n} {pk}>'.format(
            n=self.nick, pk=self.pk,
        )

    def to_dict(self) -> dict:
        d = {
            'nick': self.nick,
            'pk': b64encode(bytes(self.pk)).decode('utf-8'),
        }
        d.update(super().to_dict())
        return d

    @staticmethod
    def from_dict(d: dict) -> 'AccountReq':
        return AccountReq(
            d['nick'],
            Pubkey(b64decode(d['pk'].encode('utf-8'))),
        )

    def __eq__(self, rhs):
        return self.nick == rhs.nick \
            and self.pk == rhs.pk


class AccountRespErr(Enum):
    BadSig = 'The signature is invalid'
    PubkeyExists = 'A user with that pubkey already exists'
    Malformed = 'Message was not a valid AccountReq'
    WrongPubkey = 'Message signed with Seckey other than one associated with '\
        'given Pubkey'


class AccountResp(Message):
    def __init__(
            self, created: bool,
            cred: Optional[EncryptedMessage],
            err: Optional[AccountRespErr]):
        if created:
            assert err is None
            assert type(cred) == EncryptedMessage
        if not created:
            assert err is not None
            assert cred is None
        self.created = created
        self.cred = cred
        self.err = err

    @staticmethod
    def from_dict(d: dict) -> 'AccountResp':
        return AccountResp(
            d['created'],
            EncryptedMessage.from_dict(d['cred'])
            if d['cred'] is not None else None,
            d['err'],
        )

    def to_dict(self) -> dict:
        cred = self.cred.to_dict() if self.cred is not None else None
        d = {
            'created': self.created,
            'err': self.err,
            'cred': cred,
        }
        d.update(super().to_dict())
        return d

    def __eq__(self, rhs) -> bool:
        return self.created == rhs.created \
            and self.err == rhs.err \
            and self.cred == rhs.cred

    def __str__(self) -> str:
        return 'AccountResp<created={c} err={e} cred={cred}>'.format(
            c=self.created, e=self.err, cred=self.cred,
        )


class AccountCred(Message):
    def __init__(self, user: User, expire: float):
        assert user.rowid is not None
        self.user = user
        self.expire = expire  # timestamp it expires

    @staticmethod
    def gen(
            user: User,
            lifetime: float,  # duration, starting at *now*
            now: Optional[float] = None) -> 'AccountCred':
        if now is None:
            now = time.time()
        return AccountCred(user, now + lifetime)

    @staticmethod
    def from_dict(d: dict) -> 'AccountCred':
        u = User.from_dict(d['user'])
        return AccountCred(u, d['expire'])

    def to_dict(self) -> dict:
        d = {
            'user': self.user.to_dict(),
            'expire': self.expire,
        }
        d.update(super().to_dict())
        return d

    def __str__(self) -> str:
        return 'AccountCred<{u} {e}>'.format(
            u=self.user, e=self.expire,
        )

    def __eq__(self, rhs) -> bool:
        return self.user == rhs.user \
            and self.expire == rhs.expire


class AuthReq(Message):
    def __init__(self, user_pk: Pubkey):
        self.user_pk = user_pk

    def to_dict(self) -> dict:
        d = {
            'user_pk': b64encode(bytes(self.user_pk)).decode('utf-8'),
        }
        d.update(super().to_dict())
        return d

    @staticmethod
    def from_dict(d: dict) -> Optional['AuthReq']:
        if 'user_pk' not in d:
            return None
        return AuthReq(Pubkey(b64decode(d['user_pk'])))

    def __str__(self) -> str:
        return 'AuthReq<%s>' % (self.user_pk,)


class AuthChallenge(Message):
    def __init__(self, user: User, expire: float):
        assert user.rowid is not None
        self.user = user
        self.expire = expire

    def to_dict(self) -> dict:
        d = {
            'user': self.user.to_dict(),
            'expire': self.expire,
        }
        d.update(super().to_dict())
        return d

    @staticmethod
    def from_dict(d: dict) -> Optional['AuthChallenge']:
        if 'user' not in d or 'expire' not in d:
            return None
        u = User.from_dict(d['user'])
        if u is None:
            return None
        return AuthChallenge(u, d['expire'])

    def __str__(self) -> str:
        return 'AuthChallenge<%s %f>' % (
            self.user, self.expire)


class AuthChallengeResp(Message):
    def __init__(self, enc_chal: EncryptedMessage):
        self.enc_chal = enc_chal

    def to_dict(self) -> dict:
        d = {
            'enc_chal': self.enc_chal.to_dict(),
        }
        d.update(super().to_dict())
        return d

    @staticmethod
    def from_dict(d: dict) -> Optional['AuthChallengeResp']:
        if 'enc_chal' not in d:
            return None
        enc_chal = EncryptedMessage.from_dict(d['enc_chal'])
        if enc_chal is None:
            return None
        return AuthChallengeResp(enc_chal)

    def __str__(self) -> str:
        return 'AuthChallengeResp<%s>' % (self.enc_chal,)
