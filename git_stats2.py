import os
from collections import defaultdict
from datetime import date
from cPickle import dump, load
from pygit2 import Repository, GIT_SORT_TOPOLOGICAL, GIT_OBJ_COMMIT

repo_name = 'django'


def read_sha_set_list_txt(filename):
    try:
        with open(filename) as f:
            return set([x.strip() for x in f.readlines()])
    except IOError:
        return set()


whitelist_commits = read_sha_set_list_txt('whitelist-%s.txt' % repo_name)
blacklist_commits = read_sha_set_list_txt('blacklist-%s.txt' % repo_name)


def defaultdict_int():
    return defaultdict(int)


def get_and_update_repo_cache(repo_path):
    cache_filename = '%s-stats.cache' % repo_path
    if os.path.exists(cache_filename):
        with open(cache_filename) as f:
            data = load(f)
    else:
        data = {
            'author_to_month_to_additions': defaultdict(defaultdict_int),
            'author_to_month_to_deletions': defaultdict(defaultdict_int),
            'latest_sha': None,
        }

    repo = Repository(repo_path)

    count = 0
    for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
        count += 1
        if commit.type == GIT_OBJ_COMMIT:
            if data['latest_sha'] == commit.hex:
                break
        
            if not commit.message.startswith('Merge'):
                try:
                    d = repo.diff('%s^' % commit.hex, commit)
                except KeyError:
                    # First commit!
                    break
                patches = list(d)
                additions = sum([p.additions for p in patches])
                deletions = sum([p.deletions for p in patches])
                if additions > 1000 and deletions < 5 and commit.hex not in whitelist_commits:
                    if commit.hex not in blacklist_commits:
                        print 'WARNING: ignored %s looks like an embedding of a lib (message: %s)' % (commit.hex, commit.message)
                if additions > 5000 and commit.hex not in whitelist_commits:
                    if commit.hex not in blacklist_commits and additions != deletions:  # Guess that if additions == deletions it's a big rename of files
                        print 'WARNING: ignored %s because it is bigger than 5k lines. Put this commit in the whitelist or the blacklist' % commit.hex
                    continue
                month = date.fromtimestamp(commit.commit_time)
                month = date(month.year, month.month, 1)
                data['author_to_month_to_additions'][commit.author.email][month] += additions
                data['author_to_month_to_deletions'][commit.author.email][month] += deletions
                if data['latest_sha'] is None:
                    data['latest_sha'] = commit.hex

    with open(cache_filename, 'w') as f:
        dump(data, f)

    return data


def write_series_file(series_name, series_data):
    with open('%s.js' % series_name, 'w') as output:
        output.write('var %s = [' % series_name)
        for author, date_to_number in series_data.items():
            data_points = ', \n'.join(['[Date.UTC(%s, %s, %s), %s]' % (day.year, day.month - 1, day.day, number) for day, number in sorted(date_to_number.items())])
            output.write("""{name: '%s', data: [%s]},""" % (author, data_points))
        output.write('];')


def main():
    data = get_and_update_repo_cache('django')
    write_series_file('additions', data['author_to_month_to_additions'])
    write_series_file('deletions', data['author_to_month_to_deletions'])


if __name__ == '__main__':
    main()
