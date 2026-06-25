# Encryption and Utility Modules (`aloha.encrypt`)

The `aloha.encrypt` subpackage contains functions and classes for AES encryption, RSA signing/encryption, JWT token encoding/decoding, and hashing utilities.

## 1. AES Encryption (`aloha.encrypt.aes`)

Uses PyCryptodome to encrypt/decrypt payloads with standard AES configurations.

### Key Classes

- `AesEncryptor(key: Union[str, bytes] = None, key_size: int = 16, cipher_name: str = "AES/ECB/PKCS5Padding")`
  - Supports ECB and CBC modes (defined in `supported_cipher_methods`).
  - Methods:
    - `encrypt(text: str, output_format="hex", func_pad=None) -> Union[str, bytes]`
    - `decrypt(text: Union[str, bytes], input_format="hex", func_unpad=None) -> str`

### Usage Example

```python
from aloha.encrypt.aes import AesEncryptor

encryptor = AesEncryptor(key="my-secret-16bytes", cipher_name="AES/CBC/PKCS7Padding")
ciphertext = encryptor.encrypt("Hello World")
decrypted = encryptor.decrypt(ciphertext)
```

---

## 2. RSA Cryptography (`aloha.encrypt.rsa`)

Provides asymmetric encryption, decryption, and signature creation/verification using RSA key pairs.

### Key Classes

- `RsaEncryptor(key_private: str | None = None, key_public: str | None = None, cipher_name: str = "RSA/ECB/PKCS1Padding")`
  - Methods:
    - `encrypt(text: str, output_format="base64") -> str`
    - `decrypt(text: str, input_format="base64") -> str`
    - `sign(text: str, signature_format="base64", hash_algo="SHA-256") -> str`
    - `verify(text: str, signature: str, signature_format="base64", hash_algo="SHA-256") -> bool`
  - Static Methods:
    - `generate_key_pair(size: int = 1024) -> Tuple[str, str]`: Generates a tuple of `(private_key_pem, public_key_pem)`.

---

## 3. JWT Utilities (`aloha.encrypt.jwt`)

Wraps `pyjwt` to encode and decode tokens.

### Key Functions

- `encode(secret_key: str, payload: dict, headers: dict | None = None, **kwargs) -> str`
- `decode(secret_key: str, token: str, **kwargs) -> Union[dict, str]`: Decodes the token, catching exceptions like `ExpiredSignatureError` or `PyJWTError` and returning them as strings.

---

## 4. Hashing Utilities (`aloha.encrypt.hash`)

Provides standard hashing algorithms.

### Key Functions

- `get_md5_of_str(string: str) -> str`: Return MD5 hex digest.
- `get_sha256_of_str(string: str) -> str`: Return SHA-256 hex digest.
- `hash_dict(dic: dict) -> str`: Normalizes the dictionary to sorted JSON and returns its MD5 hash.
- `hash_obj(obj: any) -> str`: Serializes any JSON-compatible object and returns its MD5 hash.
- `hash_base62(s: str, length: int = 6) -> str`: Computes SHA-256 and encodes it using a custom Base62 alphabet of length between 1 and 11.
