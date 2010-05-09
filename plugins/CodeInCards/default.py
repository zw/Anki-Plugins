# An example library for the CodeInCards plugin for Anki.
#
# Functions:
#
#   a(text)
#     Applies a format to the text if it appears on the answer side of the card.
#
#   ifnem(text, fmt)
#     Shows formatted text only if raw text is not empty.
#     Use "%s" inside the format to substitute text.  In card templates you'll
#     need to escape this as "%%s".
#
#   ifa(text)
#     Shows text only if part of the answer side of the card.
#
#   ifq(text)
#     Shows text only if part of the question side of the card.
#
#   pick(text)
#     Splits text on "," to make a list and returns a random element.
#     e.g. pick("any,of,these,terms,perhaps this one with spaces")
#
import random

# FIXME: should have a plugin to load a stylesheet from a file:
#ANSWER_FORMAT = """<span class='answerHighlight'>%s</span>"""
ANSWER_FORMAT = """<span style='color:blue; font-weight:bold; '>%s</span>"""

def a(text):
        if QorA == "a":
                return ANSWER_FORMAT % text
        return text 

def ifnem(text, fmt):
        if text != "":
                return fmt % text
        return ""

def ifa(text):
        if QorA == "a":
                return text
        return ""

def ifq(text):
        if QorA == "q":
                return text
        return ""

def pick(text):
        return random.choice(text.split(","))

# vim: softtabstop=8 shiftwidth=8 expandtab
