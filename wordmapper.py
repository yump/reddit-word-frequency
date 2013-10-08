import re

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
