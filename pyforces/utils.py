from typing import Optional

def input_index(tot: int, prompt: Optional[str] = None):
    """ Input an index within range [0, tot). """
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
        
def input_y_or_n(prompt: str) -> bool:
    while True:
        s = input(prompt)
        if s == 'y':
            return True
        if s == 'n':
            return False
        prompt = 'Please answer y or n.'
