# Reddit Word Frequency Utilities

## get_comment_text.py

    get_comment_text.py: scrape comment text from reddit.
    
    Usage:
        get_comment_text.py user <username> -n num_comments
        get_comment_text.py subreddit [options] <subreddit_name> -n num_posts
    
    Options:
        -n --num=<n>      Number of comments, or number of submissions to scrape.
        -s --sort=<type>  Type of sorting to use for subreddit comment scraping.
                          Sort types are: hot, top_year, top_month, top_week,
                          top_day, top_hour. [default: hot]
        -d --descend      Descend into the intially hidden comments.  Very slow.
        -h --help         Help message.
        -v --version      Version information.

## word_frequency.py

    word_frequency.py: Print a list of words that appear most frequently
                       in a file.
    
    Usage:
        word_frequency.py [-n NUM_WORDS] <input_file>
    
    Options:
        -h --help            Show this screen.
        -n --num-words=<n>   Number of most-frequently-used words [default: 25].

## wordfilt.py

    wordfilt.py: Library/utility for preparing text for word frequency analysis.
    
    Usage: ./wordfilt.py [options] <file>
    
    Options:
        -h --help   Show this help

# Dependencies:

## Python Modules:

* praw
* nltk
* docopt

## NLTK packages

install with `python -m nltk.downloader stopwords punkt wordnet`

### Required

corpora::stopwords  
models::punkt

### Optional

corpora::wordnet


