import os

from attrdict import AttrDict
from pyhocon import ConfigFactory
from pyhocon.config_parser import ConfigParser
from pyhocon.config_tree import ConfigTree, ConfigValues
from pyhocon.exceptions import ConfigSubstitutionException


# Monkeypatch ConfigParser._fixup_self_references to prevent "OrderedDict mutated during iteration"
# error on Python 3.13+ when resolving self-referential environment overrides.
@classmethod
def patched_fixup_self_references(cls, config, accept_unresolved=False):
    if isinstance(config, ConfigTree) and config.root:
        for key in list(config.keys()):  # Use list to avoid mutation error during iteration
            history = config.history.get(key)
            if not history:
                continue
            previous_item = history[0]
            for current_item in history[1:]:
                for substitution in cls._find_substitutions(current_item):
                    prop_path = ConfigTree.parse_key(substitution.variable)
                    if len(prop_path) > 1 and config.get(substitution.variable, None) is not None:
                        continue
                    if prop_path[0] == key:
                        if isinstance(previous_item, ConfigValues) and not accept_unresolved:
                            raise ConfigSubstitutionException(
                                "Property {variable} cannot be substituted. Check for cycles.".format(
                                    variable=substitution.variable
                                )
                            )
                        else:
                            value = previous_item if len(prop_path) == 1 else previous_item.get(".".join(prop_path[1:]))
                            _, _, current_item = cls._do_substitute(substitution, value)
                previous_item = current_item

            if len(history) == 1:
                for substitution in cls._find_substitutions(previous_item):
                    prop_path = ConfigTree.parse_key(substitution.variable)
                    if len(prop_path) > 1 and config.get(substitution.variable, None) is not None:
                        continue
                    if prop_path[0] == key:
                        value = os.environ.get(key)
                        if value is not None:
                            cls._do_substitute(substitution, value)
                            continue
                        if substitution.optional:
                            cls._do_substitute(substitution, None)


# Fix: https://github.com/chimpler/pyhocon/pull/348 , the function and fix can be remove after this PR merged.
ConfigParser._fixup_self_references = patched_fixup_self_references


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
    f = "\n".join(s)

    config = ConfigFactory.parse_string(content=f, basedir=base_dir).as_plain_ordered_dict()
    return AttrDict(config)
