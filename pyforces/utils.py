from pathlib import Path
from typing import Optional, TypeVar
from logging import getLogger
import re

logger = getLogger(__name__)

def input_index(tot: int, prompt: Optional[str] = None):
    """ Input an index within range [0, tot).
    Prompt defaults to 'Please choose one index:\n'
    """
    prompt = prompt or 'Please choose one index:\n'
    while True:
        try:
            s = int(input(prompt))
            assert 0 <= s < tot
            return s
        except ValueError:
            prompt = 'Please input a valid integer:\n'
        except AssertionError:
            prompt = f"Please input an integer within range [0, {tot}):\n"
        
def input_y_or_n(
    prompt: str,
    add_prompt: bool = False,
    default: Optional[bool] = None,
) -> bool:
    if add_prompt:
        if default is None:
            prompt = prompt + " [y/n]: "
        elif default:
            prompt = prompt + " [Y/n]: "
        else:
            prompt = prompt + " [y/N]: "
    while True:
        s = input(prompt).lower()
        if s == 'y':
            return True
        if s == 'n':
            return False
        if s == '' and default is not None:
            return default
        prompt = 'Please answer y or n.'

def parse_firefox_http_headers(headers: dict) -> dict[str, str]:
    """ Parse the firefox F12 Copy All headers to requests headers. """
    headers = list(headers.values())[0]['headers']
    headers = {h['name']: h['value'] for h in headers}
    headers['Accept-Encoding'] = 'gzip, deflate'
    return headers

def get_current_contest_type_id_problem_id() -> tuple[str, int, str]:
    """ contest_type, contest_id, problem_id """
    parts = Path.cwd().parts
    problem_id = parts[-1].upper()
    assert re.match(r'[A-Z][1-9]?', problem_id), f'"{problem_id}" is not valid problem id'
    contest_id = int(parts[-2])
    contest_type = parts[-3]
    assert contest_type in ['contest', 'gym']
    return contest_type, contest_id, problem_id

def get_current_cpp_file() -> Path | None:
    file = Path(Path.cwd().name + '.cpp')
    if file.is_file():
        return file
    logger.warning('File "%s" not found', file)

T = TypeVar('T')
def from_list1(l: list[T]) -> T:
    assert len(l) == 1, 'This list must have exactly one element'
    return l[0]

def contest_type_from_id(x: int):
    return 'contest' if x<100000 else 'gym'

def parse_human_bytesize(human_size: str):
    m = re.match(r'(\d+)([KMG]?)', human_size.upper())
    assert m, f'"{human_size}" is not valid byte size'
    units = {"": 1, "K": 1024, "M": 1024*1024, "G": 1024*1024*1024}
    return int(m.group(1)) * units[m.group(2)]

def to_human_bytesize(byte_size: int) -> str:
    b = byte_size
    s = ''
    for suf in "KMG":
        if b >= 1024:
            b >>= 10
            s = suf
        else:
            break
    return f"{b}{s}"
