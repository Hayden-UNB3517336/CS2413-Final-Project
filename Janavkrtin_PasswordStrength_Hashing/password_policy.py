"""
Password strength policy
Rules:
  1. Minimum length 12. Maximum 128 so very long inputs can't be abused.
  2. Not on a list of common/breached passwords (case-insensitive), and its
     "base word" (trailing digits/symbols removed, e.g. Password123! -> password)
     is not on the list either.
  3. Must not contain the username.
  4. Not overly repetitive or sequential (aaaaaaaaaaaa, 123456789012).
  5. zxcvbn strength score >= 3 (0-4 scale). zxcvbn estimates how many guesses
     an attacker would need, using dictionaries, keyboard patterns, dates,
     l33t substitutions, etc.
"""
import re
import string
from dataclasses import dataclass, field
from pathlib import Path

from zxcvbn import zxcvbn

MIN_LENGTH = 12
MAX_LENGTH = 128
MIN_ZXCVBN_SCORE = 3

_LIST_PATH = Path(__file__).with_name("common_passwords.txt")


def _load_blocklist() -> set:
    if not _LIST_PATH.exists():
        return set()
    with _LIST_PATH.open(encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip() and not line.startswith("#")}


BLOCKLIST = _load_blocklist()


@dataclass
class PolicyResult:
    ok: bool
    score: int
    guesses_log10: float
    crack_time_offline_slow: str
    errors: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)


def _base_word(pw: str) -> str:
    return re.sub(r"[\d\W_]+$", "", pw.lower())


def _is_repetitive_or_sequential(pw: str) -> bool:
    if len(set(pw)) <= 2:
        return True
    seqs = [string.digits, string.ascii_lowercase, "qwertyuiopasdfghjklzxcvbnm"]
    low = pw.lower()
    for s in seqs:
        for seq in (s, s[::-1]):
            if any(low == (seq * 3)[i:i + len(low)] for i in range(len(seq))):
                return True
    return False


def check_password(password: str, username: str | None = None) -> PolicyResult:
    errors = []

    if len(password) < MIN_LENGTH:
        errors.append(f"must be at least {MIN_LENGTH} characters (got {len(password)})")
    if len(password) > MAX_LENGTH:
        errors.append(f"must be at most {MAX_LENGTH} characters")

    low = password.lower()
    if low in BLOCKLIST:
        errors.append("is a commonly used / breached password")
    elif _base_word(password) in BLOCKLIST and len(_base_word(password)) >= 4:
        errors.append("is a common password with digits/symbols added")

    if username and len(username) >= 3 and username.lower() in low:
        errors.append("must not contain the username")

    if _is_repetitive_or_sequential(password):
        errors.append("is too repetitive or sequential")

    z = zxcvbn(password[:MAX_LENGTH], user_inputs=[username] if username else [])
    if z["score"] < MIN_ZXCVBN_SCORE:
        errors.append(f"is too guessable (strength {z['score']}/4, need {MIN_ZXCVBN_SCORE})")

    suggestions = list(z["feedback"].get("suggestions", []))
    if z["feedback"].get("warning"):
        suggestions.insert(0, z["feedback"]["warning"])

    return PolicyResult(
        ok=not errors,
        score=z["score"],
        guesses_log10=round(z["guesses_log10"], 2),
        crack_time_offline_slow=z["crack_times_display"]["offline_slow_hashing_1e4_per_second"],
        errors=errors,
        suggestions=suggestions,
    )


def demo() -> None:
    samples = [
        "123456",
        "password123",
        "Password123!",
        "P@ssw0rd2024",
        "qwertyuiopas",
        "alice2024secure",
        "Tr0ub4dor&3",
        "correct horse battery staple",
        "violet-tundra-mango-42-lamp",
    ]
    print(f"{'password':<32}{'result':<10}{'score':<7}{'est. crack time*':<20}reasons")
    print("-" * 110)
    for pw in samples:
        r = check_password(pw, username="alice")
        status = "ACCEPT" if r.ok else "REJECT"
        print(f"{pw:<32}{status:<10}{r.score}/4   {r.crack_time_offline_slow:<20}{'; '.join(r.errors)}")
    print("\n*zxcvbn estimate assuming an offline attacker vs a slow hash at 10,000 guesses/sec.")


if __name__ == "__main__":
    demo()
