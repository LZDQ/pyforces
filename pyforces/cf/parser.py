from dataclasses import dataclass
from typing import Optional
from lxml import etree
from io import StringIO
import re
from markdownify import markdownify
from logging import getLogger

from pyforces.cf.problem_type import ProblemType
from pyforces.utils import from_list1, to_human_bytesize

logger = getLogger(__name__)

@dataclass
class ProblemPage:
    time_limit: float
    memory_limit: int
    problem_type: ProblemType
    title: str
    problem_statement: str
    input_spec: str
    output_spec: Optional[str]
    interaction_spec: Optional[str]
    testcases: list[tuple[str, str]]
    note: Optional[str]
    root_element: etree._Element

    def full_problem_statement(self) -> str:
        md = f"""
# {self.title}
##### time limit: {self.time_limit}s
##### memory limit: {to_human_bytesize(self.memory_limit)}
        """.strip() + "\n"
        md += "-----\n"
        md += self.problem_statement + "\n\n"
        md += "## Input\n\n"
        md += self.input_spec + "\n\n"
        if self.output_spec:
            md += "## Output\n\n"
            md += self.output_spec + "\n\n"
        if self.interaction_spec:
            md += "## Interaction\n\n"
            md += self.interaction_spec + "\n\n"
        md += "## Example\n\n"
        for input, output in self.testcases:
            md += "input\n"
            md += f"```\n{input}\n```\n"
            md += "output\n"
            md += f"```\n{output}\n```\n"
            md += "\n"
        if self.note:
            md += "## Note\n\n"
            md += self.note + "\n\n"
        return md.strip()

def parse_problem_page_from_html(html: str) -> ProblemPage:
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    problem_root = from_list1(tree.xpath("//div[@class='problem-statement']"))

    # Title
    title = from_list1(problem_root.xpath("./div[@class='header']/div[@class='title']/text()")).strip()

    # TL, ML
    try:
        time_limit_text = from_list1(problem_root.xpath(".//div[@class='time-limit']/text()"))
        tl_match = re.match(r'((?:[0-9]+\.)?[0-9]+) seconds?', time_limit_text.strip())
        time_limit = float(tl_match.group(1))
    except Exception as e:
        logger.exception(e)
        logger.warning("Cannot parse time limit, default to 2 seconds")
        time_limit = 2.
    try:
        memory_limit_text = problem_root.xpath(".//div[@class='memory-limit']/text()")[-1]
        ml_match = re.match(r'([0-9]+) megabytes?', memory_limit_text.strip())
        memory_limit = int(ml_match.group(1)) * 1024 * 1024
    except Exception as e:
        logger.exception(e)
        logger.warning("Cannot parse memory limit, default to 512 MB")
        memory_limit = 512 * 1024 * 1024

    html2md = lambda html: markdownify(html.replace("$$$", "$"), escape_underscores=False)
    div2md = lambda elem: html2md(etree.tostring(elem).decode())

    # Problem statement
    try:
        problem_statement_md = div2md(problem_root.xpath("./div[not(@class)]")[0])
    except Exception as e:
        logger.exception(e)
        logger.warning("Cannot parse problem statement")
        problem_statement_md = None

    # Input specification
    input_spec_md = output_spec_md = interaction_spec_md = None
    problem_type = ProblemType.TRADITIONAL

    # Interaction/Output specification
    interaction_div = problem_root.xpath('.//div[@class="section-title" and text()="Interaction"]')
    if interaction_div:
        problem_type = ProblemType.INTERACTIVE
        interaction_div = from_list1(interaction_div)
        logger.info("Interactive problem detected")
        try:
            input_spec_md = div2md(from_list1(
                problem_root.xpath("./div[@class='input-specification']")
            )).removeprefix("Input").strip()
        except Exception as e:
            logger.exception(e)
            logger.warning("Cannot parse input specification")
        try:
            interaction_spec_md = div2md(
                interaction_div.getparent()
            ).removeprefix("Interaction").strip()
        except Exception as e:
            logger.exception(e)
            logger.warning("Cannot parse interaction specification")
    else:
        try:
            input_spec_md = div2md(from_list1(
                problem_root.xpath("./div[@class='input-specification']")
            )).removeprefix("Input").strip()
        except Exception as e:
            logger.exception(e)
            logger.warning("Cannot parse input specification")
        try:
            output_spec_md = div2md(from_list1(
                problem_root.xpath("./div[@class='output-specification']")
            )).removeprefix("Output").strip()
        except Exception as e:
            logger.exception(e)
            logger.warning("Cannot parse output specification")

    # Note (testcase explanation, etc.)
    note_div = problem_root.xpath("./div[@class='note']")
    if note_div:
        note_md = div2md(from_list1(note_div)).removeprefix("Note").strip()
    else:
        note_md = None

    # Sample testcases
    testcases = []
    sample_div = tree.xpath("//div[@class='sample-tests']")[0]
    for input_div, output_div in \
            zip(sample_div.xpath(".//div[@class='input']"),
                sample_div.xpath(".//div[@class='output']")):
        input_text_nodes = input_div.xpath("./pre//text()")
        input_text = '\n'.join(node.strip() for node in input_text_nodes if node.strip())

        answer_text_nodes = output_div.xpath("./pre//text()")
        answer_text = '\n'.join(node.strip() for node in answer_text_nodes if node.strip())

        testcases.append((input_text, answer_text))

    logger.info("Parsed problem from html: %s", title)
    return ProblemPage(
        time_limit=time_limit,
        memory_limit=memory_limit,
        problem_type=problem_type,
        title=title,
        problem_statement=problem_statement_md,
        input_spec=input_spec_md,
        output_spec=output_spec_md,
        interaction_spec=interaction_spec_md,
        testcases=testcases,
        note=note_md,
        root_element=problem_root,
    )

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

def parse_problem_indices_from_html(html: str) -> list[str]:
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    return [idx.strip() for idx in tree.xpath("//td[contains(@class, 'id')]/a/text()")]

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


