from collections import defaultdict
from datetime import date
import os
from pygit2 import Repository, GIT_SORT_TOPOLOGICAL, GIT_OBJ_COMMIT, GIT_SORT_REVERSE
from cPickle import dump, load

cache_filename = 'repo-stats.pickle'

def defaultdict_int():
    return defaultdict(int)

if not os.path.exists(cache_filename):
    repo = Repository('django')

    data = {
        'additions_by_date_by_author': defaultdict(defaultdict_int),
        'deletions_by_date_by_author': defaultdict(defaultdict_int),
    }

    count = 0

    last_commit = None
    for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):
        # commit.author.email
        if count > 5000:
            break
        count += 1
        if commit.type == GIT_OBJ_COMMIT:
            d = repo.diff(commit, last_commit)
            patches = list(d)
            additions = sum([p.additions for p in patches])
            deletions = sum([p.deletions for p in patches])
            data['additions_by_date_by_author'][date.fromtimestamp(commit.commit_time)][commit.author.email] += additions
            data['additions_by_date_by_author'][date.fromtimestamp(commit.commit_time)][commit.author.email] += deletions
        last_commit = commit

    with open(cache_filename, 'w') as f:
        dump(data, f)
else:
    with open(cache_filename) as f:
        data = load(f)

