import os
from pathlib import Path
from typing import Dict, List, Optional
import pickle
import logging


class CodeTemplate:
    """ Code template for generating a.cpp, b.cpp, etc. """
    
    def __init__(self,
                 path: Path,
                 name: str,
                 ):
        self.path = path
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
                 folder_name: Dict[str, str],
                 config_file: Path,
                 ):
        self.templates = templates
        self.default_template = default_template
        self.gen_after_parse = gen_after_parse
        self.host = host
        self.folder_name = folder_name
        self._config_file = config_file
    
    @classmethod
    def from_file(cls, path: Path):
        """ Init a new config from file (with pickle). """
        try:
            with path.open() as fp:
                return pickle.load(fp)
        except FileNotFoundError:
            logging.info("Config file not found, will create one.")
            return cls(
                templates=[],
                default_template=-1,
                gen_after_parse=True,
                host='https://codeforces.com',
                folder_name={},
                config_file=path,
            )

    def save(self):
        """ Save to file (with pickle). """
        with self._config_file.open() as fp:
            pickle.dump(self, fp)
