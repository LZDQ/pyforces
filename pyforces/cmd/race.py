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

from pyforces.utils import contest_type_from_id

logger = getLogger(__name__)


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

    if cfg.race_delay_parse:
        print(f"Delaying parsing")
        countdown_bar(mins=0, secs=cfg.race_delay_parse)

    print("Parsing examples")
    problem_count = cln.parse_problem_count(url_contest)
    print(f"Found {problem_count} problems")
    for problem_idx in ascii_uppercase[:problem_count]:
        problem_path = contest_path / problem_idx.lower()
        problem_path.mkdir(exist_ok=True)
        os.chdir(problem_path)
        try:
            print(f"Parsing {problem_idx}")
            do_parse(cfg, cln)  # it takes accounts of gen_after_parse
        except:
            # Fallback: if parse failed, still generate template
            print(f"Couldn't parse sample testcases of {problem_idx}")
            if cfg.gen_after_parse:
                do_gen(cfg)

