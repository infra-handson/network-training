#!/usr/bin/env python3

"""Insert Header/Footer into markdown files"""

import glob
import os
import re
import sys


SEQ_DICT = {
    "for_user": ["command_list", "glossary"],
    "for_author": ["setup", "make_exercise"],
    "tutorials": ["tutorial_0", "tutorial_1", "tutorial_2", "tutorial_3", "tutorial_4", "tutorial_5"],
    "basic_exercise": [
        "l2nw_1",
        "l2nw_1ans",
        "l2nw_2",
        "l2nw_2ans",
        "l3nw_1",
        "l3nw_1ans",
        "l3nw_2",
        "l3nw_2ans",
        "l4nw_1",
        "l4nw_1ans",
        "l4nw_2",
        "l4nw_2ans",
    ],
    "adv_exercise": [
        "tutorial_6",
        "l2nw_3",
        "l2nw_3ans",
        "l4nw_3",
        "l4nw_3ans",
        "app_1",
        "app_1ans",
        "app_2",
        "app_2ans",
    ],
}


def find_dict_contains(md_file_basename):
    """find key and list that contains specified file basename from SEQ_DICT"""
    for seq_name, seq_list in SEQ_DICT.items():
        if next((f for f in seq_list if f == md_file_basename), None):
            return seq_name  # return seq_name if found filename
    return None


def make_link(md_file_basename, found_dict, link_text):
    """make markdown link href"""
    if found_dict in ("for_user", "for_author"):
        return "[%s](../common/%s.md)" % (link_text, md_file_basename)
    if found_dict == "tutorials":
        return "[%s](../%s/%s.md)" % (link_text, re.sub("[a-z]$", "", md_file_basename), md_file_basename)
    if found_dict in ("basic_exercise", "adv_exercise"):
        return "[%s](../%s/%s.md)" % (link_text, md_file_basename.replace("ans", ""), md_file_basename)
    return "[%s]" % link_text


def make_prev_link(md_file_basename, found_dict):
    """make previous link"""
    found_index = SEQ_DICT[found_dict].index(md_file_basename)
    prev_index = found_index - 1
    if prev_index >= 0:
        return make_link(SEQ_DICT[found_dict][prev_index], found_dict, "Previous")

    return "Previous"


def make_next_link(md_file_basename, found_dict):
    """make next link"""
    found_index = SEQ_DICT[found_dict].index(md_file_basename)
    next_index = found_index + 1
    if next_index < len(SEQ_DICT[found_dict]):
        return make_link(SEQ_DICT[found_dict][next_index], found_dict, "Next")

    return "Next"


def make_top_link(found_dict):
    """make top link"""
    if found_dict == "for_author":
        return "[README](/README.md)"

    return "[Index](../index.md)"


def make_nav_link(file_path):
    """make page header links"""
    # basename without ext
    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    found_dict = find_dict_contains(file_basename)
    if found_dict is None:
        print("Error: file %s is not found in SEQ_DICT" % file_path, file=sys.stderr)
        sys.exit(1)

    prev_link = make_prev_link(file_basename, found_dict)
    next_link = make_next_link(file_basename, found_dict)
    top_link = make_top_link(found_dict)

    return "%s << %s >> %s" % (prev_link, top_link, next_link)


def replace_header(body, header_str):
    """replace (renew) header"""
    before_str = r"<!-- HEADER -->.*<!-- /HEADER -->"
    after_str = "<!-- HEADER -->\n%s\n<!-- /HEADER -->" % header_str
    return re.sub(before_str, after_str, body, flags=re.DOTALL)


def replace_footer(body, footer_str):
    """replace (renew) footer"""
    before_str = r"<!-- FOOTER -->.*<!-- /FOOTER -->"
    after_str = "<!-- FOOTER -->\n%s\n<!-- /FOOTER -->" % footer_str
    return re.sub(before_str, after_str, body, flags=re.DOTALL)


def replace_header_and_footer(file_path, header_str, footer_str):
    """replace (renew) header and footer"""
    body = None
    with open(file_path, "r") as file:
        body = file.read()

    if body is None:
        return  # file read error

    body = replace_header(body, header_str)
    body = replace_footer(body, footer_str)

    with open(file_path, "w") as file:
        file.write(body)


def make_header(header_nav_str):
    """make header part"""
    return "%s\n\n---" % header_nav_str


def make_footer(footer_nav_str):
    """make footer part"""
    return "\n---\n\n%s" % footer_nav_str


if __name__ == "__main__":
    for md_file_path in glob.glob("./**/*.md"):
        nav_str = make_nav_link(md_file_path)
        print("file: %s, header: %s" % (md_file_path, nav_str))
        replace_header_and_footer(md_file_path, make_header(nav_str), make_footer(nav_str))
