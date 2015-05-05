# git-stats2

Generate nice graphs of statistics from a git repository. The name is to make it clear that I aim to have a good replacement for GitStats (http://gitstats.sourceforge.net).

Differences from GitStats:

- I've removed stats that are uninteresting (changes per week, per month, etc)
- Much faster (~100 seconds for django on my laptop, vs ~300 for GitStats)
- Prettier output with JS-based interactive charts (with more than say 5 contributors this makes the output a lot more usable)
- Partial updates (cache old collected data and then rerun to update the statistics with the new changes since the last run)
- Features to clean up the data:
  - Aliases for different emails used by the same person
  - Avoids commits that looks like embedded libs or other batch updates
  - Blacklist/whitelist of commits to include or exclude in the collection
  
## Usage

```
brew install libgit2
pip install pygit2
python git_stats2.py <repo>
open graph.html
```