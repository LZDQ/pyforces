from logging import getLogger
from pyforces.cmd.gen import do_gen
from pyforces.config import Config
from pyforces.client import Client
from pyforces.utils import get_current_contest_type_id_problem_id

logger = getLogger(__name__)

def do_parse(cfg: Config, cln: Client, url: str | None = None):
    """ Parse sample testcases under the current directory.
    If parse_problem_md is True, will also store `problem.md`. """
    try:
        contest_type, contest_id, problem_id = get_current_contest_type_id_problem_id()
        url = url or f"{cfg.host}/{contest_type}/{contest_id}/problem/{problem_id}"
        problem = cln.parse_problem(url)
        testcases = problem.testcases
        for idx, (input, answer) in enumerate(testcases):
            with open(f"in{idx+1}.txt", "w") as fp:
                print(input, file=fp)
            with open(f"ans{idx+1}.txt", "w") as fp:
                print(answer, file=fp)
        print(f"Parsed {len(testcases)} testcases")
        if cfg.parse_problem_md:
            with open("problem.md", "w") as fp:
                print(problem.problem_page.full_problem_statement(), file=fp)
            print("Stored problem statement into `problem.md`.")
    except Exception as e:
        print(f"Couldn't parse {contest_id}/{problem_id}")
        logger.exception(e)

    if cfg.gen_after_parse:
        do_gen(cfg)
