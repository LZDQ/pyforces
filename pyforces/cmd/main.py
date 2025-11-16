from argparse import ArgumentParser, BooleanOptionalAction
import logging
import os
from pathlib import Path
import colorlog
from datetime import datetime

from pyforces.client import Client
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
Configure the logging level (INFO, ERROR, etc).
Also controlled by environment variable LOG_LEVEL, but argument takes precedence.
                        """,)
    # Update in v0.4.2: provide useful help message if subcommand is not provided
    subparsers = parser.add_subparsers(dest='subcommand')

    # config
    config_parser = subparsers.add_parser(
        'config',
        description="Login and configure pyforces."
    )
    # config_parser.add_argument('config_subcommand', nargs='?')

    # race
    race_parser = subparsers.add_parser('race', usage="""
pyforces race <contest_id>

For example, "pyforces race 1234" will countdown until the contest starts,
and then open the url and parse the testcases for each problem under ~/cf/contest/1234/
    """.strip())
    race_parser.add_argument('contest_id', type=int)
    race_parser.add_argument('-d', '--dir', type=Path, help="""
(For customization) a directory to put the problems into, like "./1234/"
    """)

    # gen
    gen_parser = subparsers.add_parser('gen')
    gen_parser.add_argument('name', type=str, nargs='?', help="The template's name")

    # parse
    parse_parser = subparsers.add_parser('parse', description="""
Parse current problem's testcases.
    """)
    parse_parser.add_argument('--url', type=str, help="""
(For customization) the problem's URL, for example "https://codeforces.com/contest/2092/problem/A"
    """)

    # test
    test_parser = subparsers.add_parser('test', usage="""
pyforces test [options]

Test the solution against each pair of [input, answer] ([in1.txt, ans1.txt], etc.).
Defaults to use the current directory's name + ".cpp" (like "a.cpp" if in directory "a").
If you want to use other files or custom command plz use --file or --shell
    """.strip())
    test_parser.add_argument('-f', '--file', type=Path, help="""
The source file (like a.cpp).
For .cpp files, will get the executable file's name by source file, and execute it.
For .py files, will use the current interpreter to run the file.
For other files, consider --shell
    """)
    test_parser.add_argument('--shell', type=str, help="""
(For customization) a shell string to run the solution.
For example, 'java a.java'
    """)
    test_parser.add_argument('--poll', action=BooleanOptionalAction, default=True, help="""
Whether use psutil to poll and track memory usage. If false, will use 
subprocess.run instead.
    """)
    test_parser.add_argument("--time-limit", type=float, default=2.0, help="""
Time limit in seconds. Can be float. (default: 2.0)
    """)
    test_parser.add_argument("--memory-limit", type=str, default="512M", help="""
Memory limit in bytes or K, M, G. (default: 512M)
"128m" is 128*1024*1024 bytes;
"2G" is 2*1024*1024*1024 bytes;
"998244353" is 998244353 bytes (about 952M).
Unit can be both lowercase or uppercase.
    """)

    # submit
    submit_parser = subparsers.add_parser('submit', usage="""
pyforces submit [options]

Defaults to submit the current directory's name + ".cpp" (like "a.cpp" if in directory "a").
    """.strip())
    submit_parser.add_argument('-f', '--file', type=Path, help="""
Source code file to submit, like "a.cpp"
    """)
    submit_parser.add_argument('--program-type-id', type=int, help="""
If you want to submit languages other than C++, set this to the program type id
of your language.  To view the value, right-click the drop down menu in your browser.
For example, PyPy 3.10 has value 70. """)
    submit_parser.add_argument('--track', action=BooleanOptionalAction, default=True, help="""
Whether track submission status.
    """)
    submit_parser.add_argument('--poll', type=float, required=False, help="""
If set, use this polling interval (in seconds) instead of websocket to receive updates.
    """)
    submit_parser.add_argument('--url', type=str, help="""
(For customization) the URL to POST data, for example "https://codeforces.com/contest/1234/submit"
    """)
    submit_parser.add_argument('--problem-id', type=str, help="""
(For customization) the problem id to POST, like A, B, C, D1, D2
    """)
    submit_parser.add_argument('--strip-comment', action='store_true', help="""
Whether strip all comments before submitting (only support cpp files)
    """)

    args = parser.parse_args()

    # v0.4.2: If no subcommand is given, print the help message with examples and exit.
    if args.subcommand is None:
        parser.print_usage()
        print("\nExamples:")
        print("  pyforces config      # First-time setup for login and templates.")
        print("  pyforces race 2092   # Prepare for a contest.")
        print("  pyforces test        # Test your code against sample cases (in the current directory).")
        print("  pyforces submit      # Submit your solution.")
        print("\nUse 'pyforces <command> --help' for more details on a specific command.")
        return

    # Ensure dir ~/.pyforces exists
    root_cfg = Path.home() / '.pyforces'
    if not root_cfg.is_dir():
        root_cfg.mkdir()

    # Colorful console + file logging
    handler_console = colorlog.StreamHandler()
    handler_console.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s[%(levelname)s] %(name)s: %(message)s'))
    handler_console.setLevel(args.log_level.upper())
    logs_dir = root_cfg / 'logs'
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / datetime.today().strftime('%Y-%m-%d.log')
    handler_logfile = logging.FileHandler(log_file)
    handler_logfile.setLevel(logging.DEBUG)
    handler_logfile.setFormatter(logging.Formatter(
        '%(asctime)s - [%(levelname)s] %(name)s: %(message)s'))
    logging.basicConfig(handlers=[
        handler_console, handler_logfile
    ], level=logging.DEBUG)
    logging.debug("Start at %s with args %s", Path.cwd(), args)


    # Init config, reload web session (cookies)
    cfg = Config.from_file(root_cfg / 'config.json')
    cln = Client.from_path(root_cfg)
    
    match args.subcommand:
        case 'config':
            do_config(cfg, cln)
        case 'race':
            do_race(cfg, cln, args)
        case 'gen':
            do_gen(cfg, args.name)
        case 'parse':
            do_parse(cfg, cln, args.url)
        case 'test':
            do_test(args)
        case 'submit':
            do_submit(cfg, cln, args)

