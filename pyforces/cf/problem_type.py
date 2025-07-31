from enum import Enum

class ProblemType(Enum):
    TRADITIONAL = 0  # default, most problems
    SPECIAL_JUDGE = 1  # not supported
    INTERACTIVE = 2  # support parsing but not judging
    COMMUNICATION = 3  # not supported
