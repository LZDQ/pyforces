from argparse import Namespace
import os
from pathlib import Path

from countdown.countdown import time
from pyforces.client import Client
from pyforces.config import Config
from pyforces.utils import get_current_contest_problem_id, get_current_cpp_file
import random


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
    sub_id = cln.submit(
        url=f"{cfg.host}/contest/{contest_id}/submit",
        problem_id=problem_id,
        program_type_id=program_type_id,
        source_file=source_file,
        track=args.track,
    )
    if args.track:
        if sub_id is None:
            print("Failed to get submission id")
            return
        print(f"Watching submission {sub_id}")
        url = f"{cfg.host}/contest/{contest_id}/submission/{sub_id}"
        while True:
            status = cln.parse_status(url)
            os.system('clear' if os.name == 'posix' else 'cls')
            print(status)
            if not status.startswith(["Running", "Pending"]):
                break
            time.sleep(args.poll)



