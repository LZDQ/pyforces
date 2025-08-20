from typing import Callable

from pyforces.cf.parser import ProblemPage, parse_problem_page_from_html
from pyforces.cf.problem_type import ProblemType

class CFProblem:
    
    def __init__(
        self,
        url: str,
        problem_type: ProblemType,
        testcases: list[tuple[str, str]],
        time_limit: float,
        memory_limit: int,  # in bytes
        problem_page: ProblemPage,  # for problem statement
    ):
        self.url = url
        self.problem_type = problem_type
        self.testcases = testcases
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.problem_page = problem_page

    @classmethod
    def parse_from_url(cls, url: str, web_parser: Callable):
        """ Init an instance from url.
        Args:
            url: something like https://codeforces.com/contest/2092/problem/A
            web_parser: a function that accepts a url string and returns the HTML
        """
        problem_page = parse_problem_page_from_html(web_parser(url))
        return cls(
            url=url,
            problem_type=problem_page.problem_type,
            testcases=problem_page.testcases,
            time_limit=problem_page.time_limit,
            memory_limit=problem_page.memory_limit,
            problem_page=problem_page,
        )




