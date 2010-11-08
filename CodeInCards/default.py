'''
An example library for the CodeInCards plugin for Anki.

Functions:

  a(text)
    Applies a format to the text if it appears on the answer side of the card.

  ifnem(text, fmt)
    Shows formatted text only if raw text is not empty.
    Use "%s" inside the format to substitute text.  In card templates you'll
    need to escape this as "%%s".

  ifa(text)
    Shows text only if part of the answer side of the card.

  ifq(text)
    Shows text only if part of the question side of the card.

  pick(text)
    Splits text on "," to make a list and returns a random element.
    e.g. pick("any,of,these,terms,perhaps this one with spaces")

For really simple demonstration that it's working:

  sayHello()
    Returns a hello message.

  hello
    A hello message.

$Id$
'''
import random
import CodeInCards as CIC

# FIXME: would be better if we could create the corresponding style in
# %configDir%/style.css but that firstly doesn't work and secondly messes up
# the whole UI. 
ANSWER_FORMAT = """<span style='color:blue; font-weight:bold;'>%s</span>"""
HELLO = "Hello!"

def a(text):
        if CIC.QorA == "a":
                return ANSWER_FORMAT % text
        return text

def ifnem(text, fmt):
        if text != "":
                try:
                        return fmt % text
                except TypeError:
                        # No %s in fmt
                        return fmt
        return ""

def ifem(text, ifEmpty, ifNonEmpty=""):
        if text == "":
                return ifEmpty
        else:
                return ifNonEmpty

def ifa(text):
        if CIC.QorA == "a":
                return text
        return ""

def ifq(text):
        if CIC.QorA == "q":
                return text
        return ""

def pick(text, sep=","):
        return random.choice(text.split(sep))

def sayHello():
        return HELLO

# vim: softtabstop=8 shiftwidth=8 expandtab
