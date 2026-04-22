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

Sometimes you need to compile Python source code into binary libraries to protect source code.

Aloha helps you build Python source code into binaries using `Cython`:

```bash
aloha compile --base=./app --dist=./build --keep='main.py'
```

Available options:

- `--base`: root folder that includes source code to build
- `--dist`: (default=`build`) target folder for binary code
- `--exclude`: files/folders to exclude (use multiple times for multiple paths)
- `--keep`: source files to keep as-is instead of converting to dynamic libraries (use multiple times)
