###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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

# Dependencies.
import dep_check

# Python module imports.
from os import F_OK, access, sep
PIPE, Popen = None, None
if dep_check.subprocess_module:
    from subprocess import PIPE, Popen

# relax module imports.
import lib.structure.internal.object
from status import Status; status = Status()


version = "repository checkout"
repo_revision = None
repo_url = None


def repo_information():
    """Determine the subversion revision number and URL from svn or git-svn copies of the repository."""

    # The global variables
    global repo_revision
    global repo_url

    # The variables are already set, so do nothing.
    if repo_revision != None or repo_url != None:
        return

    # Python 2.3 and earlier.
    if Popen == None:
        return

    # The command to use.
    cmd = None
    if access(status.install_path+sep+'.svn', F_OK):
        cmd = 'svn info %s' % status.install_path
    elif access(status.install_path+sep+'.git', F_OK):
        cmd = 'cd %s; git svn info' % status.install_path

    # Not a repository copy, so do nothing.
    if not cmd:
        return

    # Open the pipe and run the command.
    pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

    # Loop over the output lines.
    for line in pipe.stdout.readlines():
        # Decode Python 3 byte arrays.
        if hasattr(line, 'decode'):
            line = line.decode()

        # Split up the line.
        row = line.split()

        # Store revision as the global variable.
        if len(row) and row[0] == 'Revision:':
            repo_revision = str(row[1])

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
    if ver == 'repository checkout':
        # The global variables
        global repo_revision
        global repo_url

        # Change the version string.
        if repo_revision != None:
            ver = version + " r" + repo_revision
        if repo_url != None:
            ver = ver + " " + repo_url

    # Return the version.
    return ver


# Fetch the repository information, if present.
repo_information()

# Set the version in the relax internal structural object.
lib.structure.internal.object.RELAX_VERSION = version_full()
