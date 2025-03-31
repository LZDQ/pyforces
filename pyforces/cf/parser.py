from lxml import etree
from io import StringIO
import re
from logging import getLogger

logger = getLogger(__name__)

def parse_testcases_from_html(html: str) -> list[tuple[str, str]]:
    """ Parse and return the testcases. """
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    testcases = []
    sample_divs = tree.xpath("//div[@class='sample-test']")
    if not sample_divs:
        logger.error("No sample-test divs found")

    for sample_div in sample_divs:
        input_div = sample_div[0]
        pre_div = input_div.xpath("./pre")[0]
        subcase_divs = pre_div.xpath("./div[contains(@class, 'test-example-line')]")
        if subcase_divs:
            # (Modern) multiple subcases in one test
            input_text = '\n'.join(subcase_div.text.strip() for subcase_div in subcase_divs)
        else:
            # (Old) test without interleaving color
            input_text = pre_div.text.strip()
            
        output_div = sample_div[1]
        pre_div = output_div.xpath("./pre")[0]
        answer_text = pre_div.text.strip()
        testcases.append((input_text + '\n', answer_text + '\n'))

    return testcases

def parse_handle_from_html(html: str) -> str:
    """ Parse the username from html, throw an error if not logged in """
    # handle is in javascript; accepts alphanumeric, underscore and dash
    return re.search(r'var handle = "([\w\-]+)";', html).group(1)

def parse_csrf_token_from_html(html: str) -> str:
    """ Parse the csrf token, throw an error if fail """
    # <meta name="X-Csrf-Token" content="a-hex-string"/>
    return re.search(r'<meta name="X-Csrf-Token" content="([0-9a-f]+)"/>', html).group(1)

def parse_countdown_from_html(html: str) -> tuple[int, int, int] | None:
    if 'Go!</a>' in html:
        return
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    countdown_divs = tree.xpath("//span[@class='countdown']")
    if len(countdown_divs) != 1:
        logger.error("Found %d countdown divs", len(countdown_divs))
        return
    h_m_s = countdown_divs[0].text
    h, m, s = h_m_s.split(':')
    h, m, s = int(h), int(m), int(s)
    return h, m, s

def parse_problem_count_from_html(html: str) -> int:
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    return len(tree.xpath("//td[contains(@class, 'id')]"))

