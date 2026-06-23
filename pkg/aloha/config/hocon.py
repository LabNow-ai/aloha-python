from attrdict import AttrDict
from pyhocon import ConfigFactory


def load_config_from_hocon(config_file):
    """
    Load configuration from a single HOCON file.
    
    :param config_file: Path to the HOCON configuration file
    :return: Configuration as an ordered dictionary
    """
    config = ConfigFactory.parse_file(config_file).as_plain_ordered_dict()
    return config


def load_config_from_hocon_files(config_files: list, base_dir: str):
    """
    Load configuration from multiple HOCON files.
    
    Combines multiple HOCON files using include directives and returns
    the result as an AttrDict for attribute-style access.
    
    :param config_files: List of HOCON configuration file names
    :param base_dir: Base directory for resolving relative paths
    :return: Configuration as an AttrDict object
    """
    s = []
    for config_file in config_files:
        f = 'include required("%s")' % config_file
        s.append(f)
    f = '\n'.join(s)

    config = ConfigFactory.parse_string(content=f, basedir=base_dir).as_plain_ordered_dict()
    return AttrDict(config)
