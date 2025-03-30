from abc import ABC, abstractmethod
import json
import os
from pathlib import Path
import http.cookiejar
import logging
from typing import Dict, List, Optional, Tuple

from pyforces.cf.problem import CFProblem
from pyforces.utils import parse_csrf_token_from_html

class Client(ABC):
    """ The automated web handler class.
    Abstracted to support cloudscraper, selenium, m1.codeforces.com, etc.
    The abstract methods aligns with the interactive config options.
    """

    @classmethod
    @abstractmethod
    def from_path(cls, path: Path):
        """ Load from ~/.pyforces """
        # cookies = http.cookiejar.LWPCookieJar(path / 'cookies.txt')
        # try:
        #     cookies.load()
        # except FileNotFoundError:
        #     logging.info("Cookie file not found, will create one.")
        # return cls(cookies=cookies, _root=path)
        ...

    @abstractmethod
    def login(self, host: str, username: str, password: str):
        ...

    @abstractmethod
    def parse_testcases(self, url: str) -> List[Tuple[str, str]]:
        ...

    @abstractmethod
    def submit(self,
               url: str,
               problem_id: str,
               program_type_id: int,
               source_file: Path,
               ):
        """
        Args:
            url:  something like https://codeforces.com/contest/2092/submit
            problem_id:  A, B, C, etc
            program_type_id:  54 for C++17
            source_file:  path to source file
        """
        ...
        
    @abstractmethod
    def save(self):
        ...


class CloudscraperClient(Client):
    """ This client sends any HTTP requests with cloudscraper, with custom HTTP headers. """
    
    def __init__(self,
                 headers: Optional[Dict[str, str]],
                 csrf_token: Optional[str],
                 _root: Path,
                 _headers_file: Path,
                 _csrf_token_file: Path,
                 ):
        import cloudscraper
        self.scraper = cloudscraper.create_scraper(debug=True)
        self.headers = headers
        self.csrf_token = csrf_token
        self._root = _root
        self._headers_file = _headers_file
        self._csrf_token_file = _csrf_token_file
    
    @classmethod
    def from_path(cls, path: Path):
        headers_file = path / 'headers.txt'
        csrf_token_file = path / 'csrf_token.txt'
        try:
            with headers_file.open() as fp:
                headers = json.load(fp)
        except FileNotFoundError:
            logging.info("%s not found", headers_file)
            headers = None
        except json.JSONDecodeError:
            logging.error("%s decode error, this should not happen!", headers_file)
            headers = None

        try:
            csrf_token = csrf_token_file.read_text()
        except FileNotFoundError:
            logging.info("%s not found, will parse it later", csrf_token_file)
            csrf_token = None

        return cls(
            headers=headers,
            csrf_token=csrf_token,
            _root=path,
            _headers_file=headers_file,
            _csrf_token_file=csrf_token_file,
        )

    def login(self, host: str, username: str, password: str):
        """ Currently this is function will not be invoked, login with HTTP headers instead. """
        # resp = self.scraper.get(host + '/enter')
        # print(resp.text)
        raise NotImplementedError()

    def submit(self,
               url: str,
               problem_id: str,
               program_type_id: int,
               source_file: Path,
               ):
        if self.headers is None:
            print("You should login with HTTP headers first, see video tutorial.")
            return
        if self.csrf_token is None:
            logging.info("Csrf token not set, parsing it")
            from urllib.parse import urlparse
            parsed = urlparse(url)
            self.parse_csrf_token(f"{parsed.scheme}://{parsed.hostname}")

        source = source_file.read_text()
        resp = self.scraper.post(
            url,
            headers=self.headers,
            params={'csrf_token': self.csrf_token},
            data={
                'csrf_token': self.csrf_token,
                # 'ftaa': os.urandom(9).hex(),  # ftaa and bfaa doesn't seem to do anything
                # 'bfaa': os.urandom(16).hex(),
                'action': 'submitSolutionFormSubmitted',
                'submittedProblemIndex': problem_id.upper(),
                'programTypeId': program_type_id,
                'source': source,
                # 'sourceFile': '',
                '_tta': 961,
            }
        )

    def parse_testcases(self, url: str) -> List[Tuple[str, str]]:
        problem = CFProblem.parse_from_url(
            url, web_parser=lambda u: self.scraper.get(u, headers=self.headers).text
        )
        return problem.testcases
    
    def save(self):
        super().save()
        if self.headers:
            with self._headers_file.open('w') as fp:
                json.dump(self.headers, fp)
            logging.info("Saved %d headers to %s", len(self.headers), self._headers_file)
        if self.csrf_token:
            with self._csrf_token_file.open('w') as fp:
                fp.write(self.csrf_token)
            logging.info("Saved csrf token")

    def parse_csrf_token(self, host: str):
        if self.headers is None:
            print("You need to configure HTTP headers first")
            return
        if self.csrf_token:
            print(f"Current csrf token: {self.csrf_token}")

        resp = self.scraper.get(host, headers=self.headers)
        self.csrf_token = parse_csrf_token_from_html(resp.text)
        print(f"Parsed csrf token {self.csrf_token}")

