#!/usr/bin/env python3

"""Insert Header/Footer into markdown files"""

import glob
import os
import re
import sys


EXERCISE_DOCS = ["question.md", "answer.md"]

SEQ_DICT = {
    "for_user": ["./common/%s" % f for f in ["command_list.md", "glossary.md", "windows_code_font.md"]],
    "for_author": ["./common/%s" % f for f in ["setup.md", "make_exercise.md"]],
    "tutorials": ["./tutorial%d/scenario.md" % i for i in range(0, 8)],
    "basic_exercise": sum([
        ["./l2nw%d/%s" % (i, f) for i in range(1, 3) for f in EXERCISE_DOCS],
        ["./l3nw%d/%s" % (i, f) for i in range(1, 3) for f in EXERCISE_DOCS],
        ["./l4nw%d/%s" % (i, f) for i in range(1, 3) for f in EXERCISE_DOCS],
    ], []),
    "adv_exercise": sum([
        ["./tutorial8/scenario.md"],
        ["./l2nw%d/%s" % (i, f) for i in range(3, 4) for f in EXERCISE_DOCS],
        ["./l4nw%d/%s" % (i, f) for i in range(3, 4) for f in EXERCISE_DOCS],
        ["./app%d/%s" % (i, f) for i in range(1, 3) for f in EXERCISE_DOCS],
    ], []),
}


def find_dict_contains(md_file_basename):
    """find key and list that contains specified file basename from SEQ_DICT"""
    for seq_name, seq_list in SEQ_DICT.items():
        if next((f for f in seq_list if f == md_file_basename), None):
            return seq_name  # return seq_name if found filename
    return None


def make_link(link_text, file_path):
    """make markdown link href"""
    return "[%s](%s)" % (link_text, file_path)


def make_prev_link(file_path, found_dict):
    """make previous link"""
    found_index = SEQ_DICT[found_dict].index(file_path)
    prev_index = found_index - 1
    if prev_index >= 0:
        prev_path = os.path.normpath(SEQ_DICT[found_dict][prev_index])
        return make_link("Previous", os.path.join("..", prev_path))

    return "Previous"


def make_next_link(file_path, found_dict):
    """make next link"""
    found_index = SEQ_DICT[found_dict].index(file_path)
    next_index = found_index + 1
    if next_index < len(SEQ_DICT[found_dict]):
        next_path = os.path.normpath(SEQ_DICT[found_dict][next_index])
        return make_link("Next", os.path.join("..", next_path))

    return "Next"


def make_top_link(found_dict):
    """make top link"""
    if found_dict == "for_author":
        return "[README](/README.md)"

    return "[Index](../index.md)"


def make_nav_link(file_path):
    """make page header links"""
    # basename without ext
    found_dict = find_dict_contains(file_path)
    if found_dict is None:
        print("Error: file %s is not found in SEQ_DICT" % file_path, file=sys.stderr)
        sys.exit(1)

    prev_link = make_prev_link(file_path, found_dict)
    next_link = make_next_link(file_path, found_dict)
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
