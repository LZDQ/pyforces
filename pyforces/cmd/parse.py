from argparse import Namespace
from pyforces.cmd.gen import do_gen
from pyforces.config import Config
from pyforces.client import Client
from pyforces.utils import get_current_contest_type_id_problem_id


def do_parse(cfg: Config, cln: Client, url: str | None = None):
    """ Parse sample testcases under the current directory. """
    try:
        contest_type, contest_id, problem_id = get_current_contest_type_id_problem_id()
        url = url or f"{cfg.host}/{contest_type}/{contest_id}/problem/{problem_id}"
        testcases = cln.parse_testcases(url)
        for idx, (input, answer) in enumerate(testcases):
            with open(f"in{idx+1}.txt", "w") as fp:
                print(input, file=fp)
            with open(f"ans{idx+1}.txt", "w") as fp:
                print(answer, file=fp)
        print(f"Parsed {len(testcases)} testcases")
    except:
        print(f"Couldn't parse testcases of {contest_id}/{problem_id}")

    if cfg.gen_after_parse:
        do_gen(cfg)
