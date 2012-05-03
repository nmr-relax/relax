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

# relax module imports.
from relax_errors import RelaxError


class Class_container:
    """This class is used to process and store all of the user function class information."""

    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user function classes.
        self.title = None



class Container:
    """An empty container object."""



class Uf_container(object):
    """This class is used to process and store all of the user function specific information.

    @ivar title:            The long title of the user function.
    @ivar title_short:      The optional short title.
    @ivar args:             The list of argument details.
    @ivar backend:          The user function back end.  This should be a string version with full module path of the function which executes the back end.  For example 'generic_fns.pipes.create'.  Note, this should be importable as __import__(backend)!
    @ivar desc:             The full, multi-paragraph description.
    @ivar prompt_examples:  The examples of how to use the prompt front end.
    """

    # The list of modifiable objects (anything else will be rejected to prevent coding errors).
    self.__mod_attr__ = [
            'title',
            'title_short',
            'backend',
            'desc',
            'prompt_examples'
    ]


    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user functions.
        self.title = None
        self.title_short = None
        self.args = []
        self.backend = None
        self.desc = None
        self.prompt_examples = None


    def __setattr__(self, name, value):
        """Override the class __setattr__ method.

        @param name:    The name of the attribute to modify.
        @type name:     str
        @param value:   The new value of the attribute.
        @type value:    anything
        """

        # Test if the attribute that is trying to be set is modifiable.
        if not name in self.__mod_attr__:
            raise RelaxError("The object '%s' is not a modifiable attribute." % name)

        # Set the attribute normally.
        self.__dict__[name] = value


    def add_keyarg(self, name=None, default=None, py_type='str', desc=None, desc_short=None, can_be_none=False):
        """Wrapper method for adding keyword argument information to the container.

        @keyword name:          The name of the argument.
        @type name:             str
        @keyword default:       The default value of the argument.
        @type default:          anything
        @keyword py_type:       The Python object type that the argument must match (taking the can_be_none flag into account).
        @type py_type:          str
        @keyword desc:          The long human-readable description of the argument.
        @type desc:             str
        @keyword desc_short:    The optional short human-readable description of the argument.
        @type desc_short:       str or None
        @keyword can_be_none:   A flag which specifies if the argument is allowed to have the None value.
        @type can_be_none:      bool
        """

        # Append a new argument dictionary to the list, and alias it.
        self.args.append({})
        arg = self.args[-1]

        # Add the data.
        arg['name'] = name
        arg['default'] = default
        arg['py_type'] = py_type
        arg['desc'] = desc
        arg['desc_short'] = desc_short
        arg['can_be_none'] = can_be_none
