###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""Conversion functions for python objects to GUI strings and back."""

# Python module imports.
from math import pow
from numpy import ndarray

# relax module imports.
from compat import u
from status import Status; status = Status()


def bool_to_gui(bool):
    """Convert the bool into the GUI string.

    @param bool:    The boolean value of True or False.
    @type bool:     bool
    @return:        The GUI string.
    @rtype:         unicode
    """

    # Convert.
    return unicode(bool)


def convert_to_float(string):
    """Method to convert a string like '1.02*1e-10' to a float variable.

    @param string:  The number in string form.
    @type string:   str or unicode
    @return:        The floating point number.
    @rtype:         float
    """

    # Break the number up.
    entries = string.split('*')

    # The first part of the number.
    a = entries[0]
    a = float(a)

    # The second part of the number.
    b = entries[1]
    b = float(b[2:len(b)])

    # Recombine.
    result = a * pow(10, b)

    # Return the float.
    return result


def float_to_gui(num):
    """Convert the float into the GUI string.

    @param num:     The number in float or None form.
    @type num:      float or None
    @return:        The GUI string.
    @rtype:         unicode
    """

    # No input.
    if num == None:
        num = ''

    # Convert.
    return unicode(num)


def gui_to_bool(string):
    """Convert the GUI obtained string to a bool.

    @param string:  The bool in string form.
    @type string:   str or unicode
    @return:        The bool.
    @rtype:         bool
    """

    # No value.
    if string in ['', u(''), None]:
        return None

    # Convert.
    return eval(string)


def gui_to_float(string):
    """Convert the GUI obtained string to an float.

    @param string:  The number in string form.
    @type string:   str or unicode
    @return:        The float
    @rtype:         float or None
    """

    # No input.
    if string in ['', u(''), None]:
        return None

    # Already a float.
    if isinstance(string, float):
        return string

    # Convert.
    val = eval(string)

    # An int.
    if isinstance(val, int):
        val = float(val)

    # Not a float!
    if not isinstance(val, float):
        return string

    # A float.
    return val


def gui_to_int(string):
    """Convert the GUI obtained string to an int.

    @param string:  The number in string form.
    @type string:   str or unicode
    @return:        The integer
    @rtype:         int or None
    """

    # No input.
    if string in ['', u(''), None]:
        return None

    # Already an int.
    if isinstance(string, int):
        return string

    # Convert.
    try:
        val = eval(string)
    except:
        val = None

    # Not an int!
    if not isinstance(val, int):
        return string

    # An int.
    return val


def gui_to_int_or_list(string):
    """Convert the GUI obtained string to a list.

    @param string:  The list in string form.
    @type string:   str or unicode
    @return:        The integer or list of integers.
    @rtype:         int or int list
    """

    # No value.
    if string in ['', u(''), None]:
        return None

    # Already an int or list.
    if isinstance(string, int) or isinstance(string, list):
        return string

    # Convert.
    try:
        val = eval(string)

    # Failure, so return the original value.
    except NameError:
        return string


    # Return the list.
    return val


def gui_to_list(string):
    """Convert the GUI obtained string to a list.

    @param string:  The list in string form.
    @type string:   str or unicode
    @return:        The list.
    @rtype:         list
    """

    # No value.
    if string in ['', u(''), None]:
        return []

    # Convert.
    val = eval(string)
    if not isinstance(val, list):
        val = [val]

    # Return the list.
    return val


def gui_to_py(string):
    """Super function for converting the GUI string to a Python object.

    @param string:  The Python object in string form.
    @type string:   str or unicode
    @return:        The value.
    @rtype:         python object
    """

    # No value.
    if string in ['', u(''), None]:
        return None

    # Use an eval call to create a standard object.
    try:
        value = eval(string)

    # A string or sequence of strings.
    except:
        value = str(string)

    # Return the python type.
    return value


def gui_to_str(string):
    """Convert the GUI obtained string to a string.

    @param string:  The number in string form.
    @type string:   str or unicode
    @return:        The string.
    @rtype:         str
    """

    # No value.
    if string in ['', u(''), None]:
        return None

    # Convert.
    return str(string)


def gui_to_str_or_list(string):
    """Convert the GUI obtained string to a list.

    @param string:  The list in string form.
    @type string:   str or unicode
    @return:        The integer or list of integers.
    @rtype:         int or int list
    """

    # No value.
    if string in ['', u(''), None]:
        return None

    # Try converting to a list.
    try:
        val = eval(string)

    # Catch failures, and try as a string.
    except NameError:
        return str(string)

    # Return the list.
    return val


def gui_to_tuple(string):
    """Convert the GUI obtained string to a tuple.

    @param string:  The list in string form.
    @type string:   str or unicode
    @return:        The list.
    @rtype:         list
    """

    # No value.
    if string in ['', u(''), None]:
        return ()

    # Convert.
    val = eval(string)
    if isinstance(val, list):
        val = tuple(val)
    elif not isinstance(val, tuple):
        val = (val,)

    # Return the list.
    return val


def int_to_gui(num):
    """Convert the int into the GUI string.

    @param num:     The number in int or None form.
    @type num:      int or None
    @return:        The GUI string.
    @rtype:         unicode
    """

    # No input.
    if num == None:
        num = ''

    # Convert.
    return unicode(num)


def list_to_gui(list):
    """Convert the list into the GUI string.

    @param list:    The Python list.
    @type list:     list or None
    @return:        The GUI string.
    @rtype:         unicode
    """

    # No input.
    if list == None:
        list = ''

    # Handle numpy arrays.
    if isinstance(list, ndarray):
        list = list.tolist()

    # Convert.
    return unicode(list)


def nothing(value):
    """Do not convert the value.

    @param value:   A Python value.
    @type value:    float or int or str
    @return:        The unmodified value.
    @rtype:         float or int or str
    """

    # Return, unmodified.
    return value


def py_to_gui(value):
    """Super function for converting a Python object to a GUI string.

    @param value:   The value.
    @type value:    anything
    @return:        The Python object in GUI string form.
    @rtype:         unicode
    """

    # No input.
    if value == None:
        string = ''

    # All other types.
    else:
        string = unicode(value)

    # Return the GUI string.
    return string


def str_to_gui(string):
    """Convert the string into the GUI string.

    @param string:  The string or None to convert.
    @type string:   str or None
    @return:        The GUI string.
    @rtype:         unicode
    """

    # No input.
    if string == None:
        string = ''

    # Convert.
    return unicode(string)


def tuple_to_gui(tuple):
    """Convert the tuple into the GUI string.

    @param tuple:   The Python tuple.
    @type tuple:    tuple or None
    @return:        The GUI string.
    @rtype:         unicode
    """

    # No input.
    if tuple == None:
        tuple = ''

    # Convert.
    return unicode(tuple)
