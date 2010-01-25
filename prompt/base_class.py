###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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
"""The base class for all the user function classes."""

# relax module imports.
import help
from string import split, strip



class Basic_class:
    def __init__(self, exec_info=None):
        """All non-user function classes.

        @keyword exec_info: The execution information container.  This must contain at least the exec_info.intro boolean variable.  If not supplied, an instance will be generated.
        @type exec_info:    None or class instance
        """

        # Generate the execution info container.
        if exec_info == None:
            exec_info = Exec_info()

        # Store the execution info container.
        self.exec_info = exec_info



class Exec_info:
    """Container for execution information."""

    # The hard-coded prompts (to change the Python prompt, as well as the function print outs).
    ps1 = 'relax> '
    ps2 = 'relax| '
    ps3 = '\nrelax> '

    def __init__(self):
        """Initialise the data of this container.

        This includes the introduction flag as well as the strings to change the Python prompts.
        """

        # The user function intro flag.
        self.intro = True



class User_fn_class:
    def __init__(self, exec_info=None):
        """Initialise the user function class, compiling the help string.

        @keyword exec_info: The execution information container.  This must contain at least the exec_info.intro boolean variable.  If not supplied, an instance will be generated.
        @type exec_info:    None or class instance
        """

        # Generate the execution info container.
        if exec_info == None:
            exec_info = Exec_info()

        # Store the execution info container.
        self.exec_info = exec_info

        # Add the generic help string.
        self.__relax_help__ = self.__doc__ + "\n" + help.relax_class_help

        # Add a description to the help string.
        if hasattr(self, '__description__'):
            self.__relax_help__ = self.__relax_help__ + "\n\n" + self.__strip_lead(self.__description__)


    def __strip_lead(self, text):
        """Strip the leading whitespace from the given text.

        @param text:    The text to strip the leading whitespace from.
        @type text:     str
        @return:        The text with leading whitespace removed.
        @rtype:         str
        """

        # Split by newline.
        lines = split(text, '\n')

        # Find the minimum whitespace.
        min_white = 1000
        for line in lines:
            # Empty lines.
            if strip(line) == '':
                continue

            # Count the whitespace for the current line.
            num_white = 0
            for i in range(len(line)):
                if line[i] != ' ':
                    break
                num_white = num_white + 1

            # The min value.
            min_white = min(min_white, num_white)

        # Strip the whitespace.
        new_text = ''
        for line in lines:
            new_text = new_text + line[min_white:] + '\n'

        # Return the new text.
        return new_text
