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
from os import chdir, mkdir, path
from shutil import rmtree
from subprocess import PIPE, Popen
import sys


# The revisions or ranges to eliminate.
SKIP = [
    [76],
    [1523, 2093],
    [2097],
    [2202],
    [2392],
    [2427],
    [2576, 2577],
    [2787, 2789],
    [2842],
    [3380, 3381],
    [4206],
    [5090],
    [5275],
    [5729],
    [6105],
    [6260],
    [6355],
    [6739, 'rdc_analysis'],
    [7079],
    [7311],
    [7498],
    [8094],
    [8636],
    [9025],
    [9201],
    [10757],
    [11857],
    [12553],
    [12593],
    [12596],
    [12781],
    [12839],
    [14344],
    [14389],
    [14421],
    [15208],
    [16818],
    [17182],
    [17202],
    [17779],
    [19006],
    [19166, 'relax_disp'],
    [20626],
    [21661, 21662],
    [22646],
    [23601, 23602],
    [24665],
    [24705],
    [24894],
    [25572],
    [26871],
    [27967],
]

# Paths.
SVN_REPO = "/data/relax/gna/repository_backup/svnrepo"
LOAD_DIR = "/data/relax/gna/repository_backup/git_migration"


def exec_cmd(cmd):
    """Shell command execution function."""

    # Printout.
    print("$ %s" % cmd)

    # Exec.
    pipe = Popen("%s 2>&1" % cmd, shell=True, stdout=PIPE, close_fds=False)

    # Printouts.
    for line in pipe.stdout.readlines():
        sys.stdout.write(line.decode())


# Setup.
chdir(LOAD_DIR)
if path.exists("svn_cleanup"):
    rmtree("svn_cleanup")
if path.exists("svn_cleanup_co"):
    rmtree("svn_cleanup_co")
exec_cmd("svnadmin create svn_cleanup")

# Loop over the ranges to apply.
prev_commit = 0
for i in range(len(SKIP) + 1):
    # The revision range for the commits prior to those to skip.
    if i == len(SKIP):
        pre_rev_range = "r%s:28307" % prev_commit
    else:
        pre_rev_range = "r%s:%s" % (prev_commit, SKIP[i][0]-1)

    # Load the earlier commits.
    exec_cmd("svnadmin load svn_cleanup -%s < ../relax.dump" % pre_rev_range)

    # Finish.
    if i == len(SKIP):
        break

    # Skip range.
    if len(SKIP[i]) == 2 and isinstance(SKIP[i][1], int):
        skip_range = range(SKIP[i][0], SKIP[i][1]+1)
    else:
        skip_range = range(SKIP[i][0], SKIP[i][0]+1)

    # Repository checkout.
    if not path.exists("svn_cleanup_co"):
        exec_cmd("svn co file://%s/svn_cleanup svn_cleanup_co" % LOAD_DIR)
    chdir(LOAD_DIR + '/svn_cleanup_co')

    # Loop over each skipped commit.
    for j in range(len(skip_range)):
        exec_cmd("svn up")

        # Handle duplicated branches.
        if len(SKIP[i]) == 2 and isinstance(SKIP[i][1], str):
            # Backup the first copy of the duplicated branch.
            exec_cmd("svn mv branches/%s branches/%s_old" % (SKIP[i][1], SKIP[i][1]))
            exec_cmd("svn ci -m \"Keeping a copy of the original '%s' branch.\"" % SKIP[i][1])

            # Skip the dummy commits.
            continue

        # Dummy commit directory.
        if not path.exists("dummy_commits"):
            mkdir("dummy_commits")
            exec_cmd("svn add dummy_commits")

        # Dummy commit file.
        file_path = "dummy_commits/r%s" % skip_range[j]
        text = "Dummy commit to replace r%s." % skip_range[j]
        file = open(file_path, 'w')
        file.write(text)
        file.write('\n')
        file.close()
        exec_cmd("svn add %s" % file_path)
        exec_cmd("svn ci -m \"%s\"" % text)

    # Return to base directory.
    chdir(LOAD_DIR)

    # Store the first commit for the next range.
    if len(SKIP[i]) == 2 and isinstance(SKIP[i][1], int):
        prev_commit = SKIP[i][1] + 1
    else:
        prev_commit = SKIP[i][0] + 1
