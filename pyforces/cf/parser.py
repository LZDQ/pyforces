from typing import List, Tuple
from lxml import etree
from io import StringIO
import logging

def parse_testcases_from_html(html: str) -> List[Tuple[str, str]]:
    """ Parse and return the testcases. """
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    testcases = []
    sample_divs = tree.xpath("//div[@class='sample-test']")
    if not sample_divs:
        logging.error("No sample-test divs found")

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

