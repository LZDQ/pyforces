import os
from argparse import Namespace
from pathlib import Path
import sys
from colorama import Fore, Back, Style
from pyforces.cf.execute import TraditionalExecutor
from pyforces.utils import get_current_cpp_file, parse_human_bytesize
from logging import getLogger

logger = getLogger(__name__)


def do_test(args: Namespace):
    """ Test the source file against test cases.
    Most users only use cpp and the filename is cwd's name + ".cpp", so this is the default.
    """
    time_limit = args.time_limit
    memory_limit = parse_human_bytesize(args.memory_limit)
    if args.shell:
        if args.file:
            print("Cannot pass both --shell and --file")
            return
        executor = TraditionalExecutor(
            shell=args.shell, time_limit=time_limit, memory_limit=memory_limit
        )
    else:  # Get the execution args from source file
        if args.file:
            source_file = args.file
        else:
            source_file = get_current_cpp_file()
            if not source_file:
                print("Please test with  -f <file>")
                return
            logger.info('Using source file "%s"', source_file)

        if source_file.suffix == '.cpp':
            if os.name == 'nt':  # Windows, change to .exe
                executable = source_file.with_suffix('.exe')
            else:  # Unix, remove extension
                executable = source_file.with_suffix('')

            logger.info('Using executable "%s"', executable)
            if not executable.is_file():
                print(f'Executable "{executable}" not found, please compile first')
                return
            mtime_source = source_file.stat().st_mtime
            mtime_executable = executable.stat().st_mtime
            if mtime_source > mtime_executable:
                logger.warning('Source file "%s" is modified after executable "%s", '
                               'did you forget to compile?', source_file, executable)
            executor = TraditionalExecutor(
                args=str(executable.absolute()),
                time_limit=time_limit, memory_limit=memory_limit,
            )

        elif source_file.suffix == '.py':
            # use the current interpreter to run the py file
            logger.info('Using interpreter "%s"', sys.executable)
            executor = TraditionalExecutor(
                args=[sys.executable, str(source_file)],
                time_limit=time_limit, memory_limit=memory_limit,
            )

        else:
            print("Other languages are not supported yet >< plz use --shell")
            return

    # Run the tests
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
            print(f"{Fore.GREEN}#{idx} Passed...{Fore.RESET}  {result.execution_time:.2f}s",
                  f"{result.peak_memory/1024/1024:.2f}MB" if result.peak_memory and
                  result.peak_memory>0 else "")
            if result.memory_exceeded:
                # MLE, but don't change return_code
                print(f"...But memory exceeded")
        else:
            print(f"{Fore.RED}#{idx} Failed...{Fore.RESET}  {result.reason}")
            return_code = result.return_code or 1  # exit the status code if RE, else 1
        idx += 1

    if idx == 1:
        print("No testcases found, please parse them first")
        return_code = 1
    
    if not args.poll and os.name == 'posix':
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            peak_memory = usage.ru_maxrss
            if sys.platform == 'linux':
                peak_memory *= 1024  # on Linux it's KB
            print(f"Peak memory usage <= {peak_memory/1024/1024:.2f}MB")
        except Exception as e:
            logger.exception(e)

    if return_code:
        exit(return_code)

