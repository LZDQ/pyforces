import logging
import subprocess
import resource
import re
from pathlib import Path
from typing import TextIO, Tuple
from dataclasses import dataclass

import time

def compare_output(output: str, answer: str) -> Tuple[bool, str]:
    """ Compare output with answer. Return (passed, reason if not passed) """
    # TODO: add more logics like floating-point errors
    output = output.rstrip()
    answer = answer.rstrip()
    if re.match(r'\b(yes|no)\b', answer, flags=re.IGNORECASE):
        logging.info("Found 'Yes or No' type problem, performing case replacement")
        output = re.sub(r'\b(yes|no)\b', lambda m: m.group(1).lower(), output, flags=re.IGNORECASE)
        answer = re.sub(r'\b(yes|no)\b', lambda m: m.group(1).lower(), answer, flags=re.IGNORECASE)

    lines_output = output.splitlines()
    lines_answer = answer.splitlines()
    if len(lines_output) != len(lines_answer):
        return False, f"Expected {len(lines_answer)} lines, found {len(lines_output)} lines"
    for ln, (line_out, line_ans) in enumerate(zip(lines_output, lines_answer)):
        line_out = line_out.rstrip()
        line_ans = line_ans.rstrip()
        if line_out != line_ans:
            return False, f"Expected {line_ans} on line {ln}, found {line_out}"
    return True, "Passed"

@dataclass
class ExecuteResult:
    return_code: int
    timeout: bool
    runtime_error: bool
    execution_time: float  # in seconds
    peak_memory: int  # in bytes
    memory_exceeded: bool
    passed: bool
    reason: str

class TraditionalExecutor:
    
    def __init__(
        self,
        program_or_command: Path | str,
        shell: bool,
        time_limit: float,  # in seconds
        memory_limit: int,  # in bytes
    ):
        self.shell = shell
        if self.shell:
            self.command = program_or_command
        else:
            self.program = program_or_command
        self.time_limit = time_limit
        self.memory_limit = memory_limit

    def execute(self, input: TextIO, answer: TextIO) -> ExecuteResult:
        """ Given input and answer, execute the program and compare output with answer. """
        try:
            # Run subprocess with provided input and timeout
            start_time = time.perf_counter()
            proc = subprocess.run(
                self.command if self.shell else self.program,
                shell=self.shell,
                stdin=input,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.time_limit,
                text=True,
                check=True,
            )
            end_time = time.perf_counter()

            # After execution, capture resource usage (peak memory)
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            peak_memory = usage.ru_maxrss * 1024  # ru_maxrss returns KB on Linux

            passed, reason = compare_output(proc.stdout, answer.read())

            return ExecuteResult(
                return_code=proc.returncode,
                timeout=False,
                runtime_error=False,
                execution_time=end_time - start_time,
                peak_memory=peak_memory,
                memory_exceeded=peak_memory > self.memory_limit,
                passed=passed,
                reason=reason,
            )

        except subprocess.TimeoutExpired as e:
            end_time = time.perf_counter()
            return ExecuteResult(
                return_code=None,
                timeout=True,
                runtime_error=None,
                execution_time=end_time - start_time,
                peak_memory=None,
                memory_exceeded=None,
                passed=False,
                reason=f"Time limit exceeded: {end_time - start_time} seconds",
            )

        except subprocess.CalledProcessError as e:
            # Non-zero exit code encountered
            end_time = time.perf_counter()
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            peak_memory = usage.ru_maxrss * 1024

            return ExecuteResult(
                return_code=e.returncode,
                timeout=False,
                runtime_error=True,
                execution_time=end_time - start_time,
                peak_memory=peak_memory,
                memory_exceeded=peak_memory > self.memory_limit,
                passed=False,
                reason='Runtime error' + (': ' + e.stderr.decode().strip() if e.stderr else ''),
            )

