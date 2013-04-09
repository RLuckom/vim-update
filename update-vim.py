#!/usr/bin/env python

import os
import git
import sys
from git.exc import GitCommandError


def update_vim(vim_dir=None):
    """interactively git-pulls in subdirectories of ~/.vim/bundle

    @type vim_dir: str
    @param vim_dir: path to ~/.vim/bundle. Note that ~ will not be
                    expanded correctly
    """
    if vim_dir is None:
        vim_dir = '{}/.vim/bundle'.format(os.environ['HOME'])
    bundles = os.listdir(vim_dir)
    for bundle in bundles:
        if os.path.isdir(os.path.join(vim_dir, bundle)):
            try:
                repo = git.Repo(os.path.join(vim_dir, bundle))
                update_if_requested(repo, bundle)
            except GitCommandError, e:
                if str(e).find('unable to connect') != -1:
                    e = str(e).split("'")[1][:-1]
                    print e
                    sys.exit(1)


def update_if_requested(rpo, name, searched_submodules=None):
    """recursively searches repos and submodules, asking whether to update.

    @type rpo: git.Repo
    @param rpo: top-level repo to search
    @type name: str
    @param name: name of repo
    @type searched_submodules: list
    @param searched_submodules: list of names of previously-searched submodules
    """
    if searched_submodules is None:
        searched_submodules = []
    local_sha = rpo.head.commit.hexsha
    try:
        remote_sha = rpo.remote().fetch()[0].commit.hexsha
    except AssertionError:
        print 'likely caused by rebased / merged upstream'
        raise
    if local_sha != remote_sha:
        query = 'Update repository {} [y or n]? : '.format(name)
        choice = str(raw_input(query))
        if choice in ['y', 'Y', 'yes', 'Yes']:
            pull_repo_changes(rpo)
        else:
            print 'Skipping {}.'.format(name)
    elif rpo.submodules == []:
        print 'No update necessary in {}'.format(name)
    for mod in rpo.submodules:
        if mod.name not in searched_submodules:
            searched_submodules.append(mod.name)
            mod_name = mod.name.split('/')[-1]
            full_name = '{}, submodule of {}'.format(mod_name, name)
            update_if_requested(mod.repo, full_name, searched_submodules)
        else:
            print 'No update necessary in {}'.format(name)


def pull_repo_changes(repo):
    """pulls down changes, stashes / pops if necessary

    @type repo: git.Repo
    @param repo: repo to update
    """
    try:
        if repo.is_dirty():
            print 'stashing changes.'
            repo.git.add('-u')
            repo.git.stash('save')
            print 'pulling changes'
            repo.remote().pull()
            print 'restoring stashed changes'
            repo.git.stash('pop')
            pass
        else:
            print 'pulling changes'
            repo.remote().pull()
    except:
        raise

if __name__ == '__main__':
    update_vim()
