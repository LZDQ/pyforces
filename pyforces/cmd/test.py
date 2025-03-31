import os
from argparse import Namespace
from pathlib import Path
from pyforces.cf.execute import TraditionalExecutor
from pyforces.utils import get_current_cpp_file


def do_test(args: Namespace):
    idx = 1
    if args.file:
        source_file = args.file
    else:
        source_file = get_current_cpp_file()
        if not source_file:
            print(f"Please test with  -f <file>")
            return
    if source_file.suffix != '.cpp':
        print("Other languages are not supported yet ><")
        return

    executable = str(source_file.parent / source_file.stem)
    if os.name == 'nt':  # Windows
        executable += '.exe'

    executor = TraditionalExecutor(
        executable,
        shell=False,
        time_limit=2,  # TL and ML are defaults now, doesn't affect small sample testcases
        memory_limit=512*1024*1024,
    )
    while True:
        in_file = Path(f"in{idx}.txt")
        ans_file = Path(f"ans{idx}.txt")
        if not in_file.is_file() or not ans_file.is_file():
            break
        with in_file.open() as fp_in, ans_file.open() as fp_ans:
            result = executor.execute(fp_in, fp_ans)
        if result.passed:
            print(f"#{idx} Passed...  {result.execution_time:.2f}s, {result.peak_memory/1024/1024:.2f}MB")
            if result.memory_exceeded:
                print(f"...But memory exceeded")
        else:
            print(f"#{idx} Failed... {result.reason}")
        idx += 1

    if idx == 1:
        print("No testcases found, please parse them first")


