import json
import os
import shutil
from pathlib import Path
from typing import Literal, Optional
import pickle
from logging import getLogger

logger = getLogger(__name__)

class CodeTemplate:
    """ Code template for generating a.cpp, b.cpp, etc. """
    
    def __init__(self,
                 path: Path | str,
                 name: str,
                 ):
        self.path = Path(path)
        self.name = name
    
    def generate(self, dest: Path | str):
        dest = Path(dest)
        if dest.exists():
            print(f"Destination exists, not generating template...")
            return
        shutil.copy(self.path, dest)


class Config:
    """
    The config class. Use `Config.from_file` to init a new one.

    Vars:
        templates: code templates
        default_template: index of default template, -1 if not set
        gen_after_parse: whether gen a template after parse
        host: codeforces host url
        root_name: the folder name under ~/, default 'pyforces'
        submit_cpp_std: preferred cpp version, could be cpp17, cpp20, cpp23
    """
    
    def __init__(
        self,
        templates: list[CodeTemplate],
        default_template: int,
        gen_after_parse: bool,
        host: str,
        root_name: str,
        submit_cpp_std: str,
        race_pre_sec: int,
        race_open_url: str,
        race_delay_parse: int,
        _config_file: Path,
    ):
        self.templates = templates
        self.default_template = default_template
        self.gen_after_parse = gen_after_parse
        self.host = host
        self.root_name = root_name
        self.submit_cpp_std = submit_cpp_std
        self.race_pre_sec = race_pre_sec
        self.race_open_url = race_open_url
        self.race_delay_parse = race_delay_parse
        self._config_file = _config_file

    @classmethod
    def from_file(cls, path: Path):
        """ Init a new config object from json file. """
        try:
            with path.open() as fp:
                cfg = json.load(fp)
        except FileNotFoundError:
            logger.info("Config file not found, will create one.")
            cfg = {}
        except json.JSONDecodeError:
            logger.error("Config file json decode error, this should not happen!")
            cfg = {}

        return cls(
            templates=[CodeTemplate(**kwargs) for kwargs in cfg.get('templates', [])],
            default_template=cfg.get('default_template', -1),
            gen_after_parse=cfg.get('gen_after_parse', True),
            host=cfg.get('host', 'https://codeforces.com'),
            root_name=cfg.get('root_name', 'pyforces'),
            submit_cpp_std=cfg.get('submit_cpp_std', 'cpp17'),
            race_pre_sec=cfg.get('race_pre_sec', 0),
            race_open_url=cfg.get('race_open_url', '/problems'),
            race_delay_parse=cfg.get('race_delay_parse', 3),
            _config_file=path,
        )

    def save(self):
        """ Save to json file (at ~/.pyforces/config.json). """
        cfg = {
            'templates': [{'path': str(t.path), 'name': t.name} for t in self.templates],
            'default_template': self.default_template,
            'gen_after_parse': self.gen_after_parse,
            'host': self.host,
            'root_name': self.root_name,
            'submit_cpp_std': self.submit_cpp_std,
            'race_pre_sec': self.race_pre_sec,
            'race_open_url': self.race_open_url,
            'race_delay_parse': self.race_delay_parse,
        }
        with self._config_file.open('w') as fp:
            json.dump(cfg, fp, indent=4)
