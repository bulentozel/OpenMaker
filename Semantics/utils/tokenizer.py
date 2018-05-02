# -*- coding: utf-8 -*-
"""OpenMaker text tokenizer.

Author: Bulent Ozel
e-mail: bulent.ozel@gmail.com

The module contains a set of basic tools in order to tokenize a given inout text.

Todo:
    * Nothing at the moment ;)

"""

import re

ALLOWED_SYMBOLS = list("abcdefghijklmnopqrstuvwxyz1234567890-")
CHARACTERS_TO_SPLIT = """.,():;!?\n`'=+/\[]}{|><@#$%^&*_"""
CHARACTERS_TO_SPLIT += '‘'+'’'+'“'+'”'+'.'
REPLACEMENTS = {
    r"\x05": " ",
    "&": "and",
    r"`": " ",
    r"'": " ",
    r"-": " "
}

def tokenize(raw):
    """The function tokenizes by splitting them on spaces, line breaks or characters
        in CHARACTERS_TO_SPLIT.
    
    Args:
        raw: (:obj:`str`): Input string to split
    
    Returns:
        (:obj:`list` of :obj:`str`): list of terms 
    
    """
    tokenized = []
    temp_string = ""
    raw = normalise(raw)
    for cc in raw:
        c = cc
        if c == " ":
            if temp_string != "":
                tokenized.append(temp_string)
                temp_string = ""
        elif c in CHARACTERS_TO_SPLIT:
            if temp_string != "":
                tokenized.append(temp_string)
            tokenized.append(c)
            temp_string = ""
        else:
            temp_string += c
    if temp_string != "":
        tokenized.append(temp_string)
    return tokenized


def tokenize_strip_non_words(raw):
    """Same as tokenize, but also removes non-word characters.
    
    Args:
        raw: (:obj:`str`): Input string to split
    
    Returns:
        (:obj:`list` of :obj:`str`): list of terms 
        
    """
    return [t for t in tokenize(raw) if t not in CHARACTERS_TO_SPLIT]


def normalise(s):
    """Basic string normalisation.
    
    Args:
        s: (:obj:`str`): Input string to normalise.
    
    Returns:
        (:obj:`str`): Normalised string.
        
    """
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = s.strip()
    s = re.sub(r"\n\n+", "\n\n", s)
    s = re.sub(r"\.\.\.+", "...", s)
    for k, v in REPLACEMENTS.items():
        s = s.replace(k, v)
    symbols = set(s)
    for c in symbols:
        if c not in ALLOWED_SYMBOLS:
            s = s.replace(c, " ")
    return s


def tokenized_pprint(tokens):
    """A pretty print function for strings tokenized by tokenize.
    
    Args:
        tokens: (:obj:`list` of :obj:`str`): list of terms 

    Returns:
        (:obj:`str`): The joined terms.
        
    """
    out = ""
    for t in tokens:
        if t in ".,):!?":
            if out[-1] == " ":
                out = out[:-1]
            out += t + " "
        elif t in "(":
            out += t
        elif t in "-\n":
            if out[-1] == " ":
                out = out[:-1]
            out += t
        else:
            out += t + " "
    return out