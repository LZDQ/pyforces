from abc import ABC, abstractmethod
from pathlib import Path
import http.cookiejar
import logging

class Client(ABC):
    """ The automated web handler class.
    Abstracted to support cloudscraper, selenium, m1.codeforces.com, etc.
    Must override `login`, `parse_testcases`, `submit` methods.
    """

    def __init__(self,
                 cookies: http.cookiejar.LWPCookieJar,
                 client_file: Path,
                 ):
        self.cookies = cookies
        self._client_file = client_file

    @classmethod
    def from_file(cls, path: Path):
        cookies = http.cookiejar.LWPCookieJar(path)
        try:
            cookies.load()
        except FileNotFoundError:
            logging.info("Cookie file not found, will create one.")
        return cls(cookies=cookies, client_file=path)

    @abstractmethod
    def login(self, host: str, username: str, password: str):
        ...

    @abstractmethod
    def parse_testcases(self, url: str):
        ...

    @abstractmethod
    def submit(self, url: str, program_type_id: int, source_file: Path):
        ...

    def save(self):
        """ Save the cookies back to disk. Child classes should ensure the cookies are updated. """
        self.cookies.save()
        

class CloudscraperClient(Client):
    """ This client send any HTTP requests with cloudscraper. """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import cloudscraper
        self.scraper = cloudscraper.create_scraper(browser='chrome', debug=True)
        self.scraper.cookies = self.cookies

    def login(self, host: str, username: str, password: str):
        resp = self.scraper.get(host + '/enter')
        # <meta name="X-Csrf-Token" content="a-hex-string"/>
        # print(resp.text)
        print(self.cookies)
        print(self.scraper.cookies)
    
    def submit():
        pass

    def parse_testcases(self, url: str):
        pass

