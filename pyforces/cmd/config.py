from argparse import Namespace
import logging
import os.path
from typing import Optional
from getpass import getpass
from pathlib import Path
import json

from pyforces.client import Client, CloudscraperClient
from pyforces.config import CodeTemplate, Config
from pyforces.utils import input_index, input_y_or_n, parse_firefox_http_headers

def login_http_header(cfg: Config, cln: Client):
    if isinstance(cln, CloudscraperClient):
        print("Please follow the video tutorial and paste the HTTP header from Firefox:")
        s = ''
        while True:
            try:
                headers = json.loads(s)
                break
            except:
                s += input()
        headers = parse_firefox_http_headers(headers)
        cln.headers = headers
        cln.parse_csrf_token(cfg.host)
        cln.save()
    else:
        raise NotImplementedError()

def ensure_logged_in(cfg: Config, cln: Client):
    if isinstance(cln, CloudscraperClient):
        token1 = cln.csrf_token
        cln.parse_csrf_token(cfg.host)
        token2 = cln.csrf_token
        if token1 != token2:
            print("Csrf token mismatched, retrying...")
            cln.parse_csrf_token(cfg.host)
            token3 = cln.csrf_token
            if token2 != token3:
                print("Not logged in, please re-login.")
                login_http_header(cfg, cln)
            else:
                print("Logged in.")
        else:
            print("Already logged in.")
        cln.save()
    else:
        raise NotImplementedError()

def login_handle_passwd(cfg: Config, cln: Client):
    print("Note: password is hidden, just type it correctly.")
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
    if cfg.host.endswith('/'):
        cfg.host = cfg.host[:-1]
    cfg.save()

def do_config(cfg: Config, cln: Client):
    """ Interactive config. """
    
    options = [
        ('login with HTTP header', login_http_header),
        ('ensure logged in', ensure_logged_in),
        # ('login with username and password', login_handle_passwd),
        ('add a template', lambda cfg, cln: add_template(cfg)),
        ('delete a template', lambda cfg, cln: delete_template(cfg)),
        ('set default template', lambda cfg, cln: set_default_template(cfg)),
        ('set host domain', lambda cfg, cln: set_host_domain(cfg)),
    ]

    for i, opt in enumerate(options):
        print(f"{i}) {opt[0]}")
    idx = input_index(len(options))
    options[idx][1](cfg, cln)

