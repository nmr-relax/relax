###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing ANSI escape sequences and helper functions for colour terminal output."""

# Python module imports.
import ctypes
import sys

# The relax prompt.
relax_prompt = "\033[94m"

# RelaxErrors.
relax_error = "\033[31m"

# RelaxWarnings.
relax_warning = "\033[33m"

# Script print out.
script = "\033[36m"

# The terminating sequence.
end = "\033[0m"


def enable_control_chars(stream=1):
    """Helper function for determining if control characters should be printed to the IO streams.

    This uses both the sys.std*.isatty() methods as well as the operating system.  Control characters are only shown on GNU/Linux and Mac OS X (or technically they are disabled on MS Windows as both cmd and the PowerShell do not support the ANSI characters).


    @keyword stream:    The stream to check.  The value of 0 corresponds to STDIN, 1 corresponds to STDOUT, and 2 corresponds to STDERR.
    @type stream:       int
    @return:            The answer of whether color and other control characters should be printed.
    @rtype:             bool
    """

    # MS Windows, therefore always return False.
    if hasattr(ctypes, 'windll'):
        return False

    # The STDIO streams.
    if stream == 0:
        if not hasattr(sys.stdin, 'isatty'):
            return False
        return sys.stdin.isatty()
    elif stream == 1:
        if not hasattr(sys.stdout, 'isatty'):
            return False
        return sys.stdout.isatty()
    elif stream == 2:
        if not hasattr(sys.stderr, 'isatty'):
            return False
        return sys.stderr.isatty()
    else:
        return False
