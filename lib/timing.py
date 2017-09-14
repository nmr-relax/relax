###############################################################################
#                                                                             #
# Copyright (C) 2014,2017 Edward d'Auvergne                                   #
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
"""Module for various timing purposes."""

# Python module imports.
from time import asctime


def print_elapsed_time(time_delta, return_str=False):
    """Print the elapsed time value in day, hour, minute, and second format.

    @param time_delta:      The time value in seconds to format.
    @type time_delta:       float
    @keyword return_str:    A flag which if True will cause the elapsed time string to be returned rather than printed.
    @type return_str:       bool
    @return:                The elapsed time string, if asked for.
    @rtype:                 None or str
    """

    # Initial values.
    sec = 0.0
    min = 0
    hour = 0
    day = 0

    # Divide up the time.
    min, sec = divmod(time_delta, 60)
    if min > 0:
        hour, min = divmod(min, 60)
    else:
        min = 0
    if hour > 0:
        day, hour = divmod(hour, 24)
    else:
        hour = 0

    # Handle single values.
    plural_min = 's'
    plural_hour = 's'
    plural_day = 's'
    if min == 1.0:
        plural_min = ''
    if hour == 1.0:
        plural_hour = ''
    if day == 1.0:
        plural_day = ''

    # Format the string.
    if min == 0.0 and hour == 0.0 and day == 0.0:
        string = "Elapsed time:  %.3f seconds\n" % sec
    elif hour == 0.0 and day == 0.0:
        string = "Elapsed time:  %i minute%s and %.3f seconds\n" % (min, plural_min, sec)
    elif day == 0.0:
        string = "Elapsed time:  %i hour%s, %i minute%s and %.3f seconds\n" % (hour, plural_hour, min, plural_min, sec)
    else:
        string = "Elapsed time:  %i day%s, %i hour%s, %i minute%s and %.3f seconds\n" % (day, plural_day, hour, plural_hour, min, plural_min, sec)

    # Printout.
    if not return_str:
        print(string)

    # Return the string.
    else:
        return string


def print_time():
    """Print the current date and time."""

    # Just print out the output from time.asctime() with spacing.
    print("%s\n" % asctime())
