#!/usr/bin/env python

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published b
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
word_frequency.py: Print a list of words that appear most frequently
                   in a file.

Usage:
    word_frequency.py [-n NUM_WORDS] <input_file>

Options:
    -h --help            Show this screen.
    -n --num-words=<n>   Number of most-frequently-used words [default: 25].
"""

from docopt import docopt
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet as wn
from nltk.corpus import treebank
from nltk.tag import ClassifierBasedPOSTagger
import sys
import re
import itertools
import pickle
from collections import Counter
from wordmapper import WordMapper

tagger_fn = "tagger.pkl"
wordmap_files = ['equivs.txt','hard_lowercase.txt']

#John Gruber URL Matcher (Holy canoli!)
re_url = re.compile(
    ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
    ur'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\('
    ur'([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?'
    ur'\xab\xbb\u201c\u201d\u2018\u2019]))'
    )

def get_tagger():
    try:
        with open(tagger_fn) as tagger_file:
            tagger = pickle.load(tagger_file)
    except:
        tagger = ClassifierBasedPOSTagger(train=treebank.tagged_sents())
        with open(tagger_fn,"w") as tagger_file:
            pickle.dump(tagger,tagger_file)
    return tagger

def get_words_posfilter(text,norm_case):
    """
    Parse text and return a sequence of words, filtered to include the
    parts of speech we expect to find interesting.  This turns out to
    be slower than using a large blacklist, because PoS tagging is either
    a) really slow or b) requires an ass-ton of boilerplate.
    """
    ## Set up the nltk norming stuff
    wnl = nltk.stem.WordNetLemmatizer()

    ## Set up the optional case normalizer.
    if norm_case:
        def casefun(word):
            return word.lower()
    else:
        def casefun(word):
            return word

    tagger = get_tagger()
    parsed = ( 
                [
                w.strip(',.\'"?!') 
                for w in sent.split()
                ] 
            for sent in sent_tokenize(text) 
            )
    tagged = ( tagger.tag(sent) for sent in parsed )

    # Split the words by tag, so we can handle case-sensitivity differently.
    noun_tags  = {'NN','NNS','CD'}
    pnoun_tags = {'NNP','NNPS','FW'}
    adj_tags   = {'JJ','JJR','JJS'}
    adv_tags   = {'RB','RBR','RBS'}
    verb_tags  = {'VB','VBD','VBG','VBN','VBP','VBZ'}
    
    nouns = []
    prop_nouns = []
    adjs = []
    advs = []
    verbs = []

    for word in itertools.chain(*tagged):
        if word[1] in noun_tags:
            nouns.append(wnl.lemmatize(casefun(word[0]),pos=wn.NOUN))
        elif word[1] in pnoun_tags:
            prop_nouns.append(wnl.lemmatize(word[0],pos=wn.NOUN))
        elif word[1] in adj_tags:
            adjs.append(wnl.lemmatize(casefun(word[0]),pos=wn.ADJ))
        elif word[1] in adv_tags:
            advs.append(wnl.lemmatize(casefun(word[0]),pos=wn.ADV))
        elif word[1] in verb_tags:
            verbs.append(wnl.lemmatize(casefun(word[0]),pos=wn.VERB))

    return itertools.chain(nouns,prop_nouns,adjs,advs,verbs)

def get_words_simple(text):
    """
    Simple word extractor. Removes punctuation at ends of words, and
    capitalization at beginnings of sentences.
    """
    # Words that should be lowercased if at the beginning of a sentence
    with open("lowercase.txt") as lcfile:
        lowercase = set(lcfile.read().decode("utf8").split())
        
    # General purpose word mapper
    mapper = WordMapper(*wordmap_files)

    # start pooping words
    for sent in sent_tokenize(text):
        for wx, w in enumerate(re.findall('[a-zA-Z0-9\'-]+',sent)):
            if re.match('^[0-9]+$',w): #no numerals
                continue
            if wx==0:
                # Uncap if only the first letter is capped.
                if w.lower() in lowercase:
                    result = w.lower()
                else:
                    result = w
            else:
                result = w
            yield mapper.map(result)
            
def main(
        infile_name,
        num_result=50, 
        norm_case=True,
        tag_pos=True
        ):

    ## Get the various filtering sets
    with open("blacklist.txt") as blfile:
        blacklist = set(blfile.read().decode("utf8").split())
    stopwords = set(nltk.corpus.stopwords.words('english'))
    badwords = blacklist.union(stopwords)

    # Get input text.
    with open(infile_name,'rb') as infile:
        text = infile.read().decode('utf8')
    # get rid of URLs
    text = re_url.sub('',text)
    
    if (tag_pos):
        words = get_words_posfilter(text,norm_case)
    else:
        words = get_words_simple(text)

    filtered = (w for w in words if w not in badwords)

    counter = Counter(filtered)

    for tally in counter.most_common(num_result):
        print(u"{} :: {}".format(*tally))

if __name__ == "__main__":
    args = docopt(__doc__)
    main(
            infile_name=args['<input_file>'],
            num_result=int(args['--num-words']),
            norm_case=True,
            tag_pos=False
        )
