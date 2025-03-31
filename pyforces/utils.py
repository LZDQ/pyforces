import glob
from pathlib import Path
from typing import Optional
from logging import getLogger

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
        
def input_y_or_n(prompt: str, default: Optional[bool] = None) -> bool:
    while True:
        s = input(prompt)
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

def get_current_contest_problem_id() -> tuple[int, str]:
    parts = Path.cwd().parts
    problem_id = parts[-1].upper()
    assert len(problem_id) == 1
    assert problem_id.isalpha()
    contest_id = int(parts[-2])
    return contest_id, problem_id

def get_current_cpp_file() -> Path:
    files = glob.glob("*.cpp")
    if not files:
        print("Cannot find any cpp file")
        return
    if len(files) > 1:
        print(f"Multiple source files found: {' '.join(files)}")
        return
    return Path(files[0]).absolute()
