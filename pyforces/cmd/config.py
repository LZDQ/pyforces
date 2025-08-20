from logging import getLogger
import os.path
from pathlib import Path
import json

from pyforces.client import Client
from pyforces.config import CodeTemplate, Config
from pyforces.utils import input_index, input_y_or_n, parse_firefox_http_headers

logger = getLogger(__name__)

def login_with_http_header(cfg: Config, cln: Client):
    if isinstance(cln, Client):
        print("Please follow the video tutorial and paste the HTTP header from Firefox:")
        s = ''
        while True:
            try:
                headers = json.loads(s)
                break
            except json.JSONDecodeError:
                s += input()
        headers = parse_firefox_http_headers(headers)
        cln.headers = headers
        cln.parse_csrf_token_and_handle(cfg.host)
        if cln.handle:
            print(f"Welcome {cln.handle} ><")
        else:
            print("Login failed ><")
        cln.save()
    else:
        raise NotImplementedError()

def ensure_logged_in(cfg: Config, cln: Client):
    if isinstance(cln, Client):
        cln.parse_csrf_token_and_handle(cfg.host)
        if cln.handle:
            print(f"Already logged in as {cln.handle}")
        else:
            print("Not logged in, please re-login.")
        cln.save()
    else:
        raise NotImplementedError()

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
    make_default = input_y_or_n("Make it default? [y/n]:\n")
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
        logger.warning("Removing default template")
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
    
def set_host_domain(cfg: Config):
    print(f"Current host domain: {cfg.host}")
    cfg.host = input("New host domain (don't forget the https://):\n")
    if cfg.host.endswith('/'):
        cfg.host = cfg.host[:-1]
    cfg.save()

def set_folder_name(cfg: Config):
    print(f"Current root folder name: {cfg.root_name}")
    new_name = input("New root folder name:\n")
    old_dir = Path.home() / cfg.root_name
    new_dir = Path.home() / new_name
    if old_dir.is_dir():
        if input_y_or_n(f"Move {old_dir} to {new_dir}? [Y/n]\n", default=True):
            old_dir.rename(new_dir)
            logger.info("Moved %s to %s", old_dir, new_dir)
    else:
        logger.info("Old dir %s not found, not creating %s", old_dir, new_dir)
    cfg.root_name = new_name
    cfg.save()

def set_cpp_std(cfg: Config):
    print(f"Current standard: {cfg.submit_cpp_std}")
    options = ['cpp17', 'cpp20', 'cpp23']
    for i, opt in enumerate(options):
        print(f"{i}) {opt}")
    cfg.submit_cpp_std = options[input_index(3)]
    cfg.save()

def config_parse(cfg: Config):
    print(f"Whether gen after parse?")
    print(f"Current value: {cfg.gen_after_parse}")
    cfg.gen_after_parse = input_y_or_n("New value", add_prompt=True, default=cfg.gen_after_parse)
    print(f"Whether store `problem.md` when `pyforces parse`?")
    print(f"Current value: {cfg.parse_problem_md}")
    cfg.parse_problem_md = input_y_or_n("New value", add_prompt=True, default=cfg.parse_problem_md)
    cfg.save()

def config_race(cfg: Config):
    print(f"What url to open?")
    print(f"Input / if u want to open the contest dashboard;")
    print(f"Input /problems if u want to open the complete problemset;")
    print(f"Input >< if u don't want to open anything;")
    print(f"Input empty if u don't want to change the value.")
    print(f"Current value: {cfg.race_open_url}")
    race_open_url = input(f"New value:\n")
    if race_open_url:
        if race_open_url == '><':
            cfg.race_open_url = ''
        else:
            cfg.race_open_url = race_open_url

    print(f"How many seconds do u want to delay the parsing (to avoid network congestion)?")
    print(f"Current value: {cfg.race_delay_parse}")
    race_delay_parse = input("New value (input empty line if u don't want to change it):\n")
    if race_delay_parse:
        try:
            race_delay_parse = int(race_delay_parse)
        except ValueError:
            print("Please input an integer.")
            return
        if race_delay_parse < 0:
            print("Please input a non-negative integer.")
            return
        cfg.race_delay_parse = race_delay_parse

    print(f"Do you want to link files? Link g2.cpp to g1.cpp so that you can continue on that.")
    print(f"Current value: {cfg.race_link_sub_problem}")
    cfg.race_link_sub_problem = input_y_or_n("New value", add_prompt=True, default=cfg.race_link_sub_problem)

    cfg.save()


def do_config(cfg: Config, cln: Client):
    """ Interactive config. """
    
    options = [
        ('login with HTTP header', login_with_http_header),
        ('ensure logged in', ensure_logged_in),
        # ('login with username and password', login_handle_passwd),
        ('add a template', lambda cfg, _: add_template(cfg)),
        ('delete a template', lambda cfg, _: delete_template(cfg)),
        ('set default template', lambda cfg, _: set_default_template(cfg)),
        ('set host domain', lambda cfg, _: set_host_domain(cfg)),
        ('set root folder name', lambda cfg, _: set_folder_name(cfg)),
        ('set C++ standard for submission', lambda cfg, _: set_cpp_std(cfg)),
        ('config parse', lambda cfg, _: config_parse(cfg)),
        ('config race', lambda cfg, _: config_race(cfg)),
    ]

    for i, opt in enumerate(options):
        print(f"{i}) {opt[0]}")
    idx = input_index(len(options))
    options[idx][1](cfg, cln)

