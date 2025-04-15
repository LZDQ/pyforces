import os
from argparse import Namespace
from pathlib import Path
import sys
from pyforces.cf.execute import TraditionalExecutor
from pyforces.utils import get_current_cpp_file
from logging import getLogger

logger = getLogger(__name__)


def do_test(args: Namespace):
    """
    test the source file against test cases.
    Most users only use cpp, so by default if the file is not specified, will
    list all cpp files and if there is only one, use that one; otherwise need to 
    specify --file
    """
    if args.file:
        source_file = args.file
    else:
        source_file = get_current_cpp_file()
        if not source_file:
            print(f"Please test with  -f <file>")
            return
        logger.info("Using source file %s", source_file)

    if source_file.suffix == '.cpp':
        executable = str(source_file.parent / source_file.stem)
        if os.name == 'nt':  # Windows
            executable += '.exe'

        logger.info("Using executable %s", executable)
        if not Path(executable).is_file():
            print(f"Executable {executable} not found, please compile first")
            return
        executor = TraditionalExecutor(
            executable,
            shell=False,
            time_limit=2,  # TL and ML are defaults now, doesn't affect small sample testcases
            memory_limit=512*1024*1024,
        )
    elif source_file.suffix == '.py':
        # use the current interpreter to run the py file
        logger.info("Using interpreter %s", sys.executable)
        executor = TraditionalExecutor(
            [sys.executable, source_file],
            shell=False,
            time_limit=2,
            memory_limit=512*1024*1024,
        )
    else:
        print("Other languages are not supported yet ><")
        return

    return_code = 0  # exit code to indicate whether passed
    idx = 1
    while True:
        in_file = Path(f"in{idx}.txt")
        ans_file = Path(f"ans{idx}.txt")
        if not in_file.is_file() or not ans_file.is_file():
            break
        with in_file.open() as fp_in, ans_file.open() as fp_ans:
            result = executor.execute(fp_in, fp_ans, args.poll)
        if result.passed:
            print(f"#{idx} Passed...  {result.execution_time:.2f}s",
                  f"{result.peak_memory/1024/1024:.2f}MB" if result.peak_memory and
                  result.peak_memory>0 else "")
            if result.memory_exceeded:
                # MLE, but don't change return_code
                print(f"...But memory exceeded")
        else:
            print(f"#{idx} Failed...  {result.reason}")
            return_code = result.return_code or 1  # exit the status code if RE, else 1
        idx += 1

    if idx == 1:
        print("No testcases found, please parse them first")
        return_code = 1
    
    if not args.poll and os.name == 'posix':
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            peak_memory = usage.ru_maxrss * 1024  # KB to B
            print(f"Peak memory usage <= {peak_memory/1024/1024:.2f}MB")
        except Exception as e:
            logger.warning("Failed to fetch maxrss: %s", e)

    if return_code:
        exit(return_code)

