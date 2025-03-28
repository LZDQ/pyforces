from argparse import ArgumentParser
import os
from pathlib import Path

from pyforces.client import Client, CloudscraperClient
from pyforces.cmd.config import do_config
from pyforces.config import Config

def main():
    # Ensure root dir ~/.pyforces exists
    root = Path.home() / '.pyforces'
    if not root.is_dir():
        root.mkdir()

    # Init config, reload web session (cookies)
    cfg = Config.from_file(root / 'config.pickle')
    cln = CloudscraperClient.from_file(root / 'cookies.txt')
    print(cln.cookies)
    
    # Parse command line arguments
    description = """
Welcome to pyforces! Parse, test, submit, make you blazingly fast!
    """.strip()
    parser = ArgumentParser(prog='pyforces', description=description)
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # config
    config_parser = subparsers.add_parser('config')
    # config_parser.add_argument('config_subcommand', nargs='?')

    # race
    race_parser = subparsers.add_parser('race')
    race_parser.add_argument('contest_id', type=int)

    # test
    test_parser = subparsers.add_parser('test')
    test_parser.add_argument('-f', '--file', type=Path)

    # submit
    submit_parser = subparsers.add_parser('submit')
    submit_parser.add_argument('-f', '--file', type=Path)
    
    args = parser.parse_args()
    match args.subcommand:
        case 'config':
            # TODO
            do_config(cfg=cfg, cln=cln)
        case 'race':
            pass
        case 'test':
            pass
        case 'submit':
            pass

