"""HTML extraction helpers."""

import re

from lxml import etree


def extract_img_url(string):
    """Extract the first image source URL from an HTML fragment."""
    try:
        if string is None:
            return None
        html = etree.HTML(string)
        for ii in html:
            images = ii.xpath("p/img/@src")
            return images[0]
    except Exception as e:
        print(e, string)


def extract_text(raw_data):
    """Extract visible text from an HTML fragment."""
    if raw_data is not None:
        html = etree.HTML(raw_data)

        content = []
        if html is not None:
            for script in html.xpath("//script"):
                parent = script.getparent()
                if parent is not None:
                    if script.tail:
                        prev = script.getprevious()
                        if prev is not None:
                            prev.tail = (prev.tail or "") + script.tail
                        else:
                            parent.text = (parent.text or "") + script.tail
                    parent.remove(script)

            html_data = html.xpath("/html/body/*//text()")
            for data in html_data:
                tmp = (
                    data.strip(" \n\r")
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\u3000", "")
                    .replace("\xa0", "")
                    .replace("\r", "")
                    .replace("\u2028", "")
                    .replace("\u2029", "")
                )
                if tmp:
                    content.append(tmp)

        item_article = "".join(content)
        return item_article
    else:
        return None
