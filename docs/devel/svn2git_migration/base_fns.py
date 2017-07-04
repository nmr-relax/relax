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
from subprocess import PIPE, Popen
from svn.local import LocalClient
import sys


def exec_cmd(cmd):
    """Shell command execution function."""

    # Printout.
    print("$ %s" % cmd)

    # Exec.
    pipe = Popen("%s 2>&1" % cmd, shell=True, stdout=PIPE, close_fds=False)

    # Printouts.
    for line in pipe.stdout.readlines():
        sys.stdout.write(line.decode())


def extract_current_branch(commit):
    """Determine the branch the commit belongs to."""

    # Nothing to check.
    if len(commit.changelist) == 0:
        return None

    # The first change.
    change = commit.changelist[0][1]

    # Catch the website.
    if search("^/website", change):
        return "website"

    # Trunk commits.
    for trunk in ["0.1", "0.2", "0.3", "1.0", "1.1", "1.2", "1.3", "trunk"]:
        if search("^/%s" % trunk, change):
            return trunk

    # Branch.
    if search("^/branches/", change):
        return change.split("/")[2]


def find_hash(text=None, hashes={}, hash_index=0):
    """Determine the git hash for the first line of the commit message."""

    # No hash.
    if text not in hashes:
        print_error("Cannot find the hash corresponding to the commit text \"%s\"." % text)
        return

    # Get the hashes.
    matches = hashes[text]

    # Multiple hash warning.
    if len(matches) > 1:
        print_warning("Multiple hashes present, selecting index %i from %s - for commit line \"%s\"." % (hash_index, matches, text))

    # Return the hash.
    return matches[hash_index]


def find_unmerged(merges=None, false_pos=None):
    """Find any possible unmerged commits."""

    # Loop over the git log.
    pipe = Popen("git log --all --pretty=format:'%s (%cd) xxxxxxxxxx %H %P xxxxxxxxxx %H %d %s (%cd) <%an>' --date=iso", shell=True, stdout=PIPE, close_fds=False)
    print("\n\nPossible unmerged commits:\n")
    for line in pipe.stdout.readlines():
        # Split up the line.
        commit_key, hashes, msg = line.decode().split(' xxxxxxxxxx ')
        msg = msg.strip()

        # Already in the merges list.
        known = False
        for i in range(len(merges)):
            if merges[i][3] == commit_key:
                known = True
        if known:
            continue

        # Find possible merge commits.
        if not search("[Mm]erg", msg):
            continue

        # Already merged.
        if len(hashes.split()) == 3:
            continue

        # Known false positives.
        false_pos_flag = False
        for text in false_pos:
            if search(text, msg):
                false_pos_flag = True
                break
        if false_pos_flag:
            continue

        # Printout.
        print(msg)


def generate_commit_key(commit):
    """Generate the identifying commit key for the commit."""

    # Format the date.
    date = "%s +0000" % (commit.date.strftime("%Y-%m-%d %H:%M:%S"))

    # The first line of the commit message.
    head = ''
    msg = []
    if commit.msg:
        msg = commit.msg.strip().split('\n')
    for i in range(len(msg)):
        if msg[i].strip() == '':
            break
        if i > 0 and head[-1] != ' ' and msg[i][0] != ' ':
            head += " "
        head += msg[i]

    # Head text modifications.
    head = head.strip()
    head = head.replace("\"", "\\\"")
    head = head.replace("\\n", "\\\\n")

    # Return the key.
    return "%s (%s)" % (head, date)


def get_git_commits():
    """Get all the git hashes and first commit lines for the repository."""

    # Exec.
    pipe = Popen("git log --all --pretty=format:'%s xxxxxx (%cd)' --date=iso", shell=True, stdout=PIPE, close_fds=False)

    # Get the data.
    commits = []
    for line in pipe.stdout.readlines():
        head, date = line.decode().split(' xxxxxx ')

        # Head text modifications.
        head = head.strip()
        head = head.replace("\"", "\\\"")
        head = head.replace("\\n", "\\\\n")

        # The commit key.
        commits.append("%s %s" % (head, date.strip()))

    # Return the data structure.
    return commits


def get_hashes():
    """Get all the git hashes and first commit lines for the repository."""

    # Init.
    hashes = {}

    # Exec.
    pipe = Popen("git log --all --pretty=format:'%H xxxxxxxxxx %s (%cd)' --date=iso", shell=True, stdout=PIPE, close_fds=False)

    # Get the data.
    for line in pipe.stdout.readlines():
        # Split up the line.
        hash, msg = line.decode().split(' xxxxxxxxxx ')
        msg = msg[:-1]

        # Store the data.
        if msg not in hashes:
            hashes[msg] = [hash]
        else:
            hashes[msg].append(hash)

    # Return the data structure.
    return hashes


def print_error(text):
    """Standardised error printout."""

    print("SCRIPT ERROR:  %s" % text)


def print_warning(text):
    """Standardised warning printout."""

    print("SCRIPT WARNING:  %s" % text)


def translate(branch):
    """Translate the branch name of 'trunk' to 'master'."""

    # Perform the svn to git name translation.
    if branch == 'trunk':
        return "master"
    else:
        return branch
