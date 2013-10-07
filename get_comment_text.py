#!/usr/bin/env python
"""get_comment_text.py: scrape comment text from reddit.

Usage:
    get_comment_text.py user <username> -n num_comments
    get_comment_text.py subreddit <subreddit_name> -n num_posts [-s sort_type]

Options:
    -n --num=<n>      Number of comments, or number of submissions to scrape.
    -s --sort=<type>  Type of sorting to use for subreddit comment scraping.
                      Sort types are: hot, top_year, top_month, top_week,
                      top_day, top_hour. [default: hot]
    -h --help         Help message.
    -v --version      Version information.
"""

from docopt import docopt
import praw
import sys
import itertools

version="get_comment_text v0.2"
user_agent="I thought what I'd do was I'd scrape some Reddit comments."

def wrap_praw_it(it,get_more=False):
    """
    comments objects can return a praw.objects.MoreComments, if there
    are too many comments to display on one page.  This is not what is
    supposed to happen when you reach the end of an iterable, so this
    generator snuffs that behavior.
    """    
    for obj in praw.helpers.flatten_tree(it):
        if type(obj) != praw.objects.MoreComments:
            yield obj
        elif get_more:
            for inner_obj in wrap_praw_it(obj.comments(update=True)):
                yield inner_obj

def get_subreddit_comments(subreddit_name,sort="hot",num_posts=50):
    conn = praw.Reddit(user_agent=user_agent)
    sub = conn.get_subreddit(subreddit_name)

    if sort == "hot":
        postings = sub.get_hot(limit=num_posts)
    elif sort == "top_all":
        postings = sub.get_top_from_all(limit=num_posts)
    elif sort == "top_year":
        postings = sub.get_top_from_year(limit=num_posts)
    elif sort == "top_month":
        postings = sub.get_top_from_month(limit=num_posts)
    elif sort == "top_week":
        postings = sub.get_top_from_week(limit=num_posts)
    elif sort == "top_day":
        postings = sub.get_top_from_day(limit=num_posts)
    elif sort == "top_hour":
        postings = sub.get_top_from_hour(limit=num_posts)
    else:
        raise ValueError("Sort must be one of {hot, top_all, top_year,"
                "top_month, top_week, top_day, top_hour}.")

    comment_gengen = (
            (
                c.body
                for c in wrap_praw_it(p.comments,get_more=True)
            )
            for p in postings 
            )

    return itertools.chain.from_iterable(comment_gengen)

def get_user_comments(
        redditor_name, 
        num_comments
        ):

    ## Retrieve posts from reddit
    conn = praw.Reddit(user_agent=user_agent)
    posts = conn.get_redditor(redditor_name).get_comments(limit=num_comments)

    # Make one big blob of text from the posts.
    return (post.body for post in posts)

if __name__ == "__main__":
    args = docopt(__doc__,version=version)

    if args['user']:
        comgen = get_user_comments(
                redditor_name=args['<username>'], 
                num_comments=int(args['--num'])
            )
    elif args['subreddit']:
        comgen = get_subreddit_comments(
                args['<subreddit_name>'],
                sort=args['--sort'],
                num_posts=args['--num']
            )

    for comment in comgen:
        print(comment.encode('utf8'))
        print('\n')