import os
from collections import defaultdict
from datetime import date
from cPickle import dump, load
from pygit2 import Repository, GIT_SORT_TOPOLOGICAL, GIT_OBJ_COMMIT, GIT_SORT_REVERSE

cache_filename = 'repo-stats.pickle'

limit_number_of_commits = None


def defaultdict_int():
    return defaultdict(int)

if not os.path.exists(cache_filename):
    repo = Repository('django')

    data = {
        'author_to_date_to_additions': defaultdict(defaultdict_int),
        'author_to_date_to_deletions': defaultdict(defaultdict_int),
    }

    count = 0

    last_commit = None
    for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
        if commit.type == GIT_OBJ_COMMIT:
            if limit_number_of_commits is not None and count > limit_number_of_commits:
                break
            count += 1
            d = repo.diff(commit, last_commit)
            patches = list(d)
            additions = sum([p.additions for p in patches])
            deletions = sum([p.deletions for p in patches])
            data['author_to_date_to_additions'][commit.author.email][date.fromtimestamp(commit.commit_time)] += additions
            data['author_to_date_to_deletions'][commit.author.email][date.fromtimestamp(commit.commit_time)] += deletions
            last_commit = commit

    with open(cache_filename, 'w') as f:
        dump(data, f)
else:
    with open(cache_filename) as f:
        data = load(f)

with open('series.js', 'w') as output:
    output.write('var series = [')
    for author, date_to_additions in data['author_to_date_to_additions'].items():
        data_points = ', \n'.join(['[Date.UTC(%s, %s, %s), %s]' % (day.year, day.month - 1, day.day, additions) for day, additions in date_to_additions.items()])
        output.write("""{name: '%s', data: [%s]},""" % (author, data_points))
    output.write('];')