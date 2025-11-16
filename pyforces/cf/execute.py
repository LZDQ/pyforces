import os
import subprocess
import re
import time
from logging import getLogger
from typing import TextIO
from dataclasses import dataclass

logger = getLogger(__name__)

def compare_output(output: str, answer: str) -> tuple[bool, str]:
    """
    Compare output with answer. Return tuple (passed, reason if not passed).

    If not passed, also print the output and answer (as a side effect).
    """
    # TODO: add more logics like floating-point errors
    output = output.rstrip()
    answer = answer.rstrip()

    if re.search(r'\b(yes|no)\b', answer, flags=re.IGNORECASE):
        logger.info('Found "Yes or No" type problem, performing case replacement')
        output = re.sub(r'\b(yes|no)\b', lambda m: m.group(1).lower(), output, flags=re.IGNORECASE)
        answer = re.sub(r'\b(yes|no)\b', lambda m: m.group(1).lower(), answer, flags=re.IGNORECASE)

    logger.debug('output is %s, answer is %s', repr(output), repr(answer))
    lines_output = output.splitlines()
    lines_answer = answer.splitlines()

    def print_diff():
        """ Print the output and answer. May add diff in the future. """
        print("--- OUTPUT ---")
        print(output)
        print("--- ANSWER ---")
        print(answer)
        print("--------------")

    if len(lines_output) != len(lines_answer):
        print_diff()
        return False, f"Expected {len(lines_answer)} lines, found {len(lines_output)} lines"

    for ln, (line_out, line_ans) in enumerate(zip(lines_output, lines_answer), 1):
        line_out = line_out.rstrip()
        line_ans = line_ans.rstrip()
        logger.debug('Comparing line %d: output=%s answer=%s', ln, repr(line_out), repr(line_ans))
        if line_out != line_ans:
            print_diff()
            return False, f"Expected {line_ans} on line {ln}, found {line_out}"

    return True, "Passed"

@dataclass
class ExecuteResult:
    return_code: int
    timeout: bool  # TLE
    runtime_error: bool  # RE
    memory_exceeded: bool  # MLE
    execution_time: float  # in seconds
    peak_memory: int  # in bytes
    passed: bool
    reason: str  # useful if failed

class TraditionalExecutor:
    
    def __init__(
        self,
        args: str | list[str] | None = None,
        shell: str | None = None,
        time_limit: float = 2.0,  # in seconds
        memory_limit: int = 512*1024*1024,  # in bytes
    ):
        if args:
            assert not shell, "Cannot pass both args and shell to TraditionalExecutor"
            self.args = args
            self.is_shell = False
        else:
            assert shell, "Must pass either args or shell to TraditionalExecutor"
            self.args = shell
            self.is_shell = True

        self.time_limit = time_limit
        self.memory_limit = memory_limit

    def execute(self, input: TextIO, answer: TextIO, poll: bool) -> ExecuteResult:
        """ Given input and answer, execute the program and compare output with answer.
        poll: whether use psutil Popen to track usage.
        If poll, Unix and Windows have almost the same impl except for peak memory stats.
        If no poll, on Unix will use getrusage to get peak memory of all test cases, and
        no memory stats on Windows. Both have no memory limit.
        """
        if poll:
            logger.info("Using psutil to poll and track")
            import psutil
            proc = psutil.Popen(
                self.args,
                shell=self.is_shell,
                stdin=input,
                stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                text=True,
            )
            peak_memory = -1
            user_time = 0.
            polls = 0
            while proc.poll() is None:
                try:  # avoid TOCTOU
                    user_time = proc.cpu_times().user
                    match os.name:
                        case 'posix':  # Linux, Mac
                            peak_memory = max(peak_memory, proc.memory_info().rss)
                        case 'nt':  # Windows
                            peak_memory = proc.memory_info().peak_wset
                except Exception as e:
                    logger.info("Stats tracking error %s", e)
                time.sleep(1e-5)
                polls += 1
                if user_time > self.time_limit:  # Change in v0.4.3: do NOT double time limit
                    proc.kill()
                    logger.info("Killed the program exceeding double timeout")
                    return ExecuteResult(
                        return_code=None,
                        timeout=True,
                        runtime_error=None,
                        execution_time=user_time,
                        memory_exceeded=peak_memory>self.memory_limit,
                        peak_memory=peak_memory,
                        passed=False,
                        reason=f"Time limit exceeded: {user_time} seconds",
                    )
            logger.info("Ran the program in %.2f seconds and %d peak memory", user_time, peak_memory)
            logger.debug("Polled %d times", polls)
            if proc.returncode:
                return ExecuteResult(
                    return_code=proc.returncode,
                    timeout=user_time>self.time_limit,
                    runtime_error=True,
                    memory_exceeded=peak_memory>self.memory_limit,
                    execution_time=user_time,
                    peak_memory=peak_memory,
                    passed=False,
                    reason=f"Runtime error, exit code {proc.returncode}.",
                )
            if user_time > self.time_limit:
                return ExecuteResult(
                    return_code=proc.returncode,
                    timeout=True,
                    runtime_error=False,
                    memory_exceeded=peak_memory>self.memory_limit,
                    execution_time=user_time,
                    peak_memory=peak_memory,
                    passed=False,
                    reason=f"Time limit exceeded: {user_time} seconds",
                )

            passed, reason = compare_output(proc.stdout.read(), answer.read())
            return ExecuteResult(
                return_code=proc.returncode,
                timeout=False,
                runtime_error=False,
                execution_time=user_time,
                peak_memory=peak_memory,
                memory_exceeded=peak_memory>self.memory_limit,
                passed=passed,
                reason=reason,
            )
        
        else:  # no poll
            logger.info("Not polling, using subprocess.run")
            try:
                # Run subprocess with provided input and timeout
                start_time = time.perf_counter()
                proc = subprocess.run(
                    self.args,
                    shell=self.is_shell,
                    stdin=input,
                    stdout=subprocess.PIPE,
                    # stderr=subprocess.PIPE,
                    timeout=self.time_limit,
                    text=True,
                    check=True,
                )
                end_time = time.perf_counter()

                passed, reason = compare_output(proc.stdout, answer.read())

                return ExecuteResult(
                    return_code=proc.returncode,
                    timeout=False,
                    runtime_error=False,
                    execution_time=end_time-start_time,
                    peak_memory=None,
                    memory_exceeded=None,
                    passed=passed,
                    reason=reason,
                )

            except subprocess.TimeoutExpired as e:
                end_time = time.perf_counter()
                return ExecuteResult(
                    return_code=None,
                    timeout=True,
                    runtime_error=None,
                    execution_time=end_time-start_time,
                    peak_memory=None,
                    memory_exceeded=None,
                    passed=False,
                    reason=f"Time limit exceeded: {end_time - start_time :.2f} seconds",
                )

            except subprocess.CalledProcessError as e:
                # Non-zero exit code encountered
                end_time = time.perf_counter()
                # usage = resource.getrusage(resource.RUSAGE_CHILDREN)
                # peak_memory = usage.ru_maxrss * 1024

                return ExecuteResult(
                    return_code=e.returncode,
                    timeout=False,
                    runtime_error=True,
                    memory_exceeded=None,
                    execution_time=end_time-start_time,
                    peak_memory=None,
                    passed=False,
                    reason=f"Runtime error, exit code {e.returncode}.",
                )

