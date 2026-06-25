# Python Binary Compilation Module (`aloha compile`)

The `aloha compile` (or `python -m aloha.script.compile`) utility compiles Python source code (`.py`) into platform-specific compiled extension libraries (such as `.so` on Linux/macOS or `.pyd` on Windows) using Cython. This process helps protect intellectual property by hiding implementation details and preventing direct inspection of source code.

## 1. CLI Command Usage

To compile your application, run:

```bash
aloha compile --base=<source_dir> --dist=<output_dir> --keep='<files_to_keep>'
```

### Example
```bash
aloha compile --base=./src --dist=./dist_build --keep='main.py'
```

---

## 2. Compilation Workflow & Logic

Under the hood, `aloha compile` executes the following steps:

1. **Source Discovery**: Scans the source directory specified by `--base` (defaults to the current working directory).
2. **Filter & Skip**: Skips hidden files/directories (starting with `.`), the target `--dist` folder, and paths specified by `--exclude`.
3. **Asset Copying**: Copies all non-Python files (e.g. configurations, static assets) as-is to the target structure.
4. **Cythonization**:
   - Converts normal `.py` files into C files.
   - Compiles these C files into platform-native dynamic library files (using parallel compilation on multiple CPU threads).
   - Skips `__init__.py` files (they are always copied as plain Python files to maintain package structure).
   - Skips files specified in `--keep` (they remain as plain `.py` files).
5. **Temporary Storage & Final Cleanup**: Writes temporary intermediate files to `/tmp/build/<project_folder_name>`, then moves the final compiled outputs to `--dist` and deletes the temporary files.

---

## 3. Important Caveats & Best Practices

- **Cython Prerequisite**: Cython must be installed in your environment prior to running the command:
  ```bash
  pip install Cython
  ```
- **`__init__.py` Requirement**: All directories acting as Python submodules/packages **must** contain an `__init__.py` file. If a directory lacks `__init__.py`, the compiled extension files under it will be incorrectly placed in the root of the output directory.
- **Empty Output Directory**: The folder path specified by `--dist` must either not exist or be completely empty. The compilation script will raise an error if the directory contains existing files to prevent accidental overwrites.
- **Excluded files**: You can pass one or more file patterns to `--exclude` to bypass compile/copy of test suites, temporary files, or local dev tools.

---

## 4. CLI Parameter Reference

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--base` | string | `./` | Root folder containing the Python source code to compile. |
| `--dist` | string | `build` | Destination directory where the final binary files and copied assets will be placed. |
| `--exclude` | string list | `()` | A list of file or folder path glob patterns to exclude from being copied or compiled. |
| `--keep` | string list | `()` | A list of specific `.py` files to keep as plain Python source code instead of compiling. |
