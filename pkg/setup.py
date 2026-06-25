import os
import shutil
from datetime import datetime

from setuptools import setup

# Get directory containing this setup.py
base_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Resolve README.md presence
# In Python package builds, README.md is required to be in the same directory.
# If it is missing (e.g., built locally without github workflow cp command), we copy it from the root directory.
readme_path = os.path.join(base_dir, "README.md")
root_readme = os.path.join(base_dir, "..", "README.md")
if not os.path.exists(readme_path) and os.path.exists(root_readme):
    shutil.copyfile(root_readme, readme_path)

# 2. Dynamic Version Generation
# Writes the version to aloha/_version.py using the current timestamp.
_t = datetime.now()
_version = "%s.%02d%02d.%02d%02d" % (_t.year, _t.month, _t.day, _t.hour, _t.minute)

version_file_path = os.path.join(base_dir, "aloha", "_version.py")
with open(version_file_path, "wt") as fp:
    fp.write('__version__ = "%s"\n' % _version)

# 3. Trigger setup (reads configuration from pyproject.toml)
setup()
