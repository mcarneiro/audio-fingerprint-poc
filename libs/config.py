import json
import os.path

CONFIG_DEFAULT_FILE = "config.json"
CONFIG_DEVELOPMENT_FILE = "config-development.json"


def get_config():
    """
    Load config from multiple files and return merged result.
    """
    defaultConfig = {
        "env": "unset",
        "log.level": "INFO",
        "log.file": "recognition.log",
        "log.format": "%(asctime)s %(processName)-10s %(message)s",
        "log.max_size": "1000000",
    }

    return merge_configs(
        defaultConfig,
        parse_config(CONFIG_DEFAULT_FILE),
        parse_config(CONFIG_DEVELOPMENT_FILE),
    )


def parse_config(filename):
    """
    Parse config from specific filename.
    Will return empty config if the file does not exist, or isn't readable.
    """
    config = {}

    if os.path.isfile(filename):
        f = open(filename, "r")
        config = json.load(f)
        f.close()

    return config


def merge_configs(*configs):
    """
    Merge multiple dicts into one.
    """
    z = {}

    for config in configs:
        z.update(config)

    return z
