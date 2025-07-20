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

    for sample_div in sample_divs:  # There is only one 'sample-test' but will keep the loop
        for input_div, output_div in \
                zip(sample_div.xpath("./div[@class='input']"),
                    sample_div.xpath("./div[@class='output']")):
            input_text_nodes = input_div.xpath("./pre//text()")
            input_text = '\n'.join(node.strip() for node in input_text_nodes if node.strip())

            answer_text_nodes = output_div.xpath("./pre//text()")
            answer_text = '\n'.join(node.strip() for node in answer_text_nodes if node.strip())

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

def parse_last_submission_id_from_html(html: str) -> int:
    # <tr data-submission-id="315671433" data-a="7963403939888496640" partyMemberIds=";915785;">
    return int(re.search(r'<tr data-submission-id="([1-9][0-9]*)"', html).group(1))

def parse_verdict_from_html(html: str) -> str:
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    th_verdict1 = tree.xpath("//th[text()='Verdict']")[0]
    row1 = th_verdict1.getparent()
    row2 = row1.getnext()
    th_verdict2 = row2.getchildren()[row1.index(th_verdict1)]
    return ' '.join(s.strip() for s in th_verdict2.xpath(".//text()") if s.strip())

def parse_ws_cc_pc_from_html(html: str) -> tuple[str, str]:
    """
    <meta name="cc" content="<some-hex>"/>
    <meta name="pc" content="<some-hex>"/>
    """
    return re.search(r'<meta name="cc" content="([0-9a-f]+)"/>', html).group(1), \
        re.search(r'<meta name="pc" content="([0-9a-f]+)"/>', html).group(1)


