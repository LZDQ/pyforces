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

logger = getLogger(__name__)


def do_race(cfg: Config, cln: Client, contest_id: int):
    if cfg.gen_after_parse and cfg.default_template == -1:
        logger.warning("No default template set")

    url_contest = f"{cfg.host}/contest/{contest_id}"
    countdown = cln.parse_countdown(url_contest)
    if countdown:
        h, m, s = countdown
        countdown_bar(mins=h*60+m, secs=s-cfg.race_pre_sec)

    if cfg.race_open_url:
        webbrowser.open(url_contest + cfg.race_open_url)

    contest_path = Path.home() / cfg.root_name / 'contest' / str(contest_id)
    contest_path.mkdir(exist_ok=True, parents=True)

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
                try:
                    do_gen(cfg)
                except:
                    print(f"Couldn't generate template for {problem_idx}")


        

