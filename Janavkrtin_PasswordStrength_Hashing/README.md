# Password Security and Hashing – CS2413 Group 10

| File | Purpose |
|---|---|
| `storage_insecure.py` | **Before**: plaintext and unsalted SHA-256 storage |
| `storage_secure.py` | **After**: salted Argon2id (plus bcrypt for comparison), with the policy enforced at registration |
| `password_policy.py` | Password strength policy (NIST SP 800-63B style) |
| `common_passwords.txt` | Blocklist of common/breached passwords |
| `benchmark.py` | Experiment: measures hash cost and estimates search time by length and character set |
| `tests/` | 19 pytest tests covering before and after behaviour |
| `results/` | Generated tables and chart |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python storage_insecure.py   # BEFORE: plaintext and identical hashes
python storage_secure.py     # AFTER: unique salted hashes, login checks, policy
python password_policy.py    # strength checker on sample passwords
python benchmark.py          # experiment -> results/
python -m pytest -v          # all tests
```


