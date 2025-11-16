import json
from pathlib import Path
from logging import getLogger
import subprocess
import time

from pyforces.cf.problem import CFProblem
from pyforces.cf.parser import *
from pyforces.utils import parse_firefox_http_headers

logger = getLogger(__name__)

class Client:
    """ This client sends any HTTP requests with cloudscraper, with custom HTTP headers. """
    
    def __init__(
        self,
        headers: dict[str, str] | None,
        csrf_token: str | None,
        handle: str | None,
        _root: Path,
        _headers_file: Path,
        _csrf_token_file: Path,
    ):
        import cloudscraper
        self.scraper = cloudscraper.create_scraper(
            # debug=all(handler.level <= logging.DEBUG for handler in logging.handlers)
            debug=False  # TODO: log the request and response
        )
        self.headers = headers
        self.csrf_token = csrf_token
        self.handle = handle
        self._root = _root
        self._headers_file = _headers_file
        self._token_file = _csrf_token_file
    
    @classmethod
    def from_path(cls, path: Path):
        headers_file = path / 'headers.txt'
        token_file = path / 'csrf_token_and_handle.txt'
        try:
            with headers_file.open() as fp:
                headers = json.load(fp)
        except FileNotFoundError:
            logger.info("%s not found", headers_file)
            headers = None
        except json.JSONDecodeError:
            logger.error("%s decode error, this should not happen!", headers_file)
            headers = None
        if headers and len(headers) == 1 and list(headers.keys())[0].startswith("Request Headers"):
            # firefox headers, parse it
            logger.info("Detected headers with only one entry with dict value, trying parsing firefox headers...")
            try:
                headers = parse_firefox_http_headers(headers)
            except Exception as e:
                logger.exception(e)
                logger.error("Failed to parse firefox headers")
                headers = None

        try:
            csrf_token, handle = token_file.read_text().splitlines()
        except FileNotFoundError:
            logger.info("%s not found, will parse it later", token_file)
            csrf_token = None
            handle = None
        except ValueError:
            logger.warning("Failed to get csrf token and handle from %s", token_file)
            csrf_token = None
            handle = None

        return cls(
            headers=headers,
            csrf_token=csrf_token,
            handle=handle,
            _root=path,
            _headers_file=headers_file,
            _csrf_token_file=token_file,
        )

    def submit(
        self,
        url: str,
        problem_id: str,
        program_type_id: int,
        source_file: Path,
        track: bool,
        strip_comment: bool,
    ):
        """
        Args:
            url:  something like https://codeforces.com/contest/2092/submit
            problem_id:  A, B, C, D1, D2, etc
            program_type_id:  54 for C++17
            source_file:  path to source file
            track:  whether return the submission id
            strip_comment:  whether use `g++ -E -fpreprocessed` to remove comments
        """
        if self.headers is None:
            print("You should login with HTTP headers first, see video tutorial.")
            return
        if self.csrf_token is None:
            logger.info("Csrf token not set, parsing it")
            from urllib.parse import urlparse
            parsed = urlparse(url)
            self.parse_csrf_token(f"{parsed.scheme}://{parsed.hostname}")

        if strip_comment:
            if source_file.suffix == '.cpp':
                source = subprocess.check_output(
                    # credits to https://www.reddit.com/r/cpp/comments/1ldkpn2/comment/mynbk4m/
                    ['g++', '-E', '-fpreprocessed', '-dD', '-P', str(source_file)]
                )
            else:
                logger.warning("Option --strip-comment only supports cpp files.")
        else:
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
                # '_tta': 961,
            }
        )
        if 'You have submitted exactly the same code before' in resp.text:
            print('You have submitted exactly the same code before')
            return
        # try:  TODO: verify the submission
        #     assert parse_csrf_token_from_html(resp.text) == self.csrf_token
        # except Exception as e:
        #     logger.error("Failed to verify csrf token: %s", e)
        #     print("Submission failed, please re-login.")
        #     return

        print(f"Submitted. {resp}")
        if track:  # TODO: verify that the last submission id is the one just submitted
            # return the submission id along with cc and pc (for websocket tracking)
            assert url.endswith("submit")
            status_url = url[:-6] + 'my'
            sub_id = None
            for t in range(3):
                resp = self.scraper.get(status_url, headers=self.headers)
                try:
                    sub_id = parse_last_submission_id_from_html(resp.text)
                    cc, pc = parse_ws_cc_pc_from_html(resp.text)
                except AttributeError as e:
                    logger.exception(e)
                    print("Failed to get last submission id, retrying...")
                time.sleep(5)

            if sub_id is None:
                logger.error("Failed to get last submission id")
                return

            logger.info("Parsed last submission id %d", sub_id)
            return sub_id, cc, pc

        return

    def parse_problem(self, url: str) -> CFProblem:
        return CFProblem.parse_from_url(
            url, web_parser=lambda u: self.scraper.get(u, headers=self.headers).text
        )
    
    def save(self):
        if self.headers:
            with self._headers_file.open('w') as fp:
                json.dump(self.headers, fp, indent=4)
            logger.info("Saved %d headers to %s", len(self.headers), self._headers_file)
        if self.csrf_token:
            with self._token_file.open('w') as fp:
                fp.write(self.csrf_token + '\n')
                fp.write(self.handle)
            logger.info("Saved csrf token and handle")

    def parse_csrf_token_and_handle(self, host: str):
        if self.headers is None:
            logger.error("You need to configure HTTP headers first")
            return
        logger.info("Parsing csrf token and handle")
        logger.info("Current csrf token: %s", self.csrf_token)
        logger.info("Current handle: %s", self.handle)

        resp = self.scraper.get(host, headers=self.headers)
        try:
            self.csrf_token = parse_csrf_token_from_html(resp.text)
            self.handle = parse_handle_from_html(resp.text)
            logger.info("Parsed csrf token %s and handle %s", self.csrf_token, self.handle)
        except Exception as e:
            self.csrf_token = None
            self.handle = None
            logger.exception(e)
            logger.error("Cannot parse csrf token and handle (not logged in)")
    
    def parse_countdown(self, url_contest: str) -> tuple[int, int, int] | None:
        """ Parse the /countdown url and return h,m,s, or None if already started
        Args:
            url_contest: contest url without /countdown
        """
        url_countdown = url_contest + '/countdown'
        resp = self.scraper.get(url_countdown, headers=self.headers)
        return parse_countdown_from_html(resp.text)

    def parse_problem_indices(self, url_contest: str) -> int:
        resp = self.scraper.get(url_contest, headers=self.headers)
        return parse_problem_indices_from_html(resp.text)
    
    def parse_status(self, url_status: str) -> str:
        resp = self.scraper.get(url_status, headers=self.headers)
        return parse_verdict_from_html(resp.text)


