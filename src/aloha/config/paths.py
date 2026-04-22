import os
import sys
import warnings

__all__ = ("get_resource_dir", "get_config_dir", "get_current_module_dir", "get_project_base_dir", "path_join")


def path_join(*args) -> str:
    """
    Join path components and normalize the result.
    Performs path joining, user expansion, environment variable expansion,
    and conversion to absolute path.

    :param args: Path components to join
    :return: Normalized absolute path string
    """
    p = os.path.join(*args)
    p = os.path.expanduser(p)
    p = os.path.expandvars(p)
    p = os.path.abspath(p)
    return p


def get_resource_dir(*args) -> str:
    """
    Get the resource directory path.
    The resource directory is determined by:
    1. If DIR_RESOURCE environment variable is set, use it;
    2. Otherwise, default to 'resource' directory under current working directory.

    :param args: Additional path components to append to the resource directory
    :return: Resource directory path
    """
    dir_cwd = os.getcwd()
    dir_resource = os.environ.get("DIR_RESOURCE", "resource")
    return path_join(dir_cwd, dir_resource, *args)


def get_config_dir(*args) -> str:
    """
    Get the configuration directory path.
    The config directory is determined by:
    1. If DIR_CONFIG environment variable is set, use it;
    2. Otherwise, default to 'config' directory under resource directory.

    :param args: Additional path components to append to the config directory
    :return: Config directory path
    """
    dir_config = os.environ.get("DIR_CONFIG")
    dir_resource = get_resource_dir()
    if dir_config is None or len(dir_config.strip()) == 0:
        dir_config = "config"
    dir_config = path_join(dir_resource, dir_config, *args)
    return dir_config


def get_config_files() -> list:
    """
    Get a list of config files to parse. The base dir of config files should be specified by `get_config_dir()`.
    1. The function will look up the `FILES_CONFIG` environment variable to get a list of file names seperated by comma, if specified;
    2. In case `FILES_CONFIG` is not specified, the function will use the default config file;
    3. The default config file is determined by:
       (a) If environment variable `ENV_PROFILE` is defined, the entry file will be "main-{ENV_PROFILE}.conf"
       (b) If environment variable `ENV_PROFILE` is not defined, the entry config file will be "main.conf".
    :return: list of string, which are file names of config files
    """
    files_config = os.environ.get("FILES_CONFIG", None)
    if files_config is None:
        env_profile = os.environ.get("ENV_PROFILE", None)
        if env_profile is None:
            files_config = "main.conf"
        else:
            files_config = "main-%s.conf" % env_profile

    files = files_config.split(",")
    ret = []
    msgs = []
    for f in files:
        file = get_config_dir(f)
        if not os.path.exists(file):
            msgs.append("Expecting config file [%s] but it does not exists!" % file)
        else:
            print("  ---> Loading config file [%s]" % file, file=sys.stderr)
            ret.append(os.path.expandvars(f))
    if len(ret) == 0:
        msgs.append("No config files set properly, EMPTY config will be used!")

    if len(msgs) > 0:
        warnings.warn("\n".join(msgs))
    return ret


def get_current_module_dir(file_caller: str) -> str:
    """
    Get the directory containing the given module file.

    :param file_caller: Path to the module file (usually __file__)
    :return: Directory path of the module
    """
    dirs = file_caller.split(os.sep)
    return os.sep.join(dirs[:-1])


def get_project_base_dir(file_caller: str) -> str:
    """
    Get the project base directory by searching upwards for __init__.py.
    Starts from the given file path and moves up until a directory without
    __init__.py is found, indicating the project root.

    :param file_caller: Path to the starting file (usually __file__)
    :return: Project base directory path
    """
    dirs = file_caller.split(os.sep)

    dir_base = ""
    for i in range(len(dirs)):
        dir_base = os.sep.join(dirs[: -1 - i])
        file_init = path_join(dir_base, "__init__.py")
        if not os.path.exists(file_init):
            break
    return dir_base
