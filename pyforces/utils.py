from typing import Dict, Optional

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

def parse_firefox_http_headers(headers: dict) -> Dict[str, str]:
    """ Parse the firefox F12 Copy All headers to requests headers. """
    headers = list(headers.values())[0]['headers']
    headers = {h['name']: h['value'] for h in headers}
    headers['Accept-Encoding'] = 'gzip, deflate'
    return headers

def parse_csrf_token_from_html(html: str):
    # <meta name="X-Csrf-Token" content="a-hex-string"/>
    return html.split('<meta name="X-Csrf-Token" content="')[1].split('"', 1)[0]
