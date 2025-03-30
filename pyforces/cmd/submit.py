from argparse import Namespace
from pathlib import Path
from pyforces.client import Client
from pyforces.config import Config
from pyforces.utils import get_current_contest_problem_id, get_current_cpp_file


def do_submit(cfg: Config, cln: Client, args: Namespace):
    """ (Non-interactive) submit.
    Normal C++ users don't need to pass any arguments.
    Other languages users need to pass both --file and --program-type-id.
    """
    if args.file:
        source_file = args.file
    else:
        source_file = get_current_cpp_file()
        if not source_file:
            print(f"Please submit with  -f <file>")
            return

    if args.program_type_id:
        program_type_id = args.program_type_id
    else:
        program_type_id = {
            'cpp17': 54,
            'cpp20': 89,
            'cpp23': 91,
        }[cfg.submit_cpp_std]

    contest_id, problem_id = get_current_contest_problem_id()
    cln.submit(
        url=f"{cfg.host}/contest/{contest_id}/submit",
        problem_id=problem_id,
        program_type_id=program_type_id,
        source_file=source_file,
    )

