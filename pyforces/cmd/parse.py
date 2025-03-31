from pyforces.cmd.gen import do_gen
from pyforces.config import Config
from pyforces.client import Client
from pyforces.utils import get_current_contest_problem_id


def do_parse(cfg: Config, cln: Client):
    """ Parse sample testcases under the current directory. """
    contest_id, problem_id = get_current_contest_problem_id()
    testcases = cln.parse_testcases(f"{cfg.host}/contest/{contest_id}/problem/{problem_id}")
    for idx, (input, answer) in enumerate(testcases):
        with open(f"in{idx+1}.txt", "w") as fp:
            fp.write(input)
        with open(f"ans{idx+1}.txt", "w") as fp:
            fp.write(answer)
    print(f"Parsed {len(testcases)} testcases")

    if cfg.gen_after_parse:
        do_gen(cfg)
