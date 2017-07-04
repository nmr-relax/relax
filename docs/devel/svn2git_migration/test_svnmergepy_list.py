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
from re import search
from svn.local import LocalClient
import sys

# Script module imports.
from base_fns import extract_current_branch, generate_commit_key, translate


# The repository checkout.
REPO = "/data/relax/gna/repository_backup/git_migration/svn_cleanup_co"

# Init.
commits = {}
merges = []

# The repository.
repo = LocalClient(REPO)

# Process the log.
log = {}
revisions = []
for commit in repo.log_default(changelist=True):
    log[commit.revision] = commit
    revisions.append(commit.revision)

# Loop over the log.
for revision in revisions:
    commit = log[revision]

    # Not a svnmerge.py commit.
    if commit.msg == None or not search("^Merged revisions .* via svnmerge from \nsvn\+ssh", commit.msg):
        continue

    # Generate the commit key.
    commit_key = generate_commit_key(commit)

    # Extract the merge branch.
    merged_branch = commit_key.split("/svn/relax/")[-1]
    merged_branch = merged_branch.split(" ")[0]
    if search("^branches", merged_branch):
        merged_branch = merged_branch.split("/")[1]

    # Extract the merged branch.
    merge_branch = extract_current_branch(commit)

    # Extract the last merged commit.
    rev_parent2 = commit_key.split(" via svnmerge from")[0]
    rev_parent2 = rev_parent2.split(" ")[-1]
    rev_parent2 = rev_parent2.split("-")[-1]
    rev_parent2 = int(rev_parent2.split(",")[-1])

    # The commit key for the last merged commit.
    parent_2 = None
    if rev_parent2 in log.keys():
        parent_2 = generate_commit_key(log[rev_parent2])

    # Store the data.
    commits[commit.revision] = {}
    commits[commit.revision]['broken'] = False
    commits[commit.revision]['merge_branch'] = translate(merge_branch)
    commits[commit.revision]['merged_branch'] = translate(merged_branch)
    commits[commit.revision]['merge_commit'] = commit_key
    commits[commit.revision]['rev_parent1'] = None
    commits[commit.revision]['parent_1'] = None
    commits[commit.revision]['rev_parent2'] = rev_parent2
    commits[commit.revision]['parent_2'] = parent_2
    merges.append(commit.revision)

# Find the first parent commits.
for revision in merges:
    # Extract the merged branch.
    merged_branch = extract_current_branch(log[revision])

    # Walk backwards to the last commit on the same branch.
    walk = list(range(revision))
    walk.reverse()
    for rev_parent1 in walk:
        if rev_parent1 in log and extract_current_branch(log[rev_parent1]) == merged_branch:
            break
    if rev_parent1 == 0:
        continue

    # The commit key for the last merged commit.
    parent_1 = generate_commit_key(log[rev_parent1])

    # Store the commit.
    commits[revision]['rev_parent1'] = rev_parent1
    commits[revision]['parent_1'] = parent_1

# Validate the second parent commits.
for revision in merges:
    # Walk backwards to the last commit on the same branch.
    walk = list(range(commits[revision]['rev_parent2']+1))
    walk.reverse()
    for rev_parent2 in walk:
        if rev_parent2 in log and extract_current_branch(log[rev_parent2]) == commits[revision]['merged_branch']:
            break
    if rev_parent2 == 0:
        continue

    # Check for a mismatch.
    if commits[revision]['rev_parent2'] == rev_parent2:
        continue

    # The commit key for the last merged commit.
    parent_2 = generate_commit_key(log[rev_parent2])

    # Store the commit.
    commits[revision]['broken'] = True
    commits[revision]['rev_parent2'] = rev_parent2
    commits[revision]['parent_2'] = parent_2

# Sanity check.
for revision in merges:
    if None in [revision, commits[revision]['rev_parent1'], commits[revision]['rev_parent2']]:
        raise NameError("No commit found for r%s: %s" % (revision, commits[revision]))

# Merge list write out.
file = sys.stdout
file.write("SVNMERGEPY_MERGES_BROKEN = [\n")
for revision in merges:
    if commits[revision]['broken']:
        file.write("    [\"%s\", \"%s\",\n" % (commits[revision]['merge_branch'], commits[revision]['merged_branch']))
        file.write("        \"r%s\", \"%s\",\n" % (revision, commits[revision]['merge_commit']))
        file.write("        \"r%s\", \"%s\",\n" % (commits[revision]['rev_parent1'], commits[revision]['parent_1']))
        file.write("        \"r%s\", \"%s\",\n" % (commits[revision]['rev_parent2'], commits[revision]['parent_2']))
        file.write("    0, 0, 0],\n")
file.write("]\n")
