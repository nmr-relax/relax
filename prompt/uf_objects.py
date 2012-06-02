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
"""The special auto-generated user function and class objects."""

# relax module imports.
import arg_check
from prompt.uf_docstring import bold_text, build_subtitle, create_table, format_text
from prompt.help import relax_class_help
from relax_errors import RelaxError
from relax_string import strip_lead
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


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
        self._desc = desc


    def __repr__(self):
        """Replacement function for displaying an instance of this user function class."""

        # Return a description.
        return "<The %s user function class object>" % self._name


    def _build_doc(self):
        """Create the user function class documentation.

        @return:    The user function class documentation to use in the help system.
        @rtype:     str
        """

        # Initialise.
        doc = ""

        # The title.
        doc += build_subtitle("The %s user function class." % self._name, start_nl=False)

        # The synopsis.
        doc += build_subtitle("Synopsis")
        doc += self._desc
        doc += "\n\n"

        # Usage help string.
        doc += build_subtitle("Usage")
        doc += format_text(relax_class_help)
        doc += "\n"

        # Add a description to the help string.
        if hasattr(self, '__description__'):
            doc += build_subtitle("Description")
            doc += "\n\n%s\n" % strip_lead(self.__description__)

        # The member user functions.
        doc += build_subtitle("Contents")
        doc += "This class contains the following user functions:\n\n"
        for uf_name, uf in uf_info.uf_loop(self._name):
            # The unformatted text.
            text = "    %s:  %s" % (uf_name, uf.title)

            # Format.
            text = format_text(text)

            # Replace the arg text with bold text.
            length = 7 + len(uf_name)
            text = "    %s:  %s" % (bold_text(uf_name), text[length:])

            # Add to the docstring.
            doc += "%s\n" % text

        # Return the documentation.
        return doc



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
        if status.uf_intro:
            # Convert the keys and values.
            keys = []
            values = []
            for i in range(self._karg_num):
                keys.append(self._kargs[i]['name'])
                values.append(uf_kargs[self._kargs[i]['name']])

            # The printout.
            print(self._intro_text(keys, values))

        # Check the argument values.
        for i in range(self._karg_num):
            # Aliases.
            value = uf_kargs[self._kargs[i]['name']]
            arg = self._kargs[i]
            py_type = arg['py_type']
            desc_short = arg['desc_short']
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
                arg_check.is_float_array(value, desc_short, size=dim, can_be_none=can_be_none)
            elif py_type == 'float_matrix':
                arg_check.is_float_matrix(value, desc_short, dim=dim, can_be_none=can_be_none)
            elif py_type == 'func':
                arg_check.is_func(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'int':
                arg_check.is_int(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'int_list':
                arg_check.is_int_list(value, desc_short, size=dim, can_be_none=can_be_none)
            elif py_type == 'int_or_int_list':
                arg_check.is_int_or_int_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty, none_elements=none_elements)
            elif py_type == 'list':
                arg_check.is_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'none':
                arg_check.is_none(value, desc_short)
            elif py_type == 'num':
                arg_check.is_num(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'num_list':
                arg_check.is_num_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'num_or_num_tuple':
                arg_check.is_num_or_num_tuple(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'num_tuple':
                arg_check.is_num_tuple(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str':
                arg_check.is_str(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'str_list':
                arg_check.is_str_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str_list_of_lists':
                arg_check.is_str_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty, list_of_lists=True)
            elif py_type == 'str_or_inst':
                arg_check.is_str_or_inst(value, desc_short, can_be_none=can_be_none)
            elif py_type == 'str_or_num_or_str_num_list':
                arg_check.is_str_or_num_or_str_num_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str_or_num_list':
                arg_check.is_str_or_num_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'str_or_str_list':
                arg_check.is_str_or_str_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'tuple':
                arg_check.is_tuple(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            elif py_type == 'val_or_list':
                arg_check.is_val_or_list(value, desc_short, size=dim, can_be_none=can_be_none, can_be_empty=can_be_empty)
            else:
                raise RelaxError("The Python object type '%s' is unknown." % py_type)

        # Execute the functional code.
        self._backend(*new_args, **uf_kargs)


    def __init__(self, name, title=None, kargs=None, backend=None, desc=None):
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
         """

        # Store the args.
        self._name = name
        self._title = title
        self._kargs = kargs
        self._backend = backend
        self._desc = desc

        # Check the args.
        if title == None:
            raise RelaxError("The title must be given.")

        # Generate fixed keyword argument data structures (for faster execution).
        self._karg_num = len(self._kargs)
        self._karg_names = []
        for i in range(self._karg_num):
            self._karg_names.append(self._kargs[i]['name'])


    def __repr__(self):
        """Replacement function for displaying an instance of this user function class."""

        # Return a description.
        return "<The %s user function>" % self._name


    def _build_doc(self):
        """Create the user function documentation.

        @return:    The user function documentation to use in the help system.
        @rtype:     str
        """

        # Checks.
        if not isinstance(self._desc, list):
            raise RelaxError("The user function 'desc' variable must be a list of Desc_container instances.")
        for i in range(len(self._desc)):
            if not isinstance(self._desc[i], Desc_container):
                raise RelaxError("The user function 'desc' list element '%s' must be a list of Desc_container instances." % self._desc[i])

        # Initialise.
        doc = ""

        # The title.
        doc += build_subtitle("The %s user function." % self._name, start_nl=False)

        # The synopsis.
        doc += build_subtitle("Synopsis")
        doc += "%s" % self._title
        doc += "\n\n"

        # The defaults.
        doc += build_subtitle("Defaults")
        keys = []
        values = []
        for i in range(self._karg_num):
            keys.append(self._kargs[i]['name'])
            values.append(self._kargs[i]['default'])
        doc += "%s" % self._intro_text(keys, values, prompt=False)
        doc += "\n\n"

        # Add the keyword args.
        if self._kargs != None:
            doc += build_subtitle("Keyword Arguments")
            for i in range(len(self._kargs)):
                # The unformatted text.
                text = "    %s:  %s" % (self._kargs[i]['name'], self._kargs[i]['desc'])

                # Format.
                text = format_text(text)

                # Replace the arg text with bold text.
                length = 7 + len(self._kargs[i]['name'])
                text = "    %s:  %s" % (bold_text(self._kargs[i]['name']), text[length:])

                # Add to the docstring.
                doc += "%s\n" % text

        # Add the description sections.
        if isinstance(self._desc, list) and len(self._desc):
            # Loop over the sections.
            for i in range(len(self._desc)):
                # The title.
                doc += build_subtitle(self._desc[i].get_title())

                # Loop over the elements.
                for type, element in self._desc[i].element_loop():
                    # A paragraph or verbatim text.
                    if type == 'paragraph':
                        doc += format_text(element) + '\n'

                    # Verbatim text.
                    elif type == 'verbatim':
                        doc += element + '\n\n'

                    # A list.
                    elif type == 'list':
                        # Loop over the list elements.
                        for j in range(len(element)):
                            doc += format_text("    - %s" % element[j])

                        # Final newline.
                        doc += '\n'

                    # An itemised list.
                    elif type == 'item list':
                        # Loop over the list elements.
                        for j in range(len(element)):
                            # No item.
                            if element[j][0] in [None, '']:
                                doc += format_text("    %s" % element[j][1])
                            else:
                                doc += format_text("    %s:  %s" % (element[j][0], element[j][1]))

                        # Final newline.
                        doc += '\n'

                    # A table.
                    elif type == 'table':
                        doc += create_table(element) + '\n'

                    # A prompt example.
                    elif type == 'prompt':
                        # Loop over the prompt examples.
                        for j in range(len(element)):
                            doc += format_text(element[j])

                        # Final double newline.
                        doc += '\n\n'

        # Return the documentation.
        return doc


    def _intro_text(self, keys, values, prompt=True):
        """Build and return the user function intro text.

        @param keys:        The user function keys.
        @type keys:         list of str
        @param values:      The values corresponding to the keys.
        @type values:       list
        @keyword prompt:    A flag which if True will cause the prompt text to be included.
        @type prompt:       bool
        @return:            The user function intro text.
        @rtype:             str
        """

        # Initialise.
        text = ""

        # The prompt.
        if prompt:
            text += status.ps3

        # The user function name.
        text += "%s(" % self._name

        # The keyword args.
        for i in range(len(keys)):
            # Comma separation.
            if i >= 1:
                text += ", "

            # Add the arg.
            text += "%s=%s" % (keys[i], repr(values[i]))

        # The end.
        text += ")"

        # Wrap the text.
        text = format_text(text)

        # Return the text.
        return text
