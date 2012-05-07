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
"""Module containing the special objects for auto-generating the user functions and classes."""

# relax module imports.
import arg_check
from prompt.base_class import _bold_text, _build_subtitle, _format_text, _strip_lead
from prompt.help import relax_class_help
from relax_errors import RelaxError
from status import Status; status = Status()


class Class_container(object):
    """The container for created the user function class objects."""

    def __init__(self, name, desc):
        """Set up the container.

        @param name:    The name of the user function class.
        @type name:     str
        @param desc:    The description to be presented by the help system.
        @type desc:     str
        """

        # Store the args.
        self._name = name

        # Build the relax help system string.
        self.__relax_help__ = desc
        self.__relax_help__ += "\n%s" % relax_class_help

        # Add a description to the help string.
        if hasattr(self, '__description__'):
            self.__relax_help__ += "\n\n%s" % _strip_lead(self.__description__)


    def __repr__(self):
        """Replacement function for displaying an instance of this user function class."""

        # Return a description.
        return "<The %s user function class object>" % self._name



class Uf_object(object):
    """The object for auto-generating the user functions."""

    def __call__(self, *uf_args, **uf_kargs):
        """Make the user function executable."""

        # Check the keyword args.
        keys = uf_kargs.keys()
        for name in keys:
            # Unknown keyword.
            if name not in self._karg_names:
                raise RelaxError("The keyword argument '%s' is unknown." % name)

        # Convert the args to keyword args if needed.
        num_args = len(uf_args)
        new_args = []
        if num_args:
            for i in range(num_args):
                # Check if the keyword is already assigned.
                if self._kargs[i]['name'] in keys:
                    raise RelaxError("The argument '%s' and the keyword argument '%s' cannot both be supplied." % (uf_args[i], self._kargs[i]['name']))

                # Add the arg as a keyword arg.
                uf_kargs[self._kargs[i]['name']] = uf_args[i]

        # Set the argument defaults.
        for i in range(self._karg_num):
            # The keyword.
            name = self._kargs[i]['name']

            # Set the default if the user has not supplied a value.
            if name not in uf_kargs.keys():
                uf_kargs[name] = self._kargs[i]['default']

        # Function intro text.
        if status.prompt_intro:
            # The prompt and user function name.
            text = "%s%s(" % (status.ps3, self._name)

            # The keyword args.
            for i in range(len(self._kargs)):
                # Comma separation.
                if i >= 1:
                    text += ", "

                # Add the arg.
                text += "%s=%s" % (self._kargs[i]['name'], repr(uf_kargs[self._kargs[i]['name']]))

            # The end.
            text += ")"

            # Print out.
            print(text)

        # Check the argument values.
        for i in range(self._karg_num):
            # Aliases.
            value = uf_kargs[self._kargs[i]['name']]
            arg = self._kargs[i]
            py_type = arg['py_type']
            desc_short = arg['desc_short']
            size = arg['size']
            dim = arg['dim']
            can_be_none = arg['can_be_none']
            can_be_empty = arg['can_be_empty']
            none_elements = arg['none_elements']

            # Check if the correct Python object type has been supplied.
            if py_type == 'bool':
                arg_check.is_bool(value, desc_short)
            elif py_type == 'float':
                arg_check.is_float(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'float_array':
                arg_check.is_float_array(value, desc_short, size=size, can_be_none=can_be_none)
            elif py_type == 'float_matrix':
                arg_check.is_float_matrix(value, desc_short, dim=dim, can_be_none=can_be_none)
            elif py_type == 'func':
                arg_check.is_func(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'int':
                arg_check.is_int(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'int_list':
                arg_check.is_int(value, desc_short, size=size, can_be_none=can_be_none)
            elif py_type == 'int_or_int_list':
                arg_check.is_int_or_int_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty, none_elements=none_elements)
            elif py_type == 'list':
                arg_check.is_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'none':
                arg_check.is_none(value, desc_short)
            elif py_type == 'num':
                arg_check.is_num(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'num_list':
                arg_check.is_num_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'num_or_num_tuple':
                arg_check.is_num_or_num_tuple(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'num_tuple':
                arg_check.is_num_tuple(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str':
                arg_check.is_str(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'str_list':
                arg_check.is_str_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str_list_of_lists':
                arg_check.is_str_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty, list_of_lists=True)
            elif py_type == 'str_or_inst':
                arg_check.is_str_or_inst(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'str_or_num_or_str_num_list':
                arg_check.is_str_or_num_or_str_num_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str_or_num_list':
                arg_check.is_str_or_num_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str_or_str_list':
                arg_check.is_str_or_str_list(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'tuple':
                arg_check.is_tuple(value, desc_short, size=size, can_be_none=can_be_none, can_be_empty=can_be_empty)
            else:
                raise RelaxError("The Python object type '%s' is unknown." % py_type)

        # Execute the functional code.
        self._backend(*new_args, **uf_kargs)


    def __init__(self, name, title=None, kargs=None, backend=None, desc=None, examples=None, additional=None):
        """Set up the object.

        @param name:            The name of the user function.
        @type name:             str
        @keyword title:         The long title of the user function.
        @type title:            str
        @keyword kargs:         The list of keyword argument details.
        @type kargs:            list of dict
        @keyword backend:       The user function back end.  This should be a string version with full module path of the function which executes the back end.  For example 'generic_fns.pipes.create'.  Note, this should be importable as __import__(backend)!
        @type backend:          executable object
        @keyword desc:          The full, multi-paragraph description.
        @type desc:             str
        @keyword examples:      The examples of how to use the prompt front end.
        @type examples:         str or None
        @keyword additional:    The examples of how to use the prompt front end.
        @type additional:       list of str or None
         """

        # Store the args.
        self._name = name
        self._title = title
        self._kargs = kargs
        self._backend = backend
        self._desc = desc
        self._examples = examples
        self._additional = additional

        # Check the args.
        if title == None:
            raise RelaxError("The title must be given.")

        # Generate fixed keyword argument data structures (for faster execution).
        self._karg_num = len(self._kargs)
        self._karg_names = []
        for i in range(self._karg_num):
            self._karg_names.append(self._kargs[i]['name'])

        # Build the user function documentation.
        self._build_doc()


    def __repr__(self):
        """Replacement function for displaying an instance of this user function class."""

        # Return a description.
        return "<The %s user function>" % self._name


    def _build_doc(self):
        """Create the user function documentation."""

        # Initialise.
        self.__relax_help__ = ""

        # Add the title.
        self.__relax_help__ = "%s%s\n" % (self.__relax_help__, _bold_text(self._title))

        # Add the keyword args.
        if self._kargs != None:
            self.__relax_help__ += _build_subtitle("Keyword Arguments")
            for i in range(len(self._kargs)):
                # The text.
                text = "%s:  %s" % (self._kargs[i]['name'], self._kargs[i]['desc'])

                # Format.
                text = _format_text(text)

                # Add to the docstring.
                self.__relax_help__ = "%s%s\n" % (self.__relax_help__, text)

        # Add the description.
        if self._desc != None:
            self.__relax_help__ += _build_subtitle("Description")
            self.__relax_help__ += _format_text(self._desc)

        # Add the examples.
        if self._examples != None:
            self.__relax_help__ += '\n%s' % _build_subtitle("Examples")
            self.__relax_help__ += _format_text(self._examples)

        # Add the additional sections.
        if self._additional != None:
            # Loop over each section.
            for i in range(len(self._additional)):
                self.__relax_help__ += '\n%s' % _build_subtitle(self._additional[i][0])
                self.__relax_help__ += _format_text(self._additional[i][1])
