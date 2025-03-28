from argparse import Namespace
import logging
import os.path
from typing import Optional
from getpass import getpass
from pathlib import Path

from pyforces.client import Client
from pyforces.config import CodeTemplate, Config
from pyforces.utils import input_index, input_y_or_n

def login(cfg: Config, cln: Client):
    username = input('Username: ')
    password = getpass()
    cln.login(cfg.host, username, password)
    cln.save()

def add_template(cfg: Config):
    # TODO: add path completion
    path = Path(os.path.expanduser(input("Path to your template file (~/ allowed):\n")))
    if not path.is_file():
        print("File doesn't exist, exiting")
        return
    if path.suffix:
        name = input(f"Name (input empty line to use file extension \"{path.suffix[1:]}\"):\n")
        name = name or path.suffix[1:]
    else:
        name = input(f"Name:\n")
    if not name:
        print("Name cannot be empty, exiting")
        return
    make_default = input_y_or_n("Make it default? (y/n):\n")
    if make_default:
        cfg.default_template = len(cfg.templates)
    cfg.templates.append(CodeTemplate(path=path, name=name))
    cfg.save()

def delete_template(cfg: Config):
    if not cfg.templates:
        print("No templates, exiting")
        return
    for i, template in enumerate(cfg.templates):
        print(f"{i}: {template.name}\t{template.path}")
    idx = input_index(len(cfg.templates))
    if idx == cfg.default_template:
        logging.warning("Removing default template")
        cfg.default_template = -1  # Set none of the templates to be default
    elif idx < cfg.default_template:
        cfg.default_template -= 1
    del cfg.templates[idx]
    cfg.save()

def set_default_template(cfg: Config):
    if not cfg.templates:
        print("No templates, exiting")
        return
    for i, template in enumerate(cfg.templates):
        print('*' if i==cfg.default_template else ' ', f"{i}: {template.name}\t{template.path}")
    print(f"Current default template: {cfg.default_template}")
    idx = input_index(len(cfg.templates), prompt="Index of new default template:\n")
    cfg.default_template = idx
    cfg.save()
    
def set_gen_after_parse(cfg: Config):
    print(f"Current state: {cfg.gen_after_parse}")
    cfg.gen_after_parse = input_y_or_n("New value (y/n):\n")
    cfg.save()

def set_host_domain(cfg: Config):
    print(f"Current host domain: {cfg.host}")
    cfg.host = input("New host domain (don't forget the https://):\n")
    cfg.save()

def set_folders_name(cfg: Config):
    print("Still working on this ><")

def do_config(cfg: Config, cln: Client):
    """ Interactive config. """

    print("""
0) login
1) add a template
2) delete a template
3) set default template
4) set whether run gen after parse
5) set host domain
6) set folders' name
    """.strip())
    idx = input_index(8)
    match idx:
        case 0:
            login(cfg, cln)
        case 1:
            add_template(cfg)
        case 2:
            delete_template(cfg)
        case 3:
            set_default_template(cfg)
        case 4:
            set_gen_after_parse(cfg)
        case 5:
            set_host_domain(cfg)
        case 6:
            set_folders_name(cfg)

