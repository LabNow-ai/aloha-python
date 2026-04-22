# Common Tasks

## Test whether aloha is properly installed

```bash
aloha info
```

This displays package version information.

## Start a function from the main function entrypoint

```bash
aloha start package_name.module_name
# e.g.: aloha start app_common.debug
```

Note: this `module_name` **must** include a function named `main()`.

## Compile Python code into binary

Sometimes you need to distribute Python code without shipping the raw `.py` files. This command turns most Python modules into compiled extension libraries (`.so` files on Linux/macOS), which can help with source-code protection and reduce direct readability of implementation details.

Aloha uses `Cython` for this workflow:

```bash
aloha compile --base=./app --dist=./build --keep='main.py'
```

How it works:

1. Scan the source tree under `--base`.
2. Skip hidden folders, the output folder, excluded paths, `.pyc` files, and `.pyx` files.
3. Copy non-Python files directly into the target tree.
4. Convert regular `.py` modules into compiled extension modules.
5. Keep files listed in `--keep` as plain Python files.
6. Move the final build result into `--dist` and clean up intermediate Cython artifacts.

Notes:

- `__init__.py` files are copied as plain Python files.
- All python submodule folders MUST contain a `__init__.py` file, otherwise python files in this submodule/folder will be compiled and built to root folder.
- Files passed through `--keep` are not compiled.
- `Cython` must be installed first.
- The command writes a temporary build tree under `/tmp/build/<project-name>` before moving the result to `--dist`.

Available options:

- `--base`: root folder that includes source code to build
- `--dist`: (default=`build`) target folder for binary code
- `--exclude`: files/folders to exclude; pass one or more paths after the flag
- `--keep`: source files to keep as-is instead of converting to dynamic libraries; pass one or more paths after the flag
