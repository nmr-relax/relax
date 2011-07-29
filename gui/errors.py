###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module for handling errors in the GUI."""

# Python module imports.
import sys
import wx


def gui_raise(relax_error, raise_flag=True):
    """Handle errors in the GUI to be reported to the user.

    @param relax_error:     The error object.
    @type relax_error:      RelaxError instance
    @keyword raise_flag:    A flag which if True will cause the error to be raised, terminating execution.
    @type raise_flag:       bool
    @raises:                The RelaxError.
    """

    # Show a dialog explaining the error.
    wx.MessageBox(relax_error.text, caption=relax_error.__class__.__name__, style=wx.OK|wx.ICON_ERROR)

    # Throw the error to terminate execution.
    if raise_flag:
        raise relax_error

    # Otherwise, send the text to STDERR.
    else:
        sys.stderr.write(relax_error.__str__())
        sys.stderr.write("\n")
