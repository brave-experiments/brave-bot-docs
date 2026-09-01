#!/usr/bin/env python3
"""Track how far behind brave-bot this documentation site has fallen.

Everything on this site describes behaviour specified clause by clause in brave-bot's
`docs/specs`. `docs-updated-to-sha` at the repository root records the brave-bot commit
the site has been brought up to, so an update knows where to start reading rather than
re-reading the whole history.

This script is the deterministic half of the update-docs skill. It resolves the brave-bot
checkout, reports what has landed since the recorded commit, and rewrites the record. No
model is involved, so its output is reproducible and cheap.

The brave-bot checkout is found, in order:

    $BRAVE_BOT_REPO
    ../brave-bot, beside this repository

Usage:
    python3 agents/skills/update-docs/docs-ref.py show
    python3 agents/skills/update-docs/docs-ref.py changes [--all] [--full]
    python3 agents/skills/update-docs/docs-ref.py set <rev>
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# .../<repo>/agents/skills/update-docs/docs-ref.py -> parents[3] == <repo>
_ROOT = Path(__file__).resolve().parents[3]
_REF_FILE = _ROOT / 'docs-updated-to-sha'

_SOURCE_URL = 'https://github.com/brave-experiments/brave-bot'
_SHA = re.compile(r'^[0-9a-f]{40}$')

# A behaviour change is supposed to arrive with the spec clause that governs it, so these
# are the paths that can make this site wrong. Code changes under crates/ matter only
# through their specs, and `--all` is there for when that assumption needs checking.
_DOC_PATHS = ['docs/', 'README.md']


class Problem(Exception):
    """Anything the user has to fix, reported without a traceback."""


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(['git', '-C', str(repo), *args],
                            capture_output=True,
                            text=True)
    if result.returncode != 0:
        raise Problem(f'git {" ".join(args)} failed in {repo}:\n'
                      f'{result.stderr.strip()}')
    return result.stdout.strip()


def _source_repo() -> Path:
    env = os.environ.get('BRAVE_BOT_REPO')
    candidate = Path(env).expanduser() if env else _ROOT.parent / 'brave-bot'
    if not (candidate / '.git').exists():
        raise Problem(
            f'No brave-bot checkout at {candidate}.\n'
            f'Clone it beside this repository:\n'
            f'    git clone {_SOURCE_URL}.git {_ROOT.parent / "brave-bot"}\n'
            f'or point BRAVE_BOT_REPO at an existing one.')
    return candidate.resolve()


def read_ref() -> str:
    """The recorded sha: the last line that is neither blank nor a comment."""
    if not _REF_FILE.is_file():
        raise Problem(f'{_REF_FILE.name} is missing.')
    lines = [
        line.strip() for line in _REF_FILE.read_text().splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]
    if not lines:
        raise Problem(f'{_REF_FILE.name} records no sha.')
    sha = lines[-1]
    if not _SHA.match(sha):
        raise Problem(f'{_REF_FILE.name} holds {sha!r}, not a 40 character sha.')
    return sha


def write_ref(sha: str, subject: str, date: str) -> None:
    """Rewrite the record, keeping the commit link in step with the sha."""
    _REF_FILE.write_text(f'''# The brave-bot commit this documentation is current as of.
#
# Everything on this site describes behaviour specified clause by clause in brave-bot's
# docs/specs. This file records how far along that history the site has been brought, so
# the next update knows where to start reading.
#
# Run `make docs-changes` to see what has landed since, and the update-docs skill
# (agents/skills/update-docs) to fold it in. The skill rewrites the sha below; nothing
# else should.
#
# {subject}
# {date}
# {_SOURCE_URL}/commit/{sha}

{sha}
''')


def _describe(repo: Path, rev: str) -> tuple[str, str, str]:
    """(sha, date, subject) for one revision, or a Problem if it is unknown here."""
    try:
        line = _git(repo, 'log', '-1', '--format=%H%x00%cs%x00%s', rev)
    except Problem:
        raise Problem(
            f'{rev} is not a commit in {repo}.\n'
            f'If it is newer than this checkout, fetch first: git -C {repo} fetch')
    sha, date, subject = line.split('\0')
    return sha, date, subject


def _resolve_head(repo: Path) -> str:
    """Prefer the fetched upstream main over whatever the checkout happens to be on.

    A local checkout is frequently mid-branch, and the site tracks what has been
    published, not somebody's work in progress.
    """
    for rev in ('origin/main', 'main', 'HEAD'):
        try:
            return _git(repo, 'rev-parse', '--verify', f'{rev}^{{commit}}')
        except Problem:
            continue
    raise Problem(f'Cannot resolve a head commit in {repo}.')


def show(_args) -> int:
    repo = _source_repo()
    ref = read_ref()
    ref_sha, ref_date, ref_subject = _describe(repo, ref)
    head_sha, head_date, head_subject = _describe(repo, _resolve_head(repo))

    behind = _git(repo, 'rev-list', '--count', f'{ref_sha}..{head_sha}')
    doc_behind = _git(repo, 'rev-list', '--count', f'{ref_sha}..{head_sha}', '--',
                      *_DOC_PATHS) if behind != '0' else '0'

    print(f'brave-bot checkout   {repo}')
    print(f'docs current as of   {ref_sha[:9]}  {ref_date}  {ref_subject}')
    print(f'brave-bot head       {head_sha[:9]}  {head_date}  {head_subject}')
    print(f'link                 {_SOURCE_URL}/commit/{ref_sha}')
    print()
    if behind == '0':
        print('Up to date.')
    else:
        print(f'{behind} commit(s) behind, {doc_behind} of them touching '
              f'{" or ".join(_DOC_PATHS)}.')
        print('Run `make docs-changes` to see them.')
    return 0


def changes(args) -> int:
    repo = _source_repo()
    ref_sha, _, _ = _describe(repo, read_ref())
    head_sha, _, _ = _describe(repo, _resolve_head(repo))
    span = f'{ref_sha}..{head_sha}'

    if ref_sha == head_sha:
        print(f'Up to date at {ref_sha[:9]}. Nothing to fold in.')
        return 0

    paths = [] if args.all else _DOC_PATHS
    scope = 'every path' if args.all else ' or '.join(_DOC_PATHS)
    print(f'brave-bot {ref_sha[:9]}..{head_sha[:9]}, commits touching {scope}, oldest first')
    print(f'new ref once folded in: {head_sha}')
    print()

    count = 0
    for record in _git(repo, 'log', '--reverse', '--no-merges',
                       '--format=%H%x00%cs%x00%s', span, '--', *paths).splitlines():
        if not record.strip():
            continue
        sha, date, subject = record.split('\0')
        count += 1
        print(f'{sha[:9]}  {date}  {subject}')
        if args.full:
            body = _git(repo, 'log', '-1', '--format=%b', sha).strip()
            for line in body.splitlines():
                print(f'    {line}')
            files = _git(repo, 'show', '--name-status', '--format=', sha, '--', *paths)
            for line in files.splitlines():
                print(f'    | {line}')
            print()

    if not count:
        print('(none)')
    else:
        print()
        print(f'{count} commit(s). Files changed across all of them:')
        for line in _git(repo, 'diff', '--name-status', span, '--',
                         *paths).splitlines():
            print(f'  {line}')

    if not args.all:
        total = _git(repo, 'rev-list', '--count', '--no-merges', span)
        if int(total) > count:
            print()
            print(f'({int(total) - count} further commit(s) touched only code or tests. '
                  f'Re-run with --all if a spec was missed.)')
    return 0


def set_ref(args) -> int:
    repo = _source_repo()
    sha, date, subject = _describe(repo, args.rev)
    previous = read_ref()
    if sha == previous:
        print(f'Already recorded at {sha[:9]}. Nothing written.')
        return 0
    write_ref(sha, subject, date)
    print(f'{_REF_FILE.name}: {previous[:9]} -> {sha[:9]}  {date}  {subject}')
    print(f'{_SOURCE_URL}/commit/{sha}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('show', help='Where the docs stand against brave-bot.')

    p_changes = sub.add_parser('changes', help='What has landed since the recorded commit.')
    p_changes.add_argument('--all',
                           action='store_true',
                           help='Every commit, not only those touching docs.')
    p_changes.add_argument('--full',
                           action='store_true',
                           help='Include commit bodies and per-commit file lists.')

    p_set = sub.add_parser('set', help='Record a new commit as the docs baseline.')
    p_set.add_argument('rev', help='A sha, tag, or ref resolved in the brave-bot checkout.')

    args = parser.parse_args()
    handler = {'show': show, 'changes': changes, 'set': set_ref}.get(args.command or 'show')

    try:
        return handler(args)
    except Problem as e:
        print(f'error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
