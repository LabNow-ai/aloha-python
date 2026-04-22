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
