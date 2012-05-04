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
    """This class is used to process and store all of the user function class information.

    @ivar title:            The user function class description.
    """

    # The list of modifiable objects (anything else will be rejected to prevent coding errors).
    __mod_attr__ = [
            'title'
    ]

    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user function classes.
        self.title = None


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



class Container:
    """An empty container object."""



class Uf_container(object):
    """This class is used to process and store all of the user function specific information.

    @ivar title:            The long title of the user function.
    @type title:            str
    @ivar title_short:      The optional short title.
    @type title_short:      str or None
    @ivar kargs:            The list of keyword argument details.
    @type kargs:            list of dict
    @ivar backend:          The user function back end.  This should be a string version with full module path of the function which executes the back end.  For example 'generic_fns.pipes.create'.  Note, this should be importable as __import__(backend)!
    @type backend:          executable object
    @ivar desc:             The full, multi-paragraph description.
    @type desc:             str
    @ivar prompt_examples:  The examples of how to use the prompt front end.
    @type prompt_examples:  str or None
    """

    # The list of modifiable objects (anything else will be rejected to prevent coding errors).
    __mod_attr__ = [
            'title',
            'title_short',
            'kargs',
            'backend',
            'desc',
            'prompt_examples'
    ]


    def __init__(self):
        """Initialise all the data."""

        # Initialise the variables for all user functions.
        self.title = None
        self.title_short = None
        self.kargs = []
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


    def add_keyarg(self, name=None, default=None, py_type=None, desc_short=None, desc=None, can_be_none=False):
        """Wrapper method for adding keyword argument information to the container.

        @keyword name:          The name of the argument.
        @type name:             str
        @keyword default:       The default value of the argument.
        @type default:          anything
        @keyword py_type:       The Python object type that the argument must match (taking the can_be_none flag into account).
        @type py_type:          str
        @keyword desc_short:    The short human-readable description of the argument.  This is used, for example, in the RelaxError messages to refer to the argument.
        @type desc_short:       str
        @keyword desc:          The long human-readable description of the argument.
        @type desc:             str
        @keyword can_be_none:   A flag which specifies if the argument is allowed to have the None value.
        @type can_be_none:      bool
        """

        # Check that the args have been properly supplied.
        if name == None:
            raise RelaxError("The 'name' argument must be supplied.")
        if py_type == None:
            raise RelaxError("The 'py_type' argument must be supplied.")
        if desc_short == None:
            raise RelaxError("The 'desc_short' argument must be supplied.")
        if desc == None:
            raise RelaxError("The 'desc' argument must be supplied.")

        # Append a new argument dictionary to the list, and alias it.
        self.kargs.append({})
        arg = self.kargs[-1]

        # Add the data.
        arg['name'] = name
        arg['default'] = default
        arg['py_type'] = py_type
        arg['desc'] = desc
        arg['desc_short'] = desc_short
        arg['can_be_none'] = can_be_none
