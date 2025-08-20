from dataclasses import dataclass
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


@dataclass
class Config:
    """
    The config class. Use `Config.from_file` to init a new one.

    Vars:
        templates: code templates
        default_template: index of default template, -1 if not set
        parse_problem_md: whether store `problem.md` when parsing
        gen_after_parse: whether gen a template after parse
        host: codeforces host url
        root_name: the folder name under ~/, default 'cf'
        submit_cpp_std: preferred cpp version, could be cpp17, cpp20, cpp23
        race_open_url: url suffix to open in browser, default '/problems'
        race_delay_parse: seconds to delay parse after the race start (to avoid network congestion)
        race_link_sub_problem: whether use hard link to bind multiple problem files into one
    """
    
    templates: list[CodeTemplate]
    default_template: int
    parse_problem_md: bool
    gen_after_parse: bool
    host: str
    root_name: str
    submit_cpp_std: str
    race_open_url: str
    race_delay_parse: int
    race_link_sub_problem: bool
    _config_file: Path

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
            parse_problem_md=cfg.get('parse_problem_md', False),
            gen_after_parse=cfg.get('gen_after_parse', True),
            host=cfg.get('host', 'https://codeforces.com'),
            root_name=cfg.get('root_name', 'cf'),
            submit_cpp_std=cfg.get('submit_cpp_std', 'cpp17'),
            race_open_url=cfg.get('race_open_url', '/problems'),
            race_delay_parse=cfg.get('race_delay_parse', 3),
            race_link_sub_problem=cfg.get('race_link_sub_problem', True),
            _config_file=path,
        )

    def save(self):
        """ Save to json file (at ~/.pyforces/config.json). """
        cfg = {
            'templates': [{'path': str(t.path), 'name': t.name} for t in self.templates],
            'default_template': self.default_template,
            'parse_problem_md': self.parse_problem_md,
            'gen_after_parse': self.gen_after_parse,
            'host': self.host,
            'root_name': self.root_name,
            'submit_cpp_std': self.submit_cpp_std,
            'race_open_url': self.race_open_url,
            'race_delay_parse': self.race_delay_parse,
            'race_link_sub_problem': self.race_link_sub_problem,
        }
        with self._config_file.open('w') as fp:
            json.dump(cfg, fp, indent=4)
