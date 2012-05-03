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
"""The module of all the objects used to hold the user function details."""


class Class_container:
    """This class is used to process and store all of the user function class information."""

    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user function classes.
        self.title = None



class Container:
    """An empty container object."""



class Uf_container:
    """This class is used to process and store all of the user function specific information."""

    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user functions.
        self.title = None
        self.title_short = None
        self.args = []
        self.desc = None
        self.prompt_examples = None


    def add_arg(self, name=None, desc=None, desc_short=None):
        """Wrapper method for adding argument information to the container.

        @keyword name:          The name of the argument.
        @type name:             str
        @keyword desc:          The long human-readable description of the argument.
        @type desc:             str
        @keyword desc_short:    The optional short human-readable description of the argument.
        @type desc_short:       str or None
        """

        # Append a new argument dictionary to the list, and alias it.
        self.args.append({})
        arg = self.args[-1]

        # Add the data.
        arg['name'] = name
        arg['desc'] = desc
        arg['desc_short'] = desc_short
