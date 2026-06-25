---
name: aloha-python
description: Guides on Python development standards, importing and using the aloha package, HOCON configuration, and running aloha-based applications.
---

# Aloha Python Skill

This skill provides coding standards, modular application structures, and usage guidelines for the `aloha` Python package within the `aloha-python` boilerplate structure.

---

## 1. Python Naming & Coding Standards

When developing Python code in this codebase, adhere to the following naming conventions:

- **Primary Type/First-Class Identity Prefix**: Place the variable's type, role, or primary characteristics first in its name.
  - _Correct_: `name_service`, `port_service`, `svc_ingress`, `cfg_postgres`.
  - _Incorrect_: `service_name`, `service_port`, `ingress_service`, `postgres_config`.
- **Logger naming**: Use lowercase with underscores for logger names, e.g., `db_sync`.

---

## 2. Package Architecture & Sub-Modules

The `aloha` package is divided into several specialized sub-modules. See their respective reference documents for detailed APIs and usage examples:

- **[Configuration Management (`aloha.config`)](references/config.md)**: HOCON configuration loading, environment profile handling (`ENV_PROFILE`), and settings loading via `SETTINGS`.
- **[Logging Framework (`aloha.logger`)](references/logger.md)**: Safe concurrent multi-process logging, console handlers, and custom logger setups.
- **[Encryption & Hashing (`aloha.encrypt`)](references/encrypt.md)**: AES encryption, RSA keys generation & signing/verifying, JWT encoding/decoding, and dictionary/object hashing helpers.
- **[Testing Utilities (`aloha.testing`)](references/testing.md)**: Base `UnitTestCase` class with pre-configured settings/loggers, and `ServiceTestCase` for testing HTTP API endpoints.
- **[Database Operators (`aloha.db`)](references/db.md)**: Secure DB operations through SQLAlchemy-backed operators (e.g. `PostgresOperator`), with password resolution via `PasswordVault`.
- **[Binary Compilation (`aloha compile`)](references/compile.md)**: Compiling normal `.py` files into binary dynamic library files using Cython for intellectual property protection.

---

## 3. Running Your `aloha`-based Application

Your application's main entry point should be a function (e.g., `main()`) within a module inside the `src/` directory.

### Running with `src/main.py`

`src/main.py` acts as a generic module runner. Run modules using:

```bash
python3 src/main.py <module_path>.<function_name>
```

**Example**:

```bash
python3 src/main.py my_app.main
```

This command resolves and executes the `main()` function in `src/my_app/main.py`.

---

## 4. Compiling Code into Binary

For IP protection, you can build your package into compiled dynamic library files (such as `.so` files on Linux/macOS) using Cython.

### Compilation Command

```bash
aloha compile --base=<source_dir> --dist=<output_dir> --keep='<files_to_keep>'
```

For full instructions, parameter reference, and package structural requirements (e.g. `__init__.py` usage), see the **[Binary Compilation reference](references/compile.md)**.

---

## 5. Summary of Advanced Best Practices

- **Configuration Isolation**: Keep config files modular by splitting environment configurations (e.g., `deploy-DEV.conf`, `deploy-PROD.conf`) and loading them using HOCON `include` syntax in `main.conf`.
- **Concurrency Logging Safety**: Avoid standard `FileHandler` in parallel/multi-process tasks; always use `aloha.logger.LOG` or named loggers from `get_logger()`.
- **Database Credentials**: Never hardcode passwords in config files. Configure them to resolve dynamically through the `PasswordVault`.
