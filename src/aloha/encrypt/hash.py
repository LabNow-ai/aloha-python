"""Hash helpers used by the signing utilities."""

import hashlib
import json


def get_md5_of_str(string):
    """Return the MD5 hex digest of a string."""
    return hashlib.md5(string.encode()).hexdigest()


def get_sha256_of_str(string):
    """Return the SHA-256 hex digest of a string."""
    return hashlib.sha256(string.encode()).hexdigest()


def hash_dict(dic):
    """Hash a dictionary after JSON normalization."""
    s = json.dumps(dict(dic), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.md5(s.encode()).hexdigest()


def hash_obj(obj):
    """Hash an arbitrary JSON-serializable object."""
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.md5(s.encode()).hexdigest()


def hash_base62(s: str, length: int = 6) -> str:
    """Return a Base62-encoded hash of a string with specified length."""
    assert length > 0 and length <= 11, "Length must be between 1 and 11 for Base62 encoding."

    CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    digest = hashlib.sha256(s.encode()).digest()  # 32 bytes = 256 bits
    # Convert the digest to an integer and then to Base62
    num = int.from_bytes(digest, "big")
    result = []
    for _ in range(length):
        result.append(CHARS[num % 62])
        num //= 62
    return "".join(reversed(result))
