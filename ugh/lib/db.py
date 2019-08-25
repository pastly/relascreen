import os
import logging
import sqlite3
from typing import Iterator, Optional
from .user import User, Pubkey

log = logging.getLogger(__name__)


def insert_user(conn: sqlite3.Connection, u: User):
    q = 'INSERT INTO users VALUES (?, ?)'
    conn.execute(q, (u.nick, u.pk))
    conn.commit()


def connect(fname: str, schema=None):
    if fname == ':memory:' or not os.path.exists(fname):
        if not schema:
            log.error(
                '%s does not exist and no default schema provided', fname)
            return False, None
        log.info('Creating db at %s', fname)
        conn = sqlite3.connect(fname, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.executescript(schema)
        conn.commit()
        return True, conn
    log.info('Opening db at %s', fname)
    conn = sqlite3.connect(fname, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return True, conn


def get_users(conn: sqlite3.Connection) -> Iterator[User]:
    q = 'SELECT rowid, * from users'
    c = conn.cursor()
    c.execute(q)
    while True:
        ret = c.fetchone()
        if not ret:
            return
        yield User.from_row(ret)


def user_with_pk(conn: sqlite3.Connection, pk: Pubkey) -> Optional[User]:
    q = 'SELECT rowid, * from users WHERE pk=?'
    c = conn.execute(q, (pk,))
    ret = c.fetchall()
    assert len(ret) == 0 or len(ret) == 1
    if not len(ret):
        return None
    return User.from_row(ret[0])