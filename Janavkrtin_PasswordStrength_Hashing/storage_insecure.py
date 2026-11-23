
import hashlib
import json


class PlaintextStore:
    def __init__(self):
        self.db = {}

    def register(self, username: str, password: str) -> None:
        self.db[username] = password

    def verify(self, username: str, password: str) -> bool:
        return self.db.get(username) == password


class Sha256Store:
    def __init__(self):
        self.db = {}

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> None:
        self.db[username] = self._hash(password)

    def verify(self, username: str, password: str) -> bool:
        return self.db.get(username) == self._hash(password)


def demo() -> None:
    users = [("alice", "password123"), ("bob", "password123"), ("carol", "Tr0ub4dor&3")]

    plain, sha = PlaintextStore(), Sha256Store()
    for u, p in users:
        plain.register(u, p)
        sha.register(u, p)

    print("=== BEFORE: plaintext database (what a breach exposes) ===")
    print(json.dumps(plain.db, indent=2))
    print("\n=== BEFORE: unsalted SHA-256 database ===")
    print(json.dumps(sha.db, indent=2))

    same = sha.db["alice"] == sha.db["bob"]
    print(f"\nalice and bob share a password -> identical hashes? {same}")
    print("Problem: one cracked hash reveals every account with that password.")


if __name__ == "__main__":
    demo()
