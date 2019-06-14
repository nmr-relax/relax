###############################################################################
#                                                                             #
# Copyright (C) 2006,2009,2012-2014,2017-2018 Edward d'Auvergne               #
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

# Module docstring.
"""Module for relax version information."""

# Python module imports.
from os import F_OK, access, sep
try:
    from subprocess import PIPE, Popen
except ImportError:
    PIPE, Popen = None, None

# relax module imports.
from lib.compat import SYSTEM
import lib.structure.internal.object
from status import Status; status = Status()


version = "4.1.3"
repo_head = None
repo_type = None
repo_url = None


def repo_information():
    """Determine the subversion revision number and URL from svn or git-svn copies of the repository."""

    # The global variables
    global repo_head
    global repo_type
    global repo_url

    # The variables are already set, so do nothing.
    if repo_head != None or repo_type != None or repo_url != None:
        return

    # Python 2.3 and earlier.
    if Popen == None:
        return

    # Command separator.
    symbol = ";"
    if SYSTEM == 'Windows' or SYSTEM == 'Microsoft':
        symbol = "&&"

    # The command to use.
    cmd = None
    if access(status.install_path+sep+'.git'+sep+'svn'+sep+'refs', F_OK):
        cmd = 'cd %s %s git svn info' % (status.install_path, symbol)
        repo_type = 'git-svn'
    elif access(status.install_path+sep+'.git', F_OK):
        cmd = 'cd %s %s git rev-parse HEAD %s git remote -v' % (status.install_path, symbol, symbol)
        repo_type = 'git'
    elif access(status.install_path+sep+'.svn', F_OK):
        cmd = 'svn info %s' % status.install_path
        repo_type = 'svn'

    # Not a repository copy, so do nothing.
    if not cmd:
        return

    # Open the pipe and run the command.
    pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

    # Loop over the output lines.
    lines = pipe.stdout.readlines()
    for i in range(len(lines)):
        # Decode Python 3 byte arrays.
        if hasattr(lines[i], 'decode'):
            lines[i] = lines[i].decode()

        # Git info.
        if repo_type == 'git':
            # Git hash.
            if i == 0:
                repo_head = lines[i].strip()
                continue

            # Remote URL.
            if repo_url:
                repo_url += '\n'
            else:
                repo_url = ''
            remote_info = lines[i].split()
            repo_url += "%s %s" % (remote_info[1], remote_info[2])

        # SVN and git-svn.
        else:
            # Split up the line.
            row = lines[i].split()

            # Store revision as the global variable.
            if len(row) and row[0] == 'Revision:':
                repo_head = str(row[1])

            # Store URL as the global variable.
            if len(row) and row[0] == 'URL:':
                repo_url = str(row[1])


def version_full():
    """Return the full relax version, including all SVN info for repository versions.

    @return:    The relax version string.
    @rtype:     str
    """

    # The relax version.
    ver = version

    # Repository version.
    if ver == 'repository commit':
        # The global variables
        global repo_head
        global repo_type
        global repo_url

        # Change the version string.
        if repo_head != None:
            if repo_type == 'git':
                ver = version + " " + repo_head
            else:
                ver = version + " r" + repo_head
        if repo_url != None:
            ver += " " + repo_url.replace('\n', '; ')

    # Return the version.
    return ver


# Fetch the repository information, if present.
repo_information()

# Set the version in the relax internal structural object.
lib.structure.internal.object.RELAX_VERSION = version_full()
