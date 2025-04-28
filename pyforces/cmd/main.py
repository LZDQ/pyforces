from argparse import ArgumentParser, BooleanOptionalAction
import logging
import os
from pathlib import Path

from pyforces.client import Client, CloudscraperClient
from pyforces.cmd.config import do_config
from pyforces.cmd.gen import do_gen
from pyforces.cmd.parse import do_parse
from pyforces.cmd.race import do_race
from pyforces.cmd.submit import do_submit
from pyforces.cmd.test import do_test
from pyforces.config import Config

def main():
    # Parse command line arguments
    description = """
Welcome to pyforces! Parse, test, submit, make you blazingly fast!
    """.strip()
    parser = ArgumentParser(prog='pyforces', description=description)
    parser.add_argument('--log-level', type=str,
                        default=os.environ.get('LOG_LEVEL', 'WARNING'),
                        help="""
Configure the logging level (INFO, ERROR, etc.). 
Also controlled by environment variable LOG_LEVEL, but argument takes precedence.
                        """,)
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # config
    config_parser = subparsers.add_parser('config')
    # config_parser.add_argument('config_subcommand', nargs='?')

    # race
    race_parser = subparsers.add_parser('race')
    race_parser.add_argument('contest_id', type=int)

    # gen
    gen_parser = subparsers.add_parser('gen')
    gen_parser.add_argument('name', type=str, help="The template's name")

    # parse
    parse_parser = subparsers.add_parser('parse')

    # test
    test_parser = subparsers.add_parser('test')
    test_parser.add_argument('-f', '--file', type=Path, help="""
The source file (like a.cpp). For cpp files, pyforces will get the executable file's name by source file,
and execute it.  For py files, pyforces will use the current interpreter to run the file.
    """)
    test_parser.add_argument('--poll', action=BooleanOptionalAction, default=True, help="""
Whether use psutil to poll and track memory usage. Default is true. If false, will use 
subprocess.run instead.
    """)

    # submit
    submit_parser = subparsers.add_parser('submit')
    submit_parser.add_argument('-f', '--file', type=Path)
    submit_parser.add_argument('--program-type-id', type=int, help="""
If you want to submit languages other than C++, set this to the program type id
of your language.  To view the value, right-click the drop down menu in your browser.
For example, PyPy 3.10 has value 70. """)
    submit_parser.add_argument('--track', action=BooleanOptionalAction, default=True, help="""
Whether track submission status.
    """)
    submit_parser.add_argument('--poll', type=float, required=False, help="""
If set, use polling instead of websocket to receive updates.
    """)
    
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())

    # Ensure dir ~/.pyforces exists
    root_cfg = Path.home() / '.pyforces'
    if not root_cfg.is_dir():
        root_cfg.mkdir()

    # Init config, reload web session (cookies)
    cfg = Config.from_file(root_cfg / 'config.json')
    cln = CloudscraperClient.from_path(root_cfg)
    
    match args.subcommand:
        case 'config':
            do_config(cfg, cln)
        case 'race':
            do_race(cfg, cln, args.contest_id)
        case 'gen':
            do_gen(cfg, args.name)
        case 'parse':
            do_parse(cfg, cln)
        case 'test':
            do_test(args)
        case 'submit':
            do_submit(cfg, cln, args)

