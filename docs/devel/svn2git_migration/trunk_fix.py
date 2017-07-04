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
from os import chdir, path
from shutil import rmtree

# Script module imports.
from base_fns import exec_cmd, find_hash, get_hashes, print_error, print_warning


# The repositories.
ORIG_REPO = "/data/relax/gna/repository_backup/git_migration/gitsvn_manual/repo_cleanup"
NEW_REPO = "/data/relax/gna/repository_backup/git_migration/gitsvn_manual/repo_trunk_fix"

# Branch head commits.
HEADS = [
    ["1.3", "Removed merge tracking for \"svnmerge\" for svn+ssh://bugman@svn.gna.org/svn/relax/branches/uf_redesign (2012-06-10 15:56:06 +0000)", 1],  # 8829a8d99a17d2e65d5f9c4b4c0c17f45231bbc2
    ["1.2", "Fix for Python >= 2.6. (2010-02-11 18:37:04 +0000)", 0],                                           # b67003aab4ee5eabaf63029929639231df936458
    ["1.1", "Merge of r2348 from 1.0 branch (2006-01-17 10:24:19 +0000)", 0],                                   # 1f755f2760d34f4f810f4fd6779c48efb6eb046b
    ["1.0", "Further fix of the results.read bug (2006-01-17 10:23:10 +0000)", 0],                              # f2f18477b439e2f44484641ae0445f05f5e5cf4f
    ["0.3", "Updating to the archive 'backup_relax_2005-06-14a.tar.bz2'. (2005-06-14 02:48:29 +0000)", 1],      # c403f4277c6f090857569b18ca8f8ffe8d7ebdca
    ["0.2", "Updating to the archive 'backup_mf_2003-02-07.tar.gz'. (2003-02-07 07:20:32 +0000)", 1],           # 1cbbe1c0ecb5d2a1d4d941d2d583e3da69271961
    ["0.1", "Updating to the archive 'backup_modelfree_2001-12-15b.tar.gz'. (2001-12-15 08:16:48 +0000)", 0],   # 663732812ad6954a569697151c59839c5f5ac9f0
]

# The branch information, ordered by reverse svn commit, as all subsequent hashes are renumbered.
# The list format is:  [Merge branch, merged branch, merge svn revision, merge commit msg, parent svn revision, parent commit msg, index 0, index 1]
# The final optional indices are for replicated first line commit messages, for the merge and parent respectively.
MERGES = [
    # Already connected:
    #["master", "1.3",
    #    "r16823", "Creation of the main development line called 'trunk' from the 1.3 line. (2012-06-10 19:13:28 +0000)",                   # 6838ed5e58ba0803a12c6a6a5f65be3a2e71cdbd
    #    "r16819", "Removed merge tracking for \"svnmerge\" for svn+ssh://bugman@svn.gna.org/svn/relax/branches/uf_redesign (2012-06-10 15:56:06 +0000)",# 8829a8d99a17d2e65d5f9c4b4c0c17f45231bbc2
    #0, 1],
    ["1.2", "1.2",
        "r8035", "Manually ported the 1.2.14 tag CHANGES file changes to the 1.2 line. (2008-11-27 10:22:10 +0000)",                        # 7e2aa78b222105d09f5f10e9612e8f9721391127
        "r7786", "Ported r7784 from the 1.3 line.  This is the fix for bug #12456 (https://gna.org/bugs/?12456). (2008-10-16 19:49:57 +0000)",  # 1437535a1d80aef0f2ff264644bb7a0a81eea21e
    0, 1],
    # Already connected:
    #["1.3", "1.2",
    #    "r2506", "Creation of the 1.3 developmental branch for the MPI and any other destabilising changes. (2006-07-06 05:25:51 +0000)",  # a6c1d801d39021aee48ed34e25e1a5f0ec728487
    #    "r2505", "Fix of bug where self.relax.data.select_sim was treated as a list (2006-05-31 08:56:06 +0000)",                          # 8e3716e228d8a4bfa27118393ef5a4d8c6805104
    #0, 1],
    ["1.1", "1.1",
        "r2349", "Merge of r2348 from 1.0 branch (2006-01-17 10:24:19 +0000)",                                                              # 1f755f2760d34f4f810f4fd6779c48efb6eb046b
        "r2334", "Many of the steps in releasing stable relax versions have been shifted into makefiles. (2006-01-14 05:04:54 +0000)",      # cf0a2f51ea3fb399902567b241303a6e658739ba
    0, 1],
    # Already connected:
    #["1.2", "1.1",
    #    "r2335", "Creation of the 1.2 stable branch. (2006-01-14 05:09:00 +0000)",                                                         # 3504701c78feda7bde64db9c1833259a29f31f52
    #    "r2334", "Many of the steps in releasing stable relax versions have been shifted into makefiles. (2006-01-14 05:04:54 +0000)",     # cf0a2f51ea3fb399902567b241303a6e658739ba
    #1, 1],
    ["1.0", "1.0",
        "r2341", "More modifications to the release checklist. (2006-01-14 05:46:51 +0000)",                                                # b4a18cc396530c80cb297e5843afa8c2d7a25b49
        "r2338", "Updated the release checklist. (2006-01-14 05:39:00 +0000)",                                                              # 4b0ed0d21fab9131c1b03ccd835f8e0f5c9a3dec
    0, 1],
    # Already connected:
    #["1.1", "1.0",
    #    "r2301", "Creating an unstable development fork from 1.0 called 1.1. (2006-01-09 04:31:42 +0000)",                                  # 1280a725727e2b7384c7089db27002f709d4586c
    #    "r2300", "A huge number of changes for the relaxation curve fitting functions. (2006-01-09 02:39:10 +0000)",                        # 2d29b01adebbbee979e68ae0aeef8b71cb26189a
    #1, 1],
    #["1.0", "0.3",
    #    "r1522", "Fork of version 0.3 to version 1.0. (2005-06-25 04:39:07 +0000)",                                                         # 7f745e179f0268a2cf61e18fc2250067b5a7d67e
    #    "r1520", "Updating to the archive 'backup_relax_2005-06-14a.tar.bz2'. (2005-06-14 02:48:29 +0000)",                                 # c403f4277c6f090857569b18ca8f8ffe8d7ebdca
    #1, 1],
    #["0.3", "0.2",
    #    "r306", "Fork of version 0.2 to version 0.3. (2003-02-14 11:19:24 +0000)",                                                          # d9c35b2aea6d0ca82bcfb0ba7f27f43cd864ebcd
    #    "r304", "Updating to the archive 'backup_mf_2003-02-07.tar.gz'. (2003-02-07 07:20:32 +0000)",                                       # 1cbbe1c0ecb5d2a1d4d941d2d583e3da69271961
    #0, 1],
    #["0.2", "0.1",
    #    "r77", "Fork of version 0.1 to version 0.2. (2001-12-16 01:07:26 +0000)",                                                           # 1eb0942ee10b0d7d4db840c01aea8bb6f4dc4ae5
    #    "r74", "Updating to the archive 'backup_modelfree_2001-12-15b.tar.gz'. (2001-12-15 08:16:48 +0000)",                                # 663732812ad6954a569697151c59839c5f5ac9f0
    #1, 0],
]


# Copy the repository.
if path.exists(NEW_REPO):
    rmtree(NEW_REPO)
exec_cmd("cp -urp %s %s" % (ORIG_REPO, NEW_REPO))
chdir(NEW_REPO)

# Get the hashes.
hashes = get_hashes()

# Fix the head references.
for branch, commit, hash_index in HEADS:
    print("\n\nFixing head reference for \"%s\"." % branch)

    # Find the hashes.
    commit_hash = find_hash(text=commit, hashes=hashes, hash_index=hash_index)

    # Fix up.
    exec_cmd("git update-ref refs/heads/%s %s" % (branch, commit_hash))

exec_cmd("git reflog expire --expire=now --all")
exec_cmd("git gc --prune=now")
rmtree("%s_init" % NEW_REPO)
exec_cmd("cp -urp %s %s_init" % (NEW_REPO, NEW_REPO))

# Fix the trunk merge points.
for merge_branch, merged_branch, merge_rev, merge_commit, rev_parent, parent, merge_hash_index, parent_hash_index in MERGES:
    print("\n\nMerge \"%s -> %s\"." % (merge_branch, merged_branch))

    # Find the hashes.
    merge_commit_hash = find_hash(text=merge_commit, hashes=hashes, hash_index=merge_hash_index)
    parent_hash = find_hash(text=parent, hashes=hashes, hash_index=parent_hash_index)
    print("%-10s %-6s %s %s" % ("Commit:", merge_rev, merge_commit_hash, merge_commit))
    print("%-10s %-6s %s %s" % ("Parent:", rev_parent, parent_hash, parent))

    # No matches.
    if merge_commit_hash == None or parent_hash == None:
        print_error("One of the hashes cannot be found.")
        continue

    # Fix up.
    exec_cmd("git filter-branch --force --parent-filter 'test $GIT_COMMIT = %s && echo \"-p %s\" || cat' %s --all" % (merge_commit_hash, parent_hash, merge_branch))

    # Clean up.
    exec_cmd("git for-each-ref --format=\"%(refname)\" refs/original/ | xargs -n 1 git update-ref -d")

# Shrink the repository.
exec_cmd("git reflog expire --expire=now --all")
exec_cmd("git gc --prune=now")
