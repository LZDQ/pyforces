import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import pickle
import logging


class CodeTemplate:
    """ Code template for generating a.cpp, b.cpp, etc. """
    
    def __init__(self,
                 path: Path | str,
                 name: str,
                 ):
        self.path = Path(path)
        self.name = name

        # template = cls()
        # template.path = Path(input('Absolute path of the template file:\n'))
        # template.name = input('Name of this template:\n')
        # return template

class Config:
    """
    The config class. Use `Config.from_file` to init a new one.

    Vars:
        templates: code templates
        default_template: index of default template
        gen_after_parse: whether gen a template after parse
        host: codeforces host url
        folder_name: TODO
    """
    
    def __init__(self,
                 templates: List[CodeTemplate],
                 default_template: int,
                 gen_after_parse: bool,
                 host: str,
                 _config_file: Path,
                 ):
        self.templates = templates
        self.default_template = default_template
        self.gen_after_parse = gen_after_parse
        self.host = host
        self._config_file = _config_file
    
    @classmethod
    def from_file(cls, path: Path):
        """ Init a new config object from json file. """
        try:
            with path.open() as fp:
                cfg = json.load(fp)
        except FileNotFoundError:
            logging.info("Config file not found, will create one.")
            cfg = {}
        except json.JSONDecodeError:
            logging.error("Config file json decode error, this should not happen!.")
            cfg = {}

        return cls(
            templates=[CodeTemplate(**kwargs) for kwargs in cfg.get('templates', [])],
            default_template=cfg.get('default_template', -1),
            gen_after_parse=cfg.get('gen_after_parse', True),
            host=cfg.get('host', 'https://codeforces.com'),
            _config_file=path,
        )

    def save(self):
        """ Save to json file (at ~/.pyforces/config.json). """
        cfg = {
            'templates': [{'path': str(t.path), 'name': t.name} for t in self.templates],
            'default_template': self.default_template,
            'gen_after_parse': self.gen_after_parse,
            'host': self.host,
        }
        with self._config_file.open('w') as fp:
            json.dump(cfg, fp)
