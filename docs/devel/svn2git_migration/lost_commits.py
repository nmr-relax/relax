#! /usr/bin/env python3
###############################################################################
#                                                                             #
# Copyright (C) 2017 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from os import chdir
from re import search
from subprocess import PIPE, Popen
from svn.local import LocalClient

# Script module imports.
from base_fns import extract_current_branch, generate_commit_key, get_git_commits


# The repositories.
SVN_REPO = "/data/relax/gna/repository_backup/git_migration/svn_cleanup_co"
GIT_REPO = "/data/relax/gna/repository_backup/git_migration/gitsvn_manual/repo_final"

# Init.
svn_commits = []

# The repository.
svn_repo = LocalClient(SVN_REPO)

# Process the svn log.
svn_file = open('lost_commits.svn.log', 'w')
#for commit in svn_repo.log_default(changelist=True, revision_to=1000):
for commit in svn_repo.log_default(changelist=True):
    # Extract the merged branch.
    merge_branch = extract_current_branch(commit)
    if merge_branch == 'website':
        continue

    # Generate the commit key.
    commit_key = generate_commit_key(commit)

    # Store the data.
    svn_commits.append(commit_key)
    if not search("^Dummy commit to replace", commit_key):
        svn_file.write("%s\n" % repr(commit_key))
svn_file.close()

# Get the git commits.
git_file = open('lost_commits.git.log', 'w')
chdir(GIT_REPO)
git_commits = get_git_commits()
#git_commits.reverse()
for git_commit in git_commits:
    git_file.write("%s\n" % repr(git_commit))
git_file.close()

# Loop over the git commits and remove them from the svn commit list.
for git_commit in git_commits:
    # No SVN commmit?!?
    if git_commit not in svn_commits:
        print("Git commit not present in SVN: \"%s\"" % git_commit)
        continue

    # Remove the first matching commit.
    svn_commits.pop(svn_commits.index(git_commit))

# Missing commit printouts.
print("\n\nMissing SVN commits:")
for commit in svn_commits:
    if not search("^Dummy commit to replace", commit):
        print(commit)
