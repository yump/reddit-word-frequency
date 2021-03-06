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

"""get_comment_text.py: scrape comment text from reddit.

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
"""

from docopt import docopt
import praw
import sys
import itertools
import time

version="get_comment_text v0.2"
user_agent="I thought what I'd do was I'd scrape some Reddit comments."

class ProgressInd:
    def __init__(self):
        self.starttime = time.time()
    def set(self,level):
        rem = 1.0 - level
        elapsed = time.time() - self.starttime
        try:
            rate = level/elapsed
            eta = rem/rate
        except ZeroDivisionError:
            eta = 1000000.0
        sys.stderr.write("   \r{:.2%} ".format(level))
        sys.stderr.write("Elapsed: {} Eta: {}".format(
            self.time_format(elapsed),
            self.time_format(eta)
            )
            )
    def complete(self):
        sys.stderr.write("\n")
    def time_format(self,seconds):
        minutes = seconds // 60.0
        seconds = seconds % 60.0
        hours = minutes // 60.0
        minutes = minutes % 60.0
        return "{:.0f}:{:02.0f}:{:02.0f}".format(hours,minutes,seconds)


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

def get_subreddit_comments(
        subreddit_name,
        sort="hot",
        num_posts=50,
        follow_more=False
        ):
    if follow_more:
        sys.stderr.write("Warning: descending into hidden comments is slow.\n")
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

    def comment_gen():
        progress = ProgressInd()
        for px,p in enumerate(postings):
            num_comments = p.num_comments
            for cx,c in enumerate(wrap_praw_it(p.comments,follow_more)):
                yield c.body
                progress.set( (1.0*cx/num_comments + px)/num_posts )
        progress.complete()

    return comment_gen()

def get_user_comments(
        redditor_name, 
        num_comments
        ):

    ## Retrieve posts from reddit
    conn = praw.Reddit(user_agent=user_agent)
    posts = conn.get_redditor(redditor_name).get_comments(limit=num_comments)
    
    ## generator over posts
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
                num_posts=int(args['--num']),
                follow_more=args['--descend']
            )

    for comment in comgen:
        print(comment.encode('utf8'))
        print('\n')
