from enum import Enum
from pathlib import Path
from typing import Callable, Literal, Optional

from pyforces.cf.parser import parse_testcases_from_html

class ProblemType(Enum):
    TRADITIONAL = 0
    SPECIAL_JUDGE = 1
    INTERACTIVE = 2
    COMMUNICATION = 3

class CFProblem:
    
    def __init__(
        self,
        url: str,
        problem_type: ProblemType,
        testcases: list[tuple[str, str]],
        time_limit: float,
        memory_limit: int,  # in bytes
    ):
        self.url = url
        self.problem_type = problem_type
        self.testcases = testcases
        self.time_limit = time_limit
        self.memory_limit = memory_limit

    @classmethod
    def parse_from_url(cls, url: str, web_parser: Callable):
        """ Init an instance from url.
        Args:
            url: something like https://codeforces.com/contest/2092/problem/A
            web_parser: a function that accepts a url string and returns the HTML.

        Currently only parse the testcases, others are default values
        """
        testcases = parse_testcases_from_html(web_parser(url))
        return cls(
            url=url,
            problem_type=ProblemType.TRADITIONAL,
            testcases=testcases,
            time_limit=2,  # TL and ML are defaults now, doesn't really affect small testcases
            memory_limit=512*1024*1024,
        )




