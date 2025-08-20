from argparse import Namespace
import os
from pathlib import Path
from pyforces.client import Client
from pyforces.cmd.gen import do_gen
from pyforces.cmd.parse import do_parse
from pyforces.config import Config
from countdown import countdown as countdown_bar
import webbrowser
from string import ascii_uppercase
from logging import getLogger
from tempfile import TemporaryDirectory

from pyforces.utils import contest_type_from_id

logger = getLogger(__name__)


def force_link(src, dest):
    # https://stackoverflow.com/a/58957613/22255633
    with TemporaryDirectory(dir=os.path.dirname(dest)) as d:
        tmpname = os.path.join(d, "foo")
        os.link(src, tmpname)
        os.replace(tmpname, dest)

def do_race(cfg: Config, cln: Client, args: Namespace):
    contest_id = args.contest_id
    if cfg.gen_after_parse and cfg.default_template == -1:
        logger.warning("No default template, will not generate")

    contest_type = contest_type_from_id(contest_id)
    contest_path = args.dir or Path.home() / cfg.root_name / contest_type / str(contest_id)
    contest_path.mkdir(exist_ok=True, parents=True)

    url_contest = f"{cfg.host}/{contest_type}/{contest_id}"
    countdown = cln.parse_countdown(url_contest)
    if countdown:
        h, m, s = countdown
        countdown_bar(mins=h*60+m, secs=s)

    if cfg.race_open_url:
        webbrowser.open(url_contest + cfg.race_open_url)

    if countdown and cfg.race_delay_parse:
        print(f"Delaying parsing")
        countdown_bar(mins=0, secs=cfg.race_delay_parse)

    print("Parsing examples")
    problem_indices = cln.parse_problem_indices(url_contest)
    print(f"Found {len(problem_indices)} problems:")
    print('\n'.join(problem_indices))
    for idx in problem_indices:
        problem_path = contest_path / idx.lower()
        problem_path.mkdir(exist_ok=True)
        os.chdir(problem_path)
        try:
            print(f"Parsing {idx}")
            do_parse(cfg, cln)  # it takes accounts of gen_after_parse
        except Exception as e:
            logger.exception(e)

        if cfg.gen_after_parse and cfg.default_template != -1 and \
                cfg.race_link_sub_problem and len(idx) == 2 and idx[1] in '23456789':
            try:
                # Try hard link to previous file (and replace the current one)
                prev_idx = idx[0] + str(int(idx[1]) - 1)
                prev_file = contest_path / prev_idx.lower() / \
                    (prev_idx.lower() + cfg.templates[cfg.default_template].path.suffix)
                curr_file = contest_path / idx.lower() / \
                    (idx.lower() + cfg.templates[cfg.default_template].path.suffix)
                logger.info('Hard linking %s to %s', curr_file, prev_file)
                force_link(prev_file, curr_file)
            except Exception as e:
                logger.exception(e)

