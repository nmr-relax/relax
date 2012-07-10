###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""The module containing the Memo classes."""


class Memo(object):
    """The multi-processor base class Memo of objects and data.

    This object is used by the slave processor (via a Slave_command) to transfer the calculation results back to the master processor.  This is to be subclassed by the user.
    """

    def memo_id(self):
        """Get the unique ID for the memo.

        Currently this is the objects unique python ID (note these ids can be recycled once the memo
        has been garbage collected it cannot be used as a unique longterm hash).

        @return:    A unique ID for this memo.
        @rtype:     int
        """

        return id(self)
