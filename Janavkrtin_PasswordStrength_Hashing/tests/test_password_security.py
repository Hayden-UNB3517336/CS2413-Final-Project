import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from password_policy import check_password  # noqa: E402
from storage_insecure import PlaintextStore, Sha256Store  # noqa: E402
from storage_secure import Argon2Store, BcryptStore, WeakPasswordError  # noqa: E402


# ---------- BEFORE: demonstrate the weaknesses ----------

def test_plaintext_store_exposes_password():
    s = PlaintextStore()
    s.register("alice", "password123")
    assert s.db["alice"] == "password123"


def test_unsalted_hash_identical_for_same_password():
    s = Sha256Store()
    s.register("alice", "password123")
    s.register("bob", "password123")
    assert s.db["alice"] == s.db["bob"]


# ---------- AFTER: secure storage ----------

@pytest.fixture
def store():
    return Argon2Store(enforce_policy=False)


def test_argon2_salts_make_hashes_unique(store):
    store.register("alice", "password123")
    store.register("bob", "password123")
    assert store.db["alice"] != store.db["bob"]


def test_argon2_does_not_store_plaintext(store):
    store.register("alice", "password123")
    assert "password123" not in store.db["alice"]
    assert store.db["alice"].startswith("$argon2id$")


def test_argon2_verify_correct_and_wrong(store):
    store.register("alice", "correct horse battery staple")
    assert store.verify("alice", "correct horse battery staple")
    assert not store.verify("alice", "correct horse battery stapl")
    assert not store.verify("alice", "")


def test_unknown_user_returns_false(store):
    assert not store.verify("nobody", "whatever")


def test_bcrypt_store():
    s = BcryptStore()
    s.register("alice", "pw-one-two-three")
    s.register("bob", "pw-one-two-three")
    assert s.db["alice"] != s.db["bob"]
    assert s.verify("alice", "pw-one-two-three")
    assert not s.verify("alice", "nope")


# ---------- Password policy ----------

@pytest.mark.parametrize("pw", [
    "123456",                # too short + common
    "password123",           # common
    "Password123!",          # common base word with suffix
    "qwertyuiopas",          # keyboard sequence
    "aaaaaaaaaaaaaa",        # repetitive
    "alice-likes-cats-99",   # contains username
])
def test_policy_rejects_weak(pw):
    assert not check_password(pw, username="alice").ok


@pytest.mark.parametrize("pw", [
    "correct horse battery staple",
    "violet-tundra-mango-42-lamp",
    "my cat eats 3 tacos on fridays",
])
def test_policy_accepts_strong(pw):
    assert check_password(pw, username="alice").ok


def test_policy_gives_reasons():
    r = check_password("short", username="alice")
    assert r.errors and any("12 characters" in e for e in r.errors)


def test_registration_blocks_weak_password():
    s = Argon2Store(enforce_policy=True)
    with pytest.raises(WeakPasswordError):
        s.register("dave", "password123")
    assert "dave" not in s.db


def test_registration_allows_strong_password():
    s = Argon2Store(enforce_policy=True)
    s.register("erin", "correct horse battery staple")
    assert s.verify("erin", "correct horse battery staple")
