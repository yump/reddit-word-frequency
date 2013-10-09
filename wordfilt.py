#!/usr/bin/env python

"""wordfilt.py: Library/utility for preparing text for word frequency analysis.

Usage: ./wordfilt.py [options] <file>

Options:
    -h --help   Show this help
"""
import re
import nltk
import unittest
from docopt import docopt

class WordMapper:

    def __init__(self, *args):
        """
        Create a WordMapper from one or more text files expressing word
        mappings.  Arguments are file names.  Each line in each file
        expresses an equivalence class after the mapping. For example,
        the line:

        be was is were are 

        will cause "was", "is", "were", and "are" to be mapped to "be".
        """
        try:
            raise NotImplementedError("Consider caching the map with marshall")
        except:
            self.mapping = dict()
            for fn in args:
                with open(fn) as mapfile:
                    map_specs =(l.split() for l in mapfile.read().splitlines())
                    # Build a dict mapping each equivalent word to the first.
                    for spec in map_specs:
                        if len(spec) >= 2: # No singletons or empty lines.
                            for word in spec:
                                if word in self.mapping:
                                    raise ValueError(
                                        "Duplicate word {}".format(word)
                                        )
                                else:
                                    self.mapping[word] = spec[0]

    def map(self,word):
        word = self.regex_subs(word)
        if word in self.mapping:
            return self.mapping[word]
        else:
            return word
    
    def regex_subs(self,word):
        word = re.sub("'s$",'',word) # killing trailing 's should be safe
        word = re.sub("'$",'',word)  # killing trailing ' should also be safe
        return word

def norm_capitalization(sent):
    """
    Normalize the capitalization of each word in a sentence, uncapping
    the first word if only the first letter is capitalized, and attempting
    to detect ALL CAPS with heuristics.
    
    Input
    =====
    sent : string

    Return
    ======
    unicode string

    """
    def uncap_titlecase_match(m):
        """Function for passing to re.sub. Lowercase a titlecase Word."""
        word = m.group(0)
        if re.sub(r'[^A-Za-z]','',word) not in {'I'}:
            return word.lower()
        else:
            return word

    def uncap_allcaps_match(m):
        phrase = m.group(0)
        return phrase.lower()
    
    # Uncap Studly words at begenning of sentence, or following " or '.
    sent = re.sub(r'((^|[\'">])[A-Z]([a-z-]+| ))',uncap_titlecase_match,sent)
    
    # Uncap n-grams of words in ALL CAPS, for n>=2.
    sent = re.sub(r'[A-Z]+( [A-Z]+)+',uncap_allcaps_match,sent)

    return sent

def clean_text(text):
   text = re.sub(r'&gt','>',text)   # quotes
   text = re.sub(r'&nbsp',' ',text) # I don't know where these come from.
   text = re.sub(r'https?://[^\s]+|[^\s]+\.[^\s]{2,3}','',text) # URLs
   return text


if __name__ == "__main__":
    args = docopt(__doc__)
    with open(args['<file>']) as infile:
        text = infile.read()
    text = clean_text(text)
    sents = nltk.sent_tokenize(text)
    text = "\n".join(norm_capitalization(s) for s in sents)
    print(text)


################################### TESTS #####################################

class Test_norm_capitalization(unittest.TestCase):

    def test_fixedstrings(self):
        fixedstrings = [
                "my machine runs Debian.",
                "there are four CPUs.",
                "CPU is an acronym here.",
                "P99 shouldn't change either",
                "bob says, 'SNAFU is an acryonym too.'",
                "T.J. rides the bus.",
                "I yam what I yam.",
                "he said, \"I yam what I yam.\""
                ]
        for s in fixedstrings:
            self.assertEqual(norm_capitalization(s),s)

    def test_sent_begin(self):
        inputs = [
                "This is a sentence.",
                "Ten-der.",
                "Supple."
                ]
        expected = [
                "this is a sentence.",
                "ten-der.",
                "supple."
                ]
        for i,e in zip(inputs,expected):
            self.assertEqual(norm_capitalization(i),e)

    def test_quote_begin(self):
        inputs = [
                "bob said, 'This is a sentence.'",
                "tj. said, \"Ten-der.\"",
                "'Supple,' Joe ejaculated.",
                "A man is not an island."
                ]
        expected = [
                "bob said, 'this is a sentence.'",
                "tj. said, \"ten-der.\"",
                "'supple,' Joe ejaculated.",
                "a man is not an island."
                ]
        for i,e in zip(inputs,expected):
            self.assertEqual(norm_capitalization(i),e)

    def test_allcaps(self):
        inputs = [
                "WHAT THE FUCK?",
                "We live in the USA.",
                "This is ABSOLUTELY RIDICULOUS.",
                "My computer has 4 GiB of RAM."
                ]
        expected = [
                "what the fuck?",
                "we live in the USA.",
                "this is absolutely ridiculous.",
                "my computer has 4 GiB of RAM."
                ]
        for i,e in zip(inputs,expected):
            self.assertEqual(norm_capitalization(i),e)


